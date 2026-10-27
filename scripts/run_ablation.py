"""Ablation study: full framework vs. removing one module at a time.

  python scripts/run_ablation.py --model glm-air --split dev
  python scripts/run_ablation.py --model glm-air --split dev --shots 0,1,3,5   # demonstration-count curve
  python scripts/run_ablation.py --model glm-air --split dev --only full,no_verify

Writes results/ablation_<model>_<split>.md and .csv (the table goes straight into
Chapter 5). Stages shared between configurations are served from the cache, so
each extra configuration only pays for the calls that actually change.
"""
import argparse
import csv
import json
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee import config  # noqa: E402
from newsee.framework import FINAL  # noqa: E402
from newsee.llm import LLM  # noqa: E402
from newsee.runner import run_framework  # noqa: E402

FULL = FINAL
PRESETS = {
    "full": ("Full framework", FULL),
    "no_decompose": ("w/o decomposition (all-in-one)", replace(FULL, decompose=False)),
    "no_guidelines": ("w/o guidelines", replace(FULL, guidelines=False)),
    "random_demos": ("random instead of retrieved demos", replace(FULL, demos="random")),
    "no_demos": ("w/o demonstrations (zero-shot)", replace(FULL, demos="none", k=0)),
    "no_verify": ("w/o verification", replace(FULL, verify=False)),
    "gold_trigger": ("full, gold triggers (arguments only)", replace(FULL, setting="gold_trigger")),
}
COLS = [("Entity-C", "F1"), ("Trig-I", "F1"), ("Trig-C", "F1"),
        ("Arg-I (EM)", "F1"), ("Arg-C (EM)", "F1"), ("Arg-C (BoW)", "F1")]


def row(label, res, info):
    r = {"setting": label}
    for m, k in COLS:
        r[m] = res[m][k]
    r["parse fail"] = f"{info.get('parse_failures', 0)}/{info.get('llm_calls', info.get('n_docs', 0))}"
    u = info.get("usage", {})
    r["blocked by filter"] = u.get("filtered", 0)
    r["tokens (k)"] = round((u.get("prompt_tokens", 0) + u.get("completion_tokens", 0)) / 1000, 1)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="glm-air", choices=list(config.MODELS))
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--only", help="comma-separated preset names: " + ",".join(PRESETS))
    ap.add_argument("--shots", help="comma-separated k values for the demonstration curve, e.g. 0,1,3,5")
    a = ap.parse_args()

    if a.shots:
        jobs = [(f"k={k}", replace(FULL, demos="none" if k == 0 else "retrieval", k=k))
                for k in map(int, a.shots.split(","))]
        tag = "shots"
    else:
        names = a.only.split(",") if a.only else list(PRESETS)
        jobs = [PRESETS[n] for n in names]
        tag = "ablation"

    llm = LLM(a.model)
    rows = []
    base = config.RUNS_DIR / f"baseline_zs_{a.model}_{a.split}" / "metrics.json"
    if not a.shots and base.exists() and not a.limit:
        info = json.loads((base.parent / "run.json").read_text())
        rows.append(row("Baseline: naive zero-shot all-in-one", json.loads(base.read_text()), info))
    for label, cfg in jobs:
        res, info, _ = run_framework(llm, cfg, a.split, a.limit, a.workers)
        rows.append(row(label, res, info))
        print(f"  done: {label}  Trig-C {res['Trig-C']['F1']}  Arg-C(EM) {res['Arg-C (EM)']['F1']}")

    out_dir = config.ROOT / "results"
    out_dir.mkdir(exist_ok=True)
    stem = out_dir / f"{tag}_{a.model}_{a.split}" if not a.limit else out_dir / f"{tag}_{a.model}_{a.split}_n{a.limit}"
    keys = list(rows[0].keys())
    with open(f"{stem}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    md = ["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys)]
    md += ["| " + " | ".join(str(r[k]) for k in keys) + " |" for r in rows]
    Path(f"{stem}.md").write_text("\n".join(md) + "\n")
    print("\n" + "\n".join(md))
    print(f"\nsaved {stem}.md / .csv")


if __name__ == "__main__":
    main()
