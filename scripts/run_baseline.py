"""Run the naive zero-shot all-in-one baseline (one prompt per document, type and role names only).

  python scripts/run_baseline.py --model glm-air --split dev --limit 5     # quick pilot
  python scripts/run_baseline.py --model ds-flash --split test             # full run

Outputs go to runs/baseline_zs_<model>_<split>/ (predictions.jsonl, raw.jsonl, metrics.json, run.json).
run_main.py runs the same baseline as part of the main experiment and shares its cache.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee import config  # noqa: E402
from newsee.llm import LLM  # noqa: E402
from newsee.runner import run_baseline_zs  # noqa: E402
from newsee.scorer import format_table  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="glm-air", choices=list(config.MODELS))
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    ap.add_argument("--limit", type=int, default=None, help="only the first N documents")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--run_name", default=None)
    a = ap.parse_args()
    llm = LLM(a.model)
    res, info, out = run_baseline_zs(llm, a.split, a.limit, a.workers, run_name=a.run_name)
    print(format_table(res))
    print(f"parse failures: {info['parse_failures']}/{info['n_docs']}   usage: {info['usage']}")
    print(f"saved to {out}")


if __name__ == "__main__":
    main()
