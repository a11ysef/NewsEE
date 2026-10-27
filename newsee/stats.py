"""Paired bootstrap over documents and helpers to restrict scoring to some event types."""
import random

from .scorer import _arg_counts, _entity_counts, _trigger_counts

METRICS = ["Entity-C", "Trig-I", "Trig-C", "Arg-C (EM)", "Arg-C (BoW)"]


def restrict_types(docs, types):
    """Keep only events whose type is in `types` (entities unchanged)."""
    types = set(types)
    return [{**d, "events": [e for e in d.get("events", []) if e.get("type") in types]} for d in docs]


def per_doc_counts(golds, preds):
    pmap = {p["id"]: p for p in preds}
    rows = []
    for g in golds:
        p = pmap.get(g["id"], {"id": g["id"], "entities": [], "events": []})
        _, ec = _entity_counts(g, p)
        ti, tc = _trigger_counts(g, p)
        rows.append({"Entity-C": ec, "Trig-I": ti, "Trig-C": tc,
                     "Arg-C (EM)": _arg_counts(g, p, True, True, False),
                     "Arg-C (BoW)": _arg_counts(g, p, True, True, True)})
    return rows


def f1(rows, idx, m):
    c = sum(rows[i][m][0] for i in idx)
    npred = sum(rows[i][m][1] for i in idx)
    ngold = sum(rows[i][m][2] for i in idx)
    p = c / npred if npred else 0.0
    r = c / ngold if ngold else 0.0
    return 100 * 2 * p * r / (p + r) if p + r else 0.0


def paired_bootstrap(golds, preds_a, preds_b, metrics=METRICS, n=1000, seed=42):
    """{metric: {"A", "B", "diff", "lo", "hi", "significant"}} for B - A."""
    A, B = per_doc_counts(golds, preds_a), per_doc_counts(golds, preds_b)
    k = len(golds)
    rng = random.Random(seed)
    samples = [[rng.randrange(k) for _ in range(k)] for _ in range(n)]
    full = list(range(k))
    out = {}
    for m in metrics:
        diffs = sorted(f1(B, s, m) - f1(A, s, m) for s in samples)
        lo, hi = diffs[int(0.025 * n)], diffs[int(0.975 * n) - 1]
        a, b = f1(A, full, m), f1(B, full, m)
        out[m] = {"A": round(a, 2), "B": round(b, 2), "diff": round(b - a, 2),
                  "lo": round(lo, 2), "hi": round(hi, 2), "significant": lo > 0 or hi < 0}
    return out
