"""Automatic error analysis (RQ4) for one framework run, plus a sample for manual checking.

  python scripts/error_analysis.py --model ds-flash            # test split, final framework run
  python scripts/error_analysis.py --model glm-air --sample 100

Trigger errors
  type confusion   the word is a gold trigger, but of another event type (gold -> predicted pairs)
  spurious         the word is not a gold trigger at all (over-generation)
  missed           a gold trigger occurrence nobody predicted
    of which repeated-mention misses: another mention of the same gold event WAS found
Argument errors (for predicted events aligned to a gold event of the same type)
  boundary         overlaps a gold argument of the same role but is not an exact match
  wrong role       exactly matches a gold argument of the event, under another role
  spurious         matches nothing in the event
  missed           a gold argument with no prediction
  from wrong event arguments attached to a predicted event that matches no gold event
Hallucinations (spans not in the document) come from the verification module's counts.

Writes results/errors_<model>_<split>.md and errors_<model>_<split>_sample.csv
(the CSV has an empty `manual_check` column to fill in by hand).
"""
import argparse
import csv
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee import config  # noqa: E402
from newsee.framework import DocView  # noqa: E402
from newsee.io_utils import read_jsonl  # noqa: E402
from newsee.scorer import _align, bow_f1, norm  # noqa: E402

from newsee.framework import FINAL  # noqa: E402
from newsee.schema import EVENT_TYPES  # noqa: E402


def spurious_breakdown(golds, preds):
    """Why is a 'spurious' trigger spurious? Looks the word up in the FULL MAVEN-Arg annotation
    (all 162 types): annotated with a type outside our 12 (schema boundary), explicitly marked as
    a non-event by the annotators (negative trigger), or not mentioned at all."""
    src = config.MAVEN_DIR / "valid.jsonl"
    if not src.exists():
        return None, None
    ids = {g["id"] for g in golds}
    full = {}
    with open(src) as f:
        for line in f:
            d = json.loads(line)
            if d["id"] in ids:
                full[d["id"]] = d
    pmap = {p["id"]: p for p in preds}
    cats, pairs = Counter(), Counter()
    for g in golds:
        f, p = full.get(g["id"]), pmap.get(g["id"], {"events": []})
        if f is None:
            continue
        gw = Counter(norm(t) for e in g["events"] for t in e["triggers"])
        other = defaultdict(Counter)
        for e in f["events"]:
            if e["type"] not in EVENT_TYPES:
                for m in e["mention"]:
                    other[norm(m["trigger_word"])][e["type"]] += 1
        neg = {norm(x["trigger_word"]) for x in f.get("negative_triggers", [])}
        pw = Counter((norm(e["trigger"]), e["type"]) for e in p["events"])
        left = Counter(gw)
        for (w, t), c in pw.items():
            take = min(c, left[w])
            left[w] -= take
            extra = c - take
            if extra <= 0:
                continue
            if other.get(w):
                top = max(other[w], key=other[w].get)
                cats["annotated as an event type outside the 12"] += extra
                pairs[(t, top)] += extra
            elif w in neg:
                cats["listed by MAVEN as a non-trigger candidate (negative instance)"] += extra
            else:
                cats["not annotated at all"] += extra
    return cats, pairs


def sentence_of(view, span):
    s = norm(span)
    for sent, sn in zip(view.sents, view.sents_norm):
        if s and f" {s} " in sn:
            return sent
    return ""


def analyse(golds, preds):
    pmap = {p["id"]: p for p in preds}
    trig, arg = Counter(), Counter()
    confusion = Counter()
    examples = defaultdict(list)
    for g in golds:
        p = pmap.get(g["id"], {"events": []})
        view = DocView(g["text"])
        # ---------------- triggers (multiset per word)
        gold_by_word = defaultdict(Counter)  # word -> Counter(type)
        for e in g["events"]:
            for t in e["triggers"]:
                gold_by_word[norm(t)][e["type"]] += 1
        pred_by_word = defaultdict(Counter)
        for e in p["events"]:
            pred_by_word[norm(e["trigger"])][e["type"]] += 1
        for w in set(gold_by_word) | set(pred_by_word):
            gw, pw = gold_by_word.get(w, Counter()), pred_by_word.get(w, Counter())
            correct = gw & pw
            trig["correct"] += sum(correct.values())
            g_left, p_left = gw - correct, pw - correct
            # same word, other type = confusion
            gl, pl = list(g_left.elements()), list(p_left.elements())
            n_conf = min(len(gl), len(pl))
            for gt, pt in zip(gl[:n_conf], pl[:n_conf]):
                trig["type confusion"] += 1
                confusion[(gt, pt)] += 1
                examples["trigger: type confusion"].append((g["id"], f"{w} [{gt}]", f"{w} [{pt}]", sentence_of(view, w)))
            for gt in gl[n_conf:]:
                trig["missed"] += 1
                examples["trigger: missed"].append((g["id"], f"{w} [{gt}]", "", sentence_of(view, w)))
            for pt in pl[n_conf:]:
                trig["spurious"] += 1
                examples["trigger: spurious"].append((g["id"], "", f"{w} [{pt}]", sentence_of(view, w)))
        # repeated-mention misses: event found through one mention, other mentions missed
        found = {norm(e["trigger"]) for e in p["events"]}
        for e in g["events"]:
            words = [norm(t) for t in e["triggers"]]
            if len(words) > 1 and any(w in found for w in words):
                trig["missed (other mention of a found event)"] += sum(1 for w in words if w not in found)
        # ---------------- arguments
        align = _align(g, p, use_type=True)
        merged = defaultdict(lambda: defaultdict(list))
        for pe, gi in zip(p["events"], align):
            for role, vals in pe.get("arguments", {}).items():
                for v in vals:
                    if gi is None:
                        arg["from wrong event"] += 1
                    elif norm(v) not in {norm(x) for x in merged[gi][role]}:
                        merged[gi][role].append(v)
        for gi, ge in enumerate(g["events"]):
            golds_r = {r: [list(acc) for acc in items] for r, items in ge["arguments"].items()}
            preds_r = merged.get(gi, {})
            used = set()
            for role, vals in preds_r.items():
                for v in vals:
                    nv = norm(v)
                    exact = [(r, i) for r, items in golds_r.items() for i, acc in enumerate(items)
                             if nv in {norm(a) for a in acc} and (r, i) not in used]
                    same_role = [x for x in exact if x[0] == role]
                    if same_role:
                        used.add(same_role[0]); arg["correct"] += 1
                        continue
                    overl = [(r, i) for r, items in golds_r.items() for i, acc in enumerate(items)
                             if r == role and (r, i) not in used and max(bow_f1(a, v) for a in acc) > 0]
                    if overl:
                        used.add(overl[0]); arg["boundary"] += 1
                        gold_txt = golds_r[overl[0][0]][overl[0][1]][0]
                        examples["argument: boundary"].append((g["id"], f"{role}: {gold_txt}", f"{role}: {v}", sentence_of(view, gold_txt)))
                    elif exact:
                        used.add(exact[0]); arg["wrong role"] += 1
                        examples["argument: wrong role"].append((g["id"], f"{exact[0][0]}: {v}", f"{role}: {v}", sentence_of(view, v)))
                    else:
                        arg["spurious"] += 1
                        examples["argument: spurious"].append((g["id"], "", f"{ge['type']}.{role}: {v}", sentence_of(view, v)))
            if gi in merged:
                for r, items in golds_r.items():
                    for i, acc in enumerate(items):
                        if (r, i) not in used:
                            arg["missed (event found)"] += 1
                            examples["argument: missed"].append((g["id"], f"{ge['type']}.{r}: {acc[0]}", "", sentence_of(view, acc[0])))
            else:
                arg["missed (event not found)"] += sum(len(items) for items in golds_r.values())
    return trig, arg, confusion, examples


def pct(c):
    tot = sum(c.values()) or 1
    return [(k, v, round(100 * v / tot, 1)) for k, v in c.most_common()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=list(config.MODELS))
    ap.add_argument("--split", default="test", choices=["dev", "test"])
    ap.add_argument("--run", help="run directory (default: final framework run of this model)")
    ap.add_argument("--sample", type=int, default=100)
    a = ap.parse_args()
    run = Path(a.run) if a.run else config.RUNS_DIR / f"{FINAL.name()}_{a.model}_{a.split}"
    golds = read_jsonl(config.DATA_DIR / f"{a.split}.jsonl")
    preds = read_jsonl(run / "predictions.jsonl")
    trig, arg, confusion, examples = analyse(golds, preds)
    removed = json.loads((run / "run.json").read_text()).get("verification_removed", {})

    lines = [f"# Error analysis: {a.model} on {a.split} ({run.name})", "",
             "## Triggers", "", "| category | count | share of all trigger decisions (%) |", "|---|---|---|"]
    trig_main = Counter({k: v for k, v in trig.items() if not k.startswith("missed (")})
    lines += [f"| {k} | {v} | {p} |" for k, v, p in pct(trig_main)]
    lines += ["", f"Of the missed triggers, {trig['missed (other mention of a found event)']} are further mentions "
              "of an event whose other mention was found.", "",
              "Most frequent type confusions (gold -> predicted):", "", "| gold | predicted | count |", "|---|---|---|"]
    lines += [f"| {g} | {p} | {c} |" for (g, p), c in confusion.most_common(10)]
    cats, pairs = spurious_breakdown(golds, preds)
    if cats:
        lines += ["", "Why the spurious triggers are spurious (full MAVEN-Arg annotation):", "",
                  "| reason | count | share (%) |", "|---|---|---|"]
        lines += [f"| {k} | {v} | {p} |" for k, v, p in pct(cats)]
        lines += ["", "Schema-boundary pairs (predicted type -> annotated type outside the 12):", "",
                  "| predicted | annotated | count |", "|---|---|---|"]
        lines += [f"| {a_} | {b_} | {c} |" for (a_, b_), c in pairs.most_common(10)]
    lines += ["", "## Arguments", "", "| category | count | share (%) |", "|---|---|---|"]
    lines += [f"| {k} | {v} | {p} |" for k, v, p in pct(arg)]
    lines += ["", "## Hallucinations removed by verification", "", "| item | count |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in sorted(removed.items(), key=lambda x: -x[1])]

    out = config.ROOT / "results"
    out.mkdir(exist_ok=True)
    stem = out / f"errors_{a.model}_{a.split}"
    Path(f"{stem}.md").write_text("\n".join(lines) + "\n")
    # stratified sample for manual checking
    rng = random.Random(42)
    cats = [c for c in examples if examples[c]]
    per = max(1, a.sample // max(1, len(cats)))
    rows = []
    for c in cats:
        for ex in rng.sample(examples[c], min(per, len(examples[c]))):
            rows.append({"category": c, "doc_id": ex[0], "gold": ex[1], "predicted": ex[2],
                         "sentence": ex[3], "manual_check": "", "note": ""})
    with open(f"{stem}_sample.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("\n".join(lines))
    print(f"\nsaved {stem}.md and {stem}_sample.csv ({len(rows)} rows for manual checking)")


if __name__ == "__main__":
    main()
