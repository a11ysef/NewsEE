"""Paired bootstrap over documents: is configuration B really better/worse than A?

  python scripts/significance.py --gold data/dev.jsonl --a runs/<A> --b runs/<B> [--b runs/<C> ...]

For each metric it resamples the documents with replacement (1000 times), recomputes
micro-F1 for A and B on the same sample, and reports the F1 difference (B - A) with a
95% confidence interval and the share of samples where B > A. A difference whose interval
excludes 0 is reported as significant.
"""
import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee.io_utils import read_jsonl  # noqa: E402
from newsee.scorer import _arg_counts, _entity_counts, _trigger_counts  # noqa: E402

METRICS = ["Entity-C", "Trig-I", "Trig-C", "Arg-C (EM)", "Arg-C (BoW)"]


def per_doc_counts(golds, preds):
    pmap = {p["id"]: p for p in preds}
    rows = []
    for g in golds:
        p = pmap.get(g["id"], {"id": g["id"], "entities": [], "events": []})
        _, ec = _entity_counts(g, p)
        ti, tc = _trigger_counts(g, p)
        rows.append({
            "Entity-C": ec, "Trig-I": ti, "Trig-C": tc,
            "Arg-C (EM)": _arg_counts(g, p, True, True, False),
            "Arg-C (BoW)": _arg_counts(g, p, True, True, True),
        })
    return rows


def f1(rows, idx, m):
    c = sum(rows[i][m][0] for i in idx)
    npred = sum(rows[i][m][1] for i in idx)
    ngold = sum(rows[i][m][2] for i in idx)
    p = c / npred if npred else 0.0
    r = c / ngold if ngold else 0.0
    return 100 * 2 * p * r / (p + r) if p + r else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--a", required=True, help="reference run directory")
    ap.add_argument("--b", required=True, action="append", help="run directory to compare (repeatable)")
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    golds = read_jsonl(a.gold)
    A = per_doc_counts(golds, read_jsonl(Path(a.a) / "predictions.jsonl"))
    n = len(golds)
    print(f"reference A = {Path(a.a).name}   ({n} documents, {a.n} bootstrap samples)\n")
    for b in a.b:
        B = per_doc_counts(golds, read_jsonl(Path(b) / "predictions.jsonl"))
        rng = random.Random(a.seed)
        samples = [[rng.randrange(n) for _ in range(n)] for _ in range(a.n)]
        print(f"B = {Path(b).name}")
        print(f"  {'metric':12s} {'A':>6s} {'B':>6s} {'B-A':>7s}   95% CI           P(B>A)")
        full = list(range(n))
        for m in METRICS:
            diffs = sorted(f1(B, s, m) - f1(A, s, m) for s in samples)
            lo, hi = diffs[int(0.025 * a.n)], diffs[int(0.975 * a.n) - 1]
            share = sum(d > 0 for d in diffs) / a.n
            sig = "*" if lo > 0 or hi < 0 else " "
            print(f"  {m:12s} {f1(A, full, m):6.1f} {f1(B, full, m):6.1f} {f1(B, full, m) - f1(A, full, m):+7.1f}"
                  f"   [{lo:+5.1f}, {hi:+5.1f}] {sig}  {share:5.2f}")
        print()


if __name__ == "__main__":
    main()
