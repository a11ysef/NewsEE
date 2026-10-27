"""Scoring for the three NewsEE sub-tasks.

Predictions are text-based (LLMs output strings, not offsets). One line per document:
  {"id": doc_id,
   "entities": [{"text": str, "type": str}],
   "events":   [{"trigger": str, "type": str,
                 "arguments": {role: [str, ...]},
                 "gold_event_id": optional, used in the gold-trigger setting}]}

Metrics
  Entity-I / Entity-C : set of mention strings (+ type), exact match after normalisation
  Trig-I / Trig-C     : multiset of trigger strings (+ event type)
  Arg-I / Arg-C       : event-level argument scoring as in MAVEN-Arg. Each predicted
                        event is aligned to a gold event through its trigger (and type
                        for Arg-C); predicted events aligned to the same gold event are
                        merged (coreferent mentions). Arguments are matched one-to-one.
                        Reported twice: EM (strict) and BoW token-F1 (relaxed), following
                        the official MAVEN-Arg evaluation.
"""
import re
import string
from collections import Counter, defaultdict

_PUNC = set(string.punctuation) | {"“", "”", "’", "‘", "–", "—"}


def detok(s):
    """Undo MAVEN's PTB-style tokenisation so 'Martin 's' == "Martin's"."""
    s = s.replace("``", '"').replace("''", '"')
    s = re.sub(r" (['’](s|re|ve|ll|d|m)|n['’]t)\b", r"\1", s)
    s = re.sub(r" ([,.;:!?%)\]])", r"\1", s)
    s = re.sub(r"([(\[$]) ", r"\1", s)
    return s


def norm(s):
    s = detok(str(s)).lower()
    s = "".join(ch for ch in s if ch not in _PUNC)
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())


def bow_f1(gold, pred):
    g, p = norm(gold).split(), norm(pred).split()
    common = Counter(g) & Counter(p)
    same = sum(common.values())
    if not g or not p or same == 0:
        return 0.0
    pr, rc = same / len(p), same / len(g)
    return 2 * pr * rc / (pr + rc)


def prf(correct, n_pred, n_gold):
    p = correct / n_pred if n_pred else 0.0
    r = correct / n_gold if n_gold else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return {"P": round(100 * p, 2), "R": round(100 * r, 2), "F1": round(100 * f, 2)}


# ---------------------------------------------------------------- entities / triggers
def _entity_counts(gold, pred):
    gi = {norm(m) for e in gold["entities"] for m in e["mentions"]}
    gc = {(norm(m), e["type"]) for e in gold["entities"] for m in e["mentions"]}
    pi = {norm(e.get("text", "")) for e in pred.get("entities", [])} - {""}
    pc = {(norm(e.get("text", "")), e.get("type")) for e in pred.get("entities", [])
          if norm(e.get("text", ""))}
    return (len(gi & pi), len(pi), len(gi)), (len(gc & pc), len(pc), len(gc))


def _trigger_counts(gold, pred):
    gi = Counter(norm(t) for e in gold["events"] for t in e["triggers"])
    gc = Counter((norm(t), e["type"]) for e in gold["events"] for t in e["triggers"])
    pevs = [e for e in pred.get("events", []) if norm(e.get("trigger", ""))]
    pi = Counter(norm(e["trigger"]) for e in pevs)
    pc = Counter((norm(e["trigger"]), e.get("type")) for e in pevs)
    return ((sum((gi & pi).values()), sum(pi.values()), sum(gi.values())),
            (sum((gc & pc).values()), sum(pc.values()), sum(gc.values())))


# ---------------------------------------------------------------- arguments
def _align(gold, pred, use_type):
    """Map each predicted event to a gold event index (or None)."""
    gidx = {e["id"]: i for i, e in enumerate(gold["events"])}
    used = Counter()
    out = []
    for p in pred.get("events", []):
        if p.get("gold_event_id") in gidx:
            out.append(gidx[p["gold_event_id"]])
            continue
        t = norm(p.get("trigger", ""))
        cands = [i for i, g in enumerate(gold["events"])
                 if t and t in {norm(x) for x in g["triggers"]}
                 and (not use_type or g["type"] == p.get("type"))]
        if not cands:
            out.append(None)
            continue
        # Same trigger word may belong to several gold events: prefer the one whose
        # arguments overlap most with the prediction, then one not yet taken.
        pvals = {norm(v) for vs in (p.get("arguments") or {}).values()
                 for v in (vs if isinstance(vs, list) else [vs])} - {""}
        def overlap(i):
            gvals = {norm(a) for items in gold["events"][i]["arguments"].values()
                     for acc in items for a in acc}
            return len(pvals & gvals)
        cands.sort(key=lambda i: (-overlap(i), used[i]))
        out.append(cands[0])
        used[cands[0]] += 1
    return out


def _match(gold_items, pred_strs, soft):
    """One-to-one greedy matching. gold_items: list of acceptable-string lists."""
    pairs = []
    for gi, acc in enumerate(gold_items):
        for pi, s in enumerate(pred_strs):
            sc = max(bow_f1(a, s) for a in acc) if soft else float(norm(s) in {norm(a) for a in acc})
            if sc > 0:
                pairs.append((sc, gi, pi))
    pairs.sort(reverse=True)
    ug, up, total = set(), set(), 0.0
    for sc, gi, pi in pairs:
        if gi not in ug and pi not in up:
            ug.add(gi); up.add(pi); total += sc
    return total


def _arg_counts(gold, pred, use_type, use_role, soft):
    align = _align(gold, pred, use_type)
    merged = defaultdict(lambda: defaultdict(list))  # gold idx -> role -> [pred strings]
    seen = defaultdict(set)  # gold idx -> {(role, normalised value)}; dedups coreferent mentions
    n_pred = 0
    for p, gi in zip(pred.get("events", []), align):
        for role, vals in (p.get("arguments") or {}).items():
            vals = [v for v in (vals if isinstance(vals, list) else [vals]) if norm(v)]
            if gi is None:
                n_pred += len(vals)
                continue
            key = role if use_role else "*"
            for v in vals:
                if (role, norm(v)) not in seen[gi]:
                    seen[gi].add((role, norm(v)))
                    merged[gi][key].append(v)
    n_pred += sum(len(v) for r in merged.values() for v in r.values())
    n_gold, correct = 0, 0.0
    for gi, g in enumerate(gold["events"]):
        groups = defaultdict(list)
        for role, items in g["arguments"].items():
            groups[role if use_role else "*"].extend(items)
        n_gold += sum(len(v) for v in groups.values())
        for key, items in groups.items():
            correct += _match(items, merged[gi].get(key, []), soft)
    return correct, n_pred, n_gold


# ---------------------------------------------------------------- public API
def score(golds, preds):
    """golds/preds: lists of document dicts. Missing predictions count as empty."""
    pmap = {p["id"]: p for p in preds}
    acc = defaultdict(lambda: [0.0, 0, 0])

    def add(name, c):
        for i in range(3):
            acc[name][i] += c[i]

    for g in golds:
        p = pmap.get(g["id"], {"id": g["id"], "entities": [], "events": []})
        ei, ec = _entity_counts(g, p)
        add("Entity-I", ei); add("Entity-C", ec)
        ti, tc = _trigger_counts(g, p)
        add("Trig-I", ti); add("Trig-C", tc)
        add("Arg-I (EM)", _arg_counts(g, p, use_type=False, use_role=False, soft=False))
        add("Arg-C (EM)", _arg_counts(g, p, use_type=True, use_role=True, soft=False))
        add("Arg-I (BoW)", _arg_counts(g, p, use_type=False, use_role=False, soft=True))
        add("Arg-C (BoW)", _arg_counts(g, p, use_type=True, use_role=True, soft=True))
    res = {k: prf(*v) for k, v in acc.items()}
    res["_coverage"] = {"docs_gold": len(golds), "docs_predicted": sum(g["id"] in pmap for g in golds)}
    return res


def format_table(res):
    lines = [f"{'metric':14s} {'P':>7s} {'R':>7s} {'F1':>7s}"]
    for k, v in res.items():
        if not k.startswith("_"):
            lines.append(f"{k:14s} {v['P']:7.2f} {v['R']:7.2f} {v['F1']:7.2f}")
    return "\n".join(lines)


def _restrict(doc, etype):
    return {**doc, "events": [e for e in doc.get("events", []) if e.get("type") == etype]}


def score_by_type(golds, preds, types):
    """Trig-C and Arg-C (EM / BoW) F1 for each event type separately.

    Predictions of one type are scored against gold events of that type only, so a
    trigger predicted with the wrong type counts as a miss for the gold type and a
    false positive for the predicted type.
    """
    pmap = {p["id"]: p for p in preds}
    out = {}
    for t in types:
        acc = {"Trig-C": [0, 0, 0], "Arg-C (EM)": [0.0, 0, 0], "Arg-C (BoW)": [0.0, 0, 0]}
        for g in golds:
            p = pmap.get(g["id"], {"id": g["id"], "entities": [], "events": []})
            gt, pt = _restrict(g, t), _restrict(p, t)
            _, tc = _trigger_counts(gt, pt)
            for k, c in (("Trig-C", tc),
                         ("Arg-C (EM)", _arg_counts(gt, pt, True, True, False)),
                         ("Arg-C (BoW)", _arg_counts(gt, pt, True, True, True))):
                for i in range(3):
                    acc[k][i] += c[i]
        out[t] = {k: prf(*v)["F1"] for k, v in acc.items()}
        out[t]["n_gold_triggers"] = acc["Trig-C"][2]
    return out
