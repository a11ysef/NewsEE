"""NewsEE staged extraction framework.

Stages (decompose=True):
  1. entity recognition         -> one call per document
  2. trigger detection          -> one call per document
  3. argument role labelling    -> one call per detected event type; each trigger is
                                   given together with the sentence it occurs in, so
                                   repeated trigger words of different events are kept apart
  4. grounding verification     -> rule-based, no LLM call

Switchable modules (for the ablation study):
  decompose   staged calls vs one all-in-one call
  guidelines  type/role definitions + annotation rules vs names only
  demos       "retrieval" (TF-IDF nearest training docs) | "random" | "none"
  k           number of demonstrations
  verify      grounding verification on/off
Setting "gold_trigger" skips stages 1-2 and labels arguments for the gold triggers
(isolates argument extraction from trigger errors).
"""
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass

from . import guidelines as G
from .io_utils import parse_json
from .schema import ENTITY_TYPES, SCHEMA, roles_of
from .scorer import detok, norm

SYSTEM = "You are a precise information extraction system. You only output valid JSON."
_SENT_END = re.compile(r" [.!?] (?=[A-Z`'\"(\[0-9])")


@dataclass
class FrameworkConfig:
    decompose: bool = True
    guidelines: bool = True
    demos: str = "retrieval"  # retrieval | random | none
    k: int = 3
    verify: bool = True
    setting: str = "end2end"  # end2end | gold_trigger
    unseen: tuple = ()  # event types whose examples are hidden from all demonstrations

    def name(self):
        return (f"{'staged' if self.decompose else 'allinone'}_"
                f"{'G' if self.guidelines else 'noG'}_"
                f"{self.demos}{self.k if self.demos != 'none' else ''}_"
                f"{'V' if self.verify else 'noV'}"
                + ("_goldtrig" if self.setting == "gold_trigger" else "")
                + ("_unseen-" + "-".join(sorted(t[:4] for t in self.unseen)) if self.unseen else ""))


# ------------------------------------------------------------------ text helpers
def sentences(text):
    """[(start, end)] character spans of sentences in the (tokenised) MAVEN text."""
    out, start = [], 0
    for m in _SENT_END.finditer(text):
        out.append((start, m.start() + 2))
        start = m.end()
    out.append((start, len(text)))
    return out


def sent_index(spans, offset):
    for i, (a, b) in enumerate(spans):
        if a <= offset < b:
            return i
    return len(spans) - 1


class DocView:
    """Sentence-level view of a document used to place trigger occurrences."""

    def __init__(self, text):
        self.text = text
        self.spans = sentences(text)
        self.sents = [detok(text[a:b]) for a, b in self.spans]
        self.sents_norm = [f" {norm(s)} " for s in self.sents]

    def occurrence_sentences(self, word):
        """Sentence index of each occurrence of word, in reading order."""
        w = norm(word)
        if not w:
            return []
        out = []
        for i, s in enumerate(self.sents_norm):
            out.extend([i] * s.count(f" {w} "))
        return out


def _order(text, spans):
    """Sort spans by their position in text (repeated spans keep successive positions)."""
    t = detok(text)
    pos, last = [], Counter()
    for s in spans:
        s2 = detok(s)
        i = t.find(s2, last[s2])
        last[s2] = (i + 1) if i >= 0 else last[s2]
        pos.append(i if i >= 0 else 10 ** 9)
    return [spans[i] for i in sorted(range(len(spans)), key=lambda i: pos[i])]


def _gold_entities(doc):
    ments = [(m, e["type"]) for e in doc["entities"] for m in e["mentions"]]
    lookup, used, out = defaultdict(list), Counter(), []
    for m, t in ments:
        lookup[m].append(t)
    for m in _order(doc["text"], [m for m, _ in ments]):
        out.append({"text": detok(m), "type": lookup[m][used[m]]})
        used[m] += 1
    return out


def _gold_mentions(doc):
    """[(offset, word, type, event)] for every gold trigger mention, in reading order."""
    out = []
    for e in doc["events"]:
        for w, off in zip(e["triggers"], e.get("offsets") or [[10 ** 9, 0]] * len(e["triggers"])):
            out.append((off[0], w, e["type"], e))
    return sorted(out, key=lambda x: x[0])


def _gold_triggers(doc):
    return [{"trigger": detok(w), "type": t} for _, w, t, _ in _gold_mentions(doc)]


def _first_args(e):
    return {r: [detok(it[0]) for it in items] for r, items in e["arguments"].items()}


def _gold_arg_entries(doc, etype):
    """Argument-stage demonstration: unique (word, sentence) entries with gold arguments."""
    view = DocView(doc["text"])
    entries = {}
    for off, w, t, e in _gold_mentions(doc):
        if t != etype:
            continue
        key = (detok(w), sent_index(view.spans, off))
        cur = entries.setdefault(key, {})
        for r, vs in _first_args(e).items():
            for v in vs:
                if v not in cur.setdefault(r, []):
                    cur[r].append(v)
    return view, entries


def _grounded(span, text_norm):
    s = norm(span)
    return bool(s) and f" {s} " in text_norm


def _occurrences(span, text_norm):
    s = norm(span)
    return text_norm.count(f" {s} ") if s else 0


def _clean_args(args):
    if not isinstance(args, dict):
        return {}
    out = {}
    for r, v in args.items():
        vals = [str(x) for x in (v if isinstance(v, list) else [v])
                if isinstance(x, (str, int, float)) and str(x).strip()]
        if vals:
            out[str(r)] = vals
    return out


# ------------------------------------------------------------------ pipeline
class Framework:
    def __init__(self, llm, cfg, retriever=None):
        self.llm, self.cfg, self.ret = llm, cfg, retriever
        if cfg.demos != "none" and cfg.k > 0 and retriever is None:
            raise ValueError("demonstrations need a retriever")

    # ---- demonstrations
    def _demo_docs(self, text, require_type=None):
        if self.cfg.demos == "none" or self.cfg.k == 0:
            return []
        fn = self.ret.similar if self.cfg.demos == "retrieval" else self.ret.random
        return fn(text, self.cfg.k, require_type=require_type)

    @staticmethod
    def _messages(instruction, demos, text, extra=""):
        """demos: list of (doc_text, extra_input, output_obj)."""
        parts = [instruction]
        for i, (dt, dx, out) in enumerate(demos, 1):
            parts.append(f"### Example {i}\nDocument:\n{detok(dt)}\n{dx}Output:\n{json.dumps(out, ensure_ascii=False)}")
        parts.append(f"### Now the target\nDocument:\n{detok(text)}\n{extra}Output:")
        return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": "\n\n".join(parts)}]

    def _call(self, messages, stage, trace):
        reply = self.llm.chat(messages)
        obj, err = parse_json(reply)
        trace["calls"].append({"stage": stage, "parse_error": err, "reply_chars": len(reply or "")})
        return obj or {}

    # ---- stage 1: entities
    def entities(self, doc, trace):
        instr = ("Extract all entity mentions from the document.\n\n" + G.entity_block(self.cfg.guidelines) +
                 '\n\nReturn JSON: {"entities": [{"text": "<mention copied from the document>", "type": "<entity type>"}]}')
        demos = [(d["text"], "", {"entities": _gold_entities(d)}) for d in self._demo_docs(doc["text"])]
        obj = self._call(self._messages(instr, demos, doc["text"]), "entity", trace)
        return [{"text": str(e.get("text", "")), "type": str(e.get("type", ""))}
                for e in obj.get("entities", []) or [] if isinstance(e, dict)]

    # ---- stage 2: triggers
    def triggers(self, doc, trace):
        instr = ("Find all event triggers of the event types below in the document.\n\n" +
                 G.event_type_block(self.cfg.guidelines) +
                 '\n\nReturn JSON: {"triggers": [{"trigger": "<word copied from the document>", "type": "<event type>"}]}'
                 '\nList one entry per occurrence, in reading order. Return {"triggers": []} if there is none.')
        demos = [(d["text"], "", {"triggers": [t for t in _gold_triggers(d) if t["type"] not in self.cfg.unseen]})
                 for d in self._demo_docs(doc["text"])]
        obj = self._call(self._messages(instr, demos, doc["text"]), "trigger", trace)
        return [{"trigger": str(t.get("trigger", "")), "type": str(t.get("type", ""))}
                for t in obj.get("triggers", []) or [] if isinstance(t, dict)]

    # ---- stage 3: arguments for one event type
    @staticmethod
    def _entry_list(etype, entries, view):
        lines = [f'{i}. "{w}" in the sentence: "{view.sents[s]}"' for i, (w, s) in enumerate(entries, 1)]
        return f"{etype} events to fill:\n" + "\n".join(lines) + "\n"

    def arguments(self, doc, etype, entries, trace):
        """entries: list of (trigger word, sentence index). Returns {entry index: args}."""
        view = DocView(doc["text"])
        instr = ("Extract the arguments of the given events from the document. Each event is identified by "
                 "its trigger and the sentence it occurs in.\n\n" + G.role_block(etype, self.cfg.guidelines) +
                 '\n\nReturn JSON: {"events": [{"id": <number>, "trigger": "<given trigger>", '
                 '"arguments": {"<role>": ["<span copied from the document>"]}}]}'
                 "\nOne entry per given event, same ids and order.")
        demos = []
        for d in ([] if etype in self.cfg.unseen else self._demo_docs(doc["text"], require_type=etype)):
            dview, gold = _gold_arg_entries(d, etype)
            keys = list(gold)[:6]
            demos.append((d["text"], self._entry_list(etype, keys, dview),
                          {"events": [{"id": i, "trigger": w, "arguments": gold[(w, s)]}
                                      for i, (w, s) in enumerate(keys, 1)]}))
        obj = self._call(self._messages(instr, demos, doc["text"], self._entry_list(etype, entries, view)),
                         f"argument:{etype}", trace)
        out = {}
        evs = [e for e in obj.get("events", []) or [] if isinstance(e, dict)]
        for pos, ev in enumerate(evs):
            try:
                idx = int(ev.get("id")) - 1
            except (TypeError, ValueError):
                idx = pos
            if 0 <= idx < len(entries):
                out[idx] = _clean_args(ev.get("arguments"))
        return out

    # ---- all-in-one variant (decompose=False)
    def all_in_one(self, doc, trace):
        role_lines = "\n\n".join(G.role_block(t, self.cfg.guidelines) for t in SCHEMA) if self.cfg.guidelines \
            else "\n".join(f"- {t}: roles = {', '.join(roles_of(t))}" for t in SCHEMA)
        instr = ("Extract entities, events and event arguments from the document.\n\n" +
                 G.entity_block(self.cfg.guidelines) + "\n\n" + G.event_type_block(self.cfg.guidelines) +
                 "\n\nArgument roles:\n" + role_lines +
                 '\n\nReturn JSON: {"entities": [{"text": "...", "type": "..."}], '
                 '"events": [{"trigger": "...", "type": "...", "arguments": {"<role>": ["..."]}}]}'
                 "\nOne event entry per trigger occurrence, in reading order.")
        demos = []
        for d in self._demo_docs(doc["text"]):
            evs = [{"trigger": detok(w), "type": t, "arguments": _first_args(e)}
                   for _, w, t, e in _gold_mentions(d) if t not in self.cfg.unseen]
            demos.append((d["text"], "", {"entities": _gold_entities(d), "events": evs}))
        obj = self._call(self._messages(instr, demos, doc["text"]), "all_in_one", trace)
        ents = [{"text": str(e.get("text", "")), "type": str(e.get("type", ""))}
                for e in obj.get("entities", []) or [] if isinstance(e, dict)]
        evs = [{"trigger": str(e.get("trigger", "")), "type": str(e.get("type", "")),
                "arguments": _clean_args(e.get("arguments"))}
               for e in obj.get("events", []) or [] if isinstance(e, dict)]
        return ents, evs

    # ---- stage 4: grounding verification
    def verify(self, doc, ents, evs, trace):
        tn = f" {norm(doc['text'])} "
        removed = Counter()
        out_e, seen_e = [], Counter()
        for e in ents:
            key = (norm(e["text"]), e["type"])
            if e["type"] not in ENTITY_TYPES:
                removed["entity_bad_type"] += 1
            elif not _grounded(e["text"], tn):
                removed["entity_not_in_text"] += 1
            elif seen_e[key] >= _occurrences(e["text"], tn):
                removed["entity_duplicate"] += 1
            else:
                seen_e[key] += 1
                out_e.append(e)
        out_v, seen_t = [], Counter()
        for ev in evs:
            key = (norm(ev["trigger"]), ev["type"])
            if ev["type"] not in SCHEMA:
                removed["event_bad_type"] += 1
                continue
            if not _grounded(ev["trigger"], tn):
                removed["trigger_not_in_text"] += 1
                continue
            if seen_t[key] >= _occurrences(ev["trigger"], tn):
                removed["trigger_duplicate"] += 1
                continue
            seen_t[key] += 1
            args = {}
            for r, vals in ev["arguments"].items():
                if r not in SCHEMA[ev["type"]]["roles"]:
                    removed["argument_bad_role"] += len(vals)
                    continue
                keep = [v for v in vals if _grounded(v, tn)]
                removed["argument_not_in_text"] += len(vals) - len(keep)
                if keep:
                    args[r] = keep
            out_v.append({**ev, "arguments": args})
        trace["removed"] = dict(removed)
        return out_e, out_v

    # ---- argument stage over a list of (word, type, sentence, payload) mentions
    def _fill_arguments(self, doc, mentions, trace):
        """mentions: list of dicts with trigger, type, sent. Adds 'arguments' in place."""
        by_type = defaultdict(list)  # type -> unique (word, sent)
        for m in mentions:
            key = (m["trigger"], m["sent"])
            if m["type"] in SCHEMA and m["trigger"] and key not in by_type[m["type"]]:
                by_type[m["type"]].append(key)
        results = {et: self.arguments(doc, et, entries, trace) for et, entries in by_type.items()}
        for m in mentions:
            et = m["type"]
            if et in results:
                idx = by_type[et].index((m["trigger"], m["sent"])) if (m["trigger"], m["sent"]) in by_type[et] else -1
                m["arguments"] = results[et].get(idx, {})
            else:
                m["arguments"] = {}

    # ---- full run
    def run(self, doc):
        trace = {"config": asdict(self.cfg), "calls": []}
        view = DocView(doc["text"])
        if self.cfg.setting == "gold_trigger":
            ents = []
            mentions = [{"trigger": detok(w), "type": t, "sent": sent_index(view.spans, off), "gold_event_id": e["id"]}
                        for off, w, t, e in _gold_mentions(doc)]
            self._fill_arguments(doc, mentions, trace)
            evs = [{"trigger": m["trigger"], "type": m["type"], "arguments": m["arguments"],
                    "gold_event_id": m["gold_event_id"]} for m in mentions]
        elif self.cfg.decompose:
            ents = self.entities(doc, trace)
            trigs = self.triggers(doc, trace)
            seen = Counter()
            mentions = []
            for t in trigs:  # place the n-th listed occurrence of a word in the n-th sentence containing it
                occ = view.occurrence_sentences(t["trigger"])
                n = seen[norm(t["trigger"])]
                seen[norm(t["trigger"])] += 1
                sent = occ[min(n, len(occ) - 1)] if occ else -1
                mentions.append({"trigger": t["trigger"], "type": t["type"], "sent": sent})
            self._fill_arguments(doc, [m for m in mentions if m["sent"] >= 0], trace)
            evs = [{"trigger": m["trigger"], "type": m["type"], "arguments": m.get("arguments", {})}
                   for m in mentions]
        else:
            ents, evs = self.all_in_one(doc, trace)

        if self.cfg.verify:
            ents, evs = self.verify(doc, ents, evs, trace)
        return {"id": doc["id"], "entities": ents, "events": evs}, trace
