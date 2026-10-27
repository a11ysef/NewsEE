"""Dictionary + LLM combination (no API calls; uses saved framework outputs).

  python scripts/run_hybrid.py --split dev
  python scripts/run_hybrid.py --split test

The rule was fixed before it was run on any data:
  * a word in the dictionary (rate >= 50%, see run_lexicon.py) is labelled by the dictionary:
    every occurrence becomes a trigger with the dictionary's event type;
  * every other word is left to the LLM framework: its triggers on such words are kept;
  * arguments: a dictionary trigger takes the arguments of the framework event with the same word
    and the same type (n-th occurrence to n-th event); otherwise it has none;
  * entities: taken from the framework unchanged.
So the dictionary decides the words it has seen and trusts, and the LLM decides everything else,
including ambiguous words such as "fire" that the dictionary leaves out.
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from newsee import config  # noqa: E402
from newsee.io_utils import read_jsonl, write_jsonl  # noqa: E402
from newsee.scorer import norm, score  # noqa: E402
from newsee.stats import paired_bootstrap  # noqa: E402
from run_lexicon import build  # noqa: E402

MODELS = ["ds-flash", "glm-4.7", "ds-pro", "glm-air"]
MIN_RATE = 0.5
METRICS = ["Entity-C", "Trig-I", "Trig-C", "Arg-C (EM)", "Arg-C (BoW)"]


def combine(doc, fw, lexicon):
    t = f" {norm(doc['text'])} "
    by_word = defaultdict(list)
    for e in fw["events"]:
        by_word[norm(e.get("trigger", ""))].append(e)
    events = []
    for w, typ in lexicon.items():
        for _ in range(t.count(f" {w} ")):
            match = next((e for e in by_word.get(w, []) if e.get("type") == typ), None)
            if match is not None:
                by_word[w].remove(match)
            events.append({"trigger": w, "type": typ, "arguments": match["arguments"] if match else {}})
    events += [e for e in fw["events"] if norm(e.get("trigger", "")) not in lexicon]
    return {"id": doc["id"], "entities": fw["entities"], "events": events}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test", choices=["dev", "test"])
    a = ap.parse_args()
    gold = read_jsonl(config.DATA_DIR / f"{a.split}.jsonl")
    trig_lex, _ = build(read_jsonl(config.DATA_DIR / "pool.jsonl"))
    lexicon = {w: typ for w, (typ, r) in trig_lex.items() if r >= MIN_RATE}
    lex_preds = read_jsonl(config.RUNS_DIR / f"lexicon_rate50_{a.split}" / "predictions.jsonl")
    lines = [f"# Dictionary + LLM combination ({a.split}, {len(gold)} documents)", "",
             f"Dictionary: {len(lexicon)} trigger words with annotation rate >= 50% in the training texts.", "",
             "| model | system | " + " | ".join(METRICS) + " | Trig-C P | Trig-C R |",
             "|---|---|" + "---|" * (len(METRICS) + 2)]
    tests = ["", "## Paired bootstrap, 1000 samples", "",
             "| model | comparison | metric | A | B | B - A | 95% CI | significant |", "|---|---|---|---|---|---|---|---|"]
    out = {"split": a.split, "n_docs": len(gold), "dictionary_words": len(lexicon), "rows": {}, "bootstrap": {}}
    r_lex = score(gold, lex_preds)
    for m in MODELS:
        fw_dir = config.RUNS_DIR / f"staged_G_retrieval3_V_{m}_{a.split}"
        if not (fw_dir / "predictions.jsonl").exists():
            continue
        fw = {p["id"]: p for p in read_jsonl(fw_dir / "predictions.jsonl")}
        empty = {"entities": [], "events": []}
        hyb = [combine(d, fw.get(d["id"], {"id": d["id"], **empty}), lexicon) for d in gold]
        run = config.RUNS_DIR / f"hybrid_lexicon50_{m}_{a.split}"
        run.mkdir(parents=True, exist_ok=True)
        write_jsonl(hyb, run / "predictions.jsonl")
        r_h, r_f = score(gold, hyb), score(gold, list(fw.values()))
        (run / "metrics.json").write_text(json.dumps(r_h, indent=2))
        (run / "run.json").write_text(json.dumps({"method": "hybrid", "dictionary": "lexicon_rate50",
                                                  "framework_run": fw_dir.name, "split": a.split,
                                                  "n_docs": len(gold), "llm_calls": 0}, indent=2))
        out["rows"][m] = {"dictionary": r_lex, "framework": r_f, "hybrid": r_h}
        for label, r in (("dictionary", r_lex), ("framework", r_f), ("dictionary + framework", r_h)):
            lines.append(f"| {m} | {label} | " + " | ".join(f"{r[k]['F1']:.1f}" for k in METRICS) +
                         f" | {r['Trig-C']['P']:.1f} | {r['Trig-C']['R']:.1f} |")
        out["bootstrap"][m] = {}
        for name, base in (("vs framework", list(fw.values())), ("vs dictionary", lex_preds)):
            bs = paired_bootstrap(gold, base, hyb, metrics=METRICS)
            out["bootstrap"][m][name] = bs
            for k, v in bs.items():
                if name == "vs dictionary" and k.startswith("Arg"):
                    continue
                tests.append(f"| {m} | hybrid {name} | {k} | {v['A']:.1f} | {v['B']:.1f} | {v['diff']:+.1f} | "
                             f"[{v['lo']:+.1f}, {v['hi']:+.1f}] | {'yes' if v['significant'] else 'no'} |")
    lines += tests

    # where the framework's trigger predictions are right: by what the training data says about the word
    lines += ["", "## Precision of the framework's triggers, by what the training data says about the word", "",
              "Groups: in dictionary = annotated in >= 50% of its training occurrences; ambiguous = annotated as a "
              "trigger in training but in < 50% of occurrences; never a trigger = never annotated as a trigger.", "",
              "| model | in dictionary: correct / predicted (P) | ambiguous | never a trigger in training |",
              "|---|---|---|---|"]
    out["precision_by_group"] = {}
    gmap = {d["id"]: d for d in gold}
    for m in out["rows"]:
        hit, tot = defaultdict(int), defaultdict(int)
        for p in read_jsonl(config.RUNS_DIR / f"staged_G_retrieval3_V_{m}_{a.split}" / "predictions.jsonl"):
            g = gmap.get(p["id"])
            if g is None:
                continue
            gc = Counter((norm(t), e["type"]) for e in g["events"] for t in e["triggers"])
            pc = Counter((norm(e["trigger"]), e.get("type")) for e in p["events"] if norm(e.get("trigger", "")))
            for k, v in pc.items():
                grp = "dict" if k[0] in lexicon else ("ambiguous" if k[0] in trig_lex else "never")
                tot[grp] += v
                hit[grp] += min(v, gc[k])
        out["precision_by_group"][m] = {k: [hit[k], tot[k]] for k in tot}
        cell = lambda k: f"{hit[k]} / {tot[k]} ({100 * hit[k] / tot[k]:.1f})" if tot[k] else "-"  # noqa: E731
        lines.append(f"| {m} | {cell('dict')} | {cell('ambiguous')} | {cell('never')} |")
    res = config.ROOT / "results"
    (res / f"hybrid_{a.split}.md").write_text("\n".join(lines) + "\n")
    (res / f"hybrid_{a.split}.json").write_text(json.dumps(out, indent=2))
    print("\n".join(lines))
    print(f"\nsaved results/hybrid_{a.split}.md / .json")


if __name__ == "__main__":
    main()
