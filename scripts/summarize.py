"""Combine all results/main_<model>_<split>.json into one cross-model table.

  python scripts/summarize.py            # test split
  python scripts/summarize.py --split dev
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee import config  # noqa: E402

ORDER = ["glm-4.7", "ds-pro", "glm-air", "ds-flash", "ds-flash-think", "qwen3b", "glm-flash"]
COLS = ["Entity-C", "Trig-I", "Trig-C", "Arg-C (EM)", "Arg-C (BoW)"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test")
    a = ap.parse_args()
    files = sorted((config.ROOT / "results").glob(f"main_*_{a.split}.json"))
    data = [json.loads(f.read_text()) for f in files]
    data.sort(key=lambda d: ORDER.index(d["model"]) if d["model"] in ORDER else 99)
    lines = [f"# All models on {a.split}", "", "| model | method | " + " | ".join(COLS) + " |",
             "|---|---|" + "---|" * len(COLS)]
    for d in data:
        for label, row in d["rows"].items():
            m = row["metrics"]
            lines.append(f"| {d['model']} | {label} | " + " | ".join(f"{m[c]['F1']:.1f}" for c in COLS) + " |")
    lines += ["", "Framework minus baseline (✱ = 95% CI excludes 0):", "",
              "| model | " + " | ".join(COLS) + " |", "|---|" + "---|" * len(COLS)]
    for d in data:
        s = d.get("framework_vs_baseline")
        if s:
            lines.append(f"| {d['model']} | " + " | ".join(
                f"{s[c]['diff']:+.1f}{' ✱' if s[c]['significant'] else ''}" for c in COLS) + " |")
    out = config.ROOT / "results" / f"summary_{a.split}.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
