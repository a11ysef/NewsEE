"""Stability check: re-run the final framework N more times without the cache and report
mean, standard deviation and range of each metric (the original run counts as run 0).

  python scripts/run_repeat.py --model ds-flash --runs 2      # about 2 x 2.2 RMB off-peak

Writes results/repeat_<model>_<split>.md / .json
"""
import argparse
import json
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee import config  # noqa: E402
from newsee.framework import FINAL  # noqa: E402
from newsee.llm import LLM  # noqa: E402
from newsee.runner import run_framework  # noqa: E402

METRICS = ["Entity-C", "Trig-I", "Trig-C", "Arg-I (EM)", "Arg-C (EM)", "Arg-C (BoW)"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="ds-flash", choices=list(config.MODELS))
    ap.add_argument("--split", default="test", choices=["dev", "test"])
    ap.add_argument("--runs", type=int, default=2, help="extra independent runs")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    results = []
    base = config.RUNS_DIR / f"{FINAL.name()}_{a.model}_{a.split}" / "metrics.json"
    if base.exists():
        results.append(("run 0 (original)", json.loads(base.read_text())))
    for r in range(1, a.runs + 1):
        llm = LLM(a.model, cache_tag=f"rep{r}")
        res, info, _ = run_framework(llm, FINAL, a.split, workers=a.workers,
                                     run_name=f"{FINAL.name()}_{a.model}_{a.split}_rep{r}")
        results.append((f"run {r}", res))
        print(f"  run {r}: Trig-C {res['Trig-C']['F1']}  Arg-C {res['Arg-C (EM)']['F1']}  "
              f"parse fail {info['parse_failures']}  blocked {info['usage'].get('filtered', 0)}")

    lines = [f"# Stability of the framework: {a.model} on {a.split} ({len(results)} runs)", "",
             "| run | " + " | ".join(METRICS) + " |", "|---|" + "---|" * len(METRICS)]
    for name, res in results:
        lines.append(f"| {name} | " + " | ".join(f"{res[m]['F1']:.1f}" for m in METRICS) + " |")
    summary = {}
    row_m, row_r = [], []
    for m in METRICS:
        xs = [res[m]["F1"] for _, res in results]
        mean, sd = st.mean(xs), (st.stdev(xs) if len(xs) > 1 else 0.0)
        summary[m] = {"mean": round(mean, 2), "sd": round(sd, 2), "min": min(xs), "max": max(xs)}
        row_m.append(f"{mean:.1f} ± {sd:.1f}")
        row_r.append(f"{min(xs):.1f} to {max(xs):.1f}")
    lines += ["| **mean ± sd** | " + " | ".join(row_m) + " |", "| range | " + " | ".join(row_r) + " |"]
    out = config.ROOT / "results"
    out.mkdir(exist_ok=True)
    stem = out / f"repeat_{a.model}_{a.split}"
    Path(f"{stem}.md").write_text("\n".join(lines) + "\n")
    Path(f"{stem}.json").write_text(json.dumps({"runs": [n for n, _ in results], "summary": summary}, indent=2))
    print("\n" + "\n".join(lines) + f"\n\nsaved {stem}.md / .json")


if __name__ == "__main__":
    main()
