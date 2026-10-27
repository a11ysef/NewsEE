"""Paired bootstrap over documents: is run B really better or worse than run A?

  python scripts/significance.py --gold data/dev.jsonl --a runs/<A> --b runs/<B> [--b runs/<C> ...]

Documents are resampled with replacement 1000 times; micro-F1 of A and B is recomputed on the
same sample, giving the F1 difference (B - A), its 95% confidence interval, and a star when the
interval excludes 0.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee.io_utils import read_jsonl  # noqa: E402
from newsee.stats import paired_bootstrap  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--a", required=True, help="reference run directory")
    ap.add_argument("--b", required=True, action="append", help="run directory to compare (repeatable)")
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    golds = read_jsonl(a.gold)
    pa = read_jsonl(Path(a.a) / "predictions.jsonl")
    print(f"reference A = {Path(a.a).name}   ({len(golds)} documents, {a.n} bootstrap samples)\n")
    for b in a.b:
        res = paired_bootstrap(golds, pa, read_jsonl(Path(b) / "predictions.jsonl"), n=a.n, seed=a.seed)
        print(f"B = {Path(b).name}")
        print(f"  {'metric':12s} {'A':>6s} {'B':>6s} {'B-A':>7s}   95% CI")
        for m, v in res.items():
            star = "*" if v["significant"] else " "
            print(f"  {m:12s} {v['A']:6.1f} {v['B']:6.1f} {v['diff']:+7.1f}   [{v['lo']:+5.1f}, {v['hi']:+5.1f}] {star}")
        print()


if __name__ == "__main__":
    main()
