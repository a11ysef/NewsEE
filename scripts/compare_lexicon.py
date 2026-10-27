"""Dictionary baseline versus the LLM framework (no API calls; run run_lexicon.py first).

  python scripts/compare_lexicon.py --split test

Outputs results/lexicon_<split>.md and .json:
  1. overall scores: dictionary, zero-shot LLM baseline and framework for every model
  2. paired bootstrap: framework minus dictionary (lexicon_rate50)
  3. Trig-C per event type
  4. trigger recall split by whether the gold trigger word is an entry of the dictionary
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee import config  # noqa: E402
from newsee.io_utils import read_jsonl  # noqa: E402
from newsee.schema import EVENT_TYPES  # noqa: E402
from newsee.scorer import norm, score, score_by_type  # noqa: E402
from newsee.stats import paired_bootstrap  # noqa: E402

MODELS = ["ds-flash", "glm-4.7", "ds-pro", "glm-air"]
LEX = "lexicon_rate50"
METRICS = ["Entity-C", "Trig-I", "Trig-C", "Arg-C (EM)"]


def preds(run):
    return read_jsonl(config.RUNS_DIR / run / "predictions.jsonl")


def recall_split(gold, pred, vocab):
    """Trig-C recall on gold mentions whose word is / is not a dictionary entry."""
    pm = {p["id"]: p for p in pred}
    hit, tot = Counter(), Counter()
    for g in gold:
        gc = Counter((norm(t), e["type"]) for e in g["events"] for t in e["triggers"])
        p = pm.get(g["id"], {"events": []})
        pc = Counter((norm(e.get("trigger", "")), e.get("type")) for e in p["events"])
        for k, n in gc.items():
            grp = "in dictionary" if k[0] in vocab else "not in dictionary"
            tot[grp] += n
            hit[grp] += min(n, pc[k])
    return {k: (hit[k], tot[k], round(100 * hit[k] / tot[k], 1) if tot[k] else 0.0) for k in tot}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test", choices=["dev", "test"])
    a = ap.parse_args()
    gold = read_jsonl(config.DATA_DIR / f"{a.split}.jsonl")
    lex = preds(f"{LEX}_{a.split}")
    vocab = {norm(e["trigger"]) for p in lex for e in p["events"]}
    # dictionary entries that could fire: every word of the rate-50 dictionary that occurs in the split
    runs = {"Dictionary (all entries)": f"lexicon_all_{a.split}", "Dictionary (rate >= 50%)": f"{LEX}_{a.split}"}
    for m in MODELS:
        runs[f"{m} zero-shot"] = f"baseline_zs_{m}_{a.split}"
        runs[f"{m} framework"] = f"staged_G_retrieval3_V_{m}_{a.split}"
    runs = {k: v for k, v in runs.items() if (config.RUNS_DIR / v / "predictions.jsonl").exists()}
    out = {"split": a.split, "n_docs": len(gold), "overall": {}, "bootstrap": {}, "per_type": {}, "recall_split": {}}
    lines = [f"# Dictionary baseline versus LLM framework ({a.split}, {len(gold)} documents)", "",
             "## Overall (F1)", "", "| system | " + " | ".join(METRICS) + " | Trig-C P | Trig-C R |",
             "|---|" + "---|" * (len(METRICS) + 2)]
    for label, run in runs.items():
        r = score(gold, preds(run))
        out["overall"][label] = r
        lines.append(f"| {label} | " + " | ".join(f"{r[m]['F1']:.1f}" for m in METRICS) +
                     f" | {r['Trig-C']['P']:.1f} | {r['Trig-C']['R']:.1f} |")

    lines += ["", f"## Framework minus dictionary (rate >= 50%), paired bootstrap, 1000 samples", "",
              "| model | metric | dictionary | framework | difference | 95% CI | significant |",
              "|---|---|---|---|---|---|---|"]
    for m in MODELS:
        run = f"staged_G_retrieval3_V_{m}_{a.split}"
        if run not in runs.values():
            continue
        bs = paired_bootstrap(gold, lex, preds(run), metrics=["Entity-C", "Trig-I", "Trig-C"])
        out["bootstrap"][m] = bs
        for met, v in bs.items():
            lines.append(f"| {m} | {met} | {v['A']:.1f} | {v['B']:.1f} | {v['diff']:+.1f} | "
                         f"[{v['lo']:+.1f}, {v['hi']:+.1f}] | {'yes' if v['significant'] else 'no'} |")

    best = "ds-flash"
    lines += ["", f"## Trig-C F1 per event type (dictionary vs {best} framework)", "",
              "| event type | gold triggers | dictionary | framework | difference |", "|---|---|---|---|---|"]
    t_lex = score_by_type(gold, lex, EVENT_TYPES)
    t_fw = score_by_type(gold, preds(f"staged_G_retrieval3_V_{best}_{a.split}"), EVENT_TYPES)
    for t in EVENT_TYPES:
        d, f = t_lex[t]["Trig-C"], t_fw[t]["Trig-C"]
        out["per_type"][t] = {"n": t_lex[t]["n_gold_triggers"], "dictionary": d, "framework": f}
        lines.append(f"| {t} | {t_lex[t]['n_gold_triggers']} | {d:.1f} | {f:.1f} | {f - d:+.1f} |")

    lines += ["", "## Trig-C recall by whether the gold trigger word is a dictionary entry", "",
              "| system | in dictionary: found / gold (recall) | not in dictionary: found / gold (recall) |",
              "|---|---|---|"]
    for label, run in runs.items():
        s = recall_split(gold, preds(run), vocab)
        out["recall_split"][label] = s
        cell = lambda k: f"{s[k][0]} / {s[k][1]} ({s[k][2]})" if k in s else "-"  # noqa: E731
        lines.append(f"| {label} | {cell('in dictionary')} | {cell('not in dictionary')} |")
    lines += ["", "Dictionary entries: words annotated as triggers in the 1,919 training documents; the rate-50 "
              "dictionary keeps a word only if at least half of its occurrences in the training texts are annotated. "
              "'In dictionary' = the gold trigger word is an entry that the rate-50 dictionary used in this split."]

    res = config.ROOT / "results"
    (res / f"lexicon_{a.split}.md").write_text("\n".join(lines) + "\n")
    (res / f"lexicon_{a.split}.json").write_text(json.dumps(out, indent=2))
    print("\n".join(lines))
    print(f"\nsaved results/lexicon_{a.split}.md / .json")


if __name__ == "__main__":
    main()
