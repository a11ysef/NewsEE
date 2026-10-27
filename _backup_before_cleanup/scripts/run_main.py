"""Main experiment on the test set for one model: baseline vs final framework (+ gold triggers).

  python scripts/run_main.py --model glm-air
  python scripts/run_main.py --model ds-pro --skip-baseline      # save money on the expensive model
  python scripts/run_main.py --model glm-air --split dev --limit 3   # quick check

Writes results/main_<model>_<split>.md (tables for Chapter 5) and .json (used by summarize.py).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee import config  # noqa: E402
from newsee.framework import FrameworkConfig  # noqa: E402
from newsee.io_utils import read_jsonl  # noqa: E402
from newsee.llm import LLM  # noqa: E402
from newsee.runner import run_baseline_zs, run_framework  # noqa: E402
from newsee.schema import EVENT_TYPES  # noqa: E402
from newsee.scorer import score_by_type  # noqa: E402
from newsee.stats import paired_bootstrap  # noqa: E402

# Final configuration chosen on the dev set (week 2)
FINAL = FrameworkConfig(decompose=True, guidelines=True, demos="retrieval", k=3, verify=True)
COLS = [("Entity-C", "F1"), ("Trig-I", "F1"), ("Trig-C", "F1"), ("Arg-I (EM)", "F1"),
        ("Arg-C (EM)", "F1"), ("Arg-C (BoW)", "F1")]
# rough peak-hour prices, RMB per million tokens (input, output); Zhipu runs use resource packs
PRICES = {"ds-flash": (2, 8), "ds-pro": (9, 27), "ds-flash-think": (2, 8)}


def cost(model, usage):
    pin, pout = PRICES.get(model, (0, 0))
    return round(usage.get("prompt_tokens", 0) / 1e6 * pin + usage.get("completion_tokens", 0) / 1e6 * pout, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=list(config.MODELS))
    ap.add_argument("--split", default="test", choices=["dev", "test"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--skip-baseline", action="store_true")
    ap.add_argument("--skip-goldtrig", action="store_true")
    a = ap.parse_args()

    llm = LLM(a.model)
    golds = read_jsonl(config.DATA_DIR / f"{a.split}.jsonl")[: a.limit]
    runs = {}
    if not a.skip_baseline:
        runs["Baseline (zero-shot, all-in-one)"] = run_baseline_zs(llm, a.split, a.limit, a.workers)
    runs["NewsEE framework"] = run_framework(llm, FINAL, a.split, a.limit, a.workers)
    if not a.skip_goldtrig:
        from dataclasses import replace
        runs["Framework, gold triggers"] = run_framework(llm, replace(FINAL, setting="gold_trigger"),
                                                         a.split, a.limit, a.workers)

    lines = [f"# Main results: {a.model} ({llm.model}) on {a.split} ({len(golds)} documents)", "",
             "| setting | " + " | ".join(m for m, _ in COLS) + " | calls | parse fail | blocked | tokens (k) | cost (RMB, peak) |",
             "|" + "---|" * (len(COLS) + 6)]
    summary = {"model": a.model, "model_id": llm.model, "split": a.split, "n_docs": len(golds), "rows": {}}
    for label, (res, info, out) in runs.items():
        u = info["usage"]
        tok = round((u.get("prompt_tokens", 0) + u.get("completion_tokens", 0)) / 1000, 1)
        lines.append(f"| {label} | " + " | ".join(f"{res[m][k]:.1f}" for m, k in COLS) +
                     f" | {info['llm_calls']} | {info['parse_failures']} | {u.get('filtered', 0)} | {tok} | {cost(a.model, u)} |")
        summary["rows"][label] = {"metrics": res, "info": info, "run_dir": str(out)}

    base = "Baseline (zero-shot, all-in-one)"
    if base in runs:
        pb = read_jsonl(runs[base][2] / "predictions.jsonl")
        pf = read_jsonl(runs["NewsEE framework"][2] / "predictions.jsonl")
        sig = paired_bootstrap(golds, pb, pf)
        summary["framework_vs_baseline"] = sig
        lines += ["", "## Framework minus baseline (paired bootstrap, 1000 samples)", "",
                  "| metric | baseline | framework | difference | 95% CI | significant |", "|---|---|---|---|---|---|"]
        for m, v in sig.items():
            lines.append(f"| {m} | {v['A']:.1f} | {v['B']:.1f} | {v['diff']:+.1f} | [{v['lo']:+.1f}, {v['hi']:+.1f}] | {'yes' if v['significant'] else 'no'} |")
        bt = score_by_type(golds, pb, EVENT_TYPES)
        ft = score_by_type(golds, pf, EVENT_TYPES)
        summary["per_type"] = {"baseline": bt, "framework": ft}
        lines += ["", "## Per event type (F1)", "",
                  "| event type | gold triggers | Trig-C baseline | Trig-C framework | Arg-C baseline | Arg-C framework |",
                  "|---|---|---|---|---|---|"]
        for t in EVENT_TYPES:
            lines.append(f"| {t} | {ft[t]['n_gold_triggers']} | {bt[t]['Trig-C']:.1f} | {ft[t]['Trig-C']:.1f} | "
                         f"{bt[t]['Arg-C (EM)']:.1f} | {ft[t]['Arg-C (EM)']:.1f} |")

    fw_info = runs["NewsEE framework"][1]
    lines += ["", f"Verification removed (framework): {fw_info.get('verification_removed', {})}"]
    out_dir = config.ROOT / "results"
    out_dir.mkdir(exist_ok=True)
    stem = out_dir / (f"main_{a.model}_{a.split}" + (f"_n{a.limit}" if a.limit else ""))
    Path(f"{stem}.md").write_text("\n".join(lines) + "\n")
    Path(f"{stem}.json").write_text(json.dumps(summary, indent=2, default=str))
    print("\n" + "\n".join(lines))
    print(f"\nsaved {stem}.md / .json")


if __name__ == "__main__":
    main()
