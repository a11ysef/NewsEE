"""Check that every reported number can be recomputed from the saved model outputs.

  python scripts/verify_results.py

No API calls. For every run in runs/ it re-scores predictions.jsonl against the gold data with
the frozen scorer and compares the result with the stored metrics.json; it then checks that the
tables in results/main_*.json match those runs. Exit code 1 if anything differs.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee import config  # noqa: E402
from newsee.io_utils import read_jsonl  # noqa: E402
from newsee.scorer import score  # noqa: E402

TOL = 0.01


def same(a, b):
    for k, v in a.items():
        if k.startswith("_"):
            continue
        for m in ("P", "R", "F1"):
            if abs(v[m] - b[k][m]) > TOL:
                return f"{k} {m}: stored {b[k][m]} vs recomputed {v[m]}"
    return None


def main():
    golds = {}
    problems, checked = [], 0
    for run in sorted(p for p in config.RUNS_DIR.iterdir() if p.is_dir() and not p.name.startswith("_")):
        files = [run / f for f in ("predictions.jsonl", "metrics.json", "run.json")]
        if not all(f.exists() for f in files):
            problems.append(f"{run.name}: missing output files")
            continue
        info = json.loads((run / "run.json").read_text())
        split = info["split"]
        if split not in golds:
            golds[split] = read_jsonl(config.DATA_DIR / f"{split}.jsonl")
        gold = golds[split][: info["n_docs"]]
        res = score(gold, read_jsonl(run / "predictions.jsonl"))
        diff = same(res, json.loads((run / "metrics.json").read_text()))
        checked += 1
        status = "ok" if diff is None else "DIFF"
        print(f"  {status:4s}  {run.name:60s} Trig-C {res['Trig-C']['F1']:6.2f}  Arg-C {res['Arg-C (EM)']['F1']:6.2f}")
        if diff:
            problems.append(f"{run.name}: {diff}")

    tables = 0
    for f in sorted((config.ROOT / "results").glob("main_*.json")):
        d = json.loads(f.read_text())
        for label, row in d["rows"].items():
            run_dir = Path(row["run_dir"])
            local = config.RUNS_DIR / run_dir.name
            if not (local / "metrics.json").exists():
                problems.append(f"{f.name} / {label}: run {run_dir.name} not found")
                continue
            diff = same(row["metrics"], json.loads((local / "metrics.json").read_text()))
            tables += 1
            if diff:
                problems.append(f"{f.name} / {label}: {diff}")

    print(f"\nre-scored {checked} runs, checked {tables} table rows in results/main_*.json")
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  - " + p)
        sys.exit(1)
    print("ALL RESULTS REPRODUCED FROM SAVED OUTPUTS")


if __name__ == "__main__":
    main()
