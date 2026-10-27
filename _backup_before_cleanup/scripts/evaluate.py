"""Score a predictions file.

  python scripts/evaluate.py --pred runs/<run>/predictions.jsonl [--gold data/test.jsonl]
  python scripts/evaluate.py --oracle [--gold data/dev.jsonl]   # sanity check: must be 100
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee import config  # noqa: E402
from newsee.io_utils import read_jsonl  # noqa: E402
from newsee.scorer import format_table, score  # noqa: E402


def oracle(golds):
    """Turn gold annotations into predictions (one event per trigger mention)."""
    preds = []
    for g in golds:
        ents = [{"text": m, "type": e["type"]} for e in g["entities"] for m in e["mentions"]]
        evs = []
        for e in g["events"]:
            for t in e["triggers"]:
                evs.append({"trigger": t, "type": e["type"],
                            "arguments": {r: [it[0] for it in items] for r, items in e["arguments"].items()}})
        preds.append({"id": g["id"], "entities": ents, "events": evs})
    return preds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", default=str(config.DATA_DIR / "test.jsonl"))
    ap.add_argument("--pred")
    ap.add_argument("--oracle", action="store_true")
    ap.add_argument("--out", help="optional path to save metrics json")
    a = ap.parse_args()
    golds = read_jsonl(a.gold)
    preds = oracle(golds) if a.oracle else read_jsonl(a.pred)
    res = score(golds, preds)
    print(format_table(res))
    print(res["_coverage"])
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
