"""Run the naive zero-shot all-in-one baseline and score it.

  python scripts/run_baseline.py --model glm-flash --split dev --limit 5     # quick pilot
  python scripts/run_baseline.py --model ds-flash --split test               # full run

Outputs go to runs/<run_name>/:
  predictions.jsonl  parsed predictions (scorer format)
  raw.jsonl          raw model replies + parse errors (for error analysis)
  metrics.json       scores
  run.json           configuration, token usage, parse-failure rate
"""
import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee import config  # noqa: E402
from newsee.io_utils import parse_json, read_jsonl, write_jsonl  # noqa: E402
from newsee.llm import LLM  # noqa: E402
from newsee.prompts import baseline_all_in_one, to_prediction  # noqa: E402
from newsee.scorer import format_table, score  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="glm-flash", choices=list(config.MODELS))
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    ap.add_argument("--limit", type=int, default=None, help="only the first N documents")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--run_name", default=None)
    a = ap.parse_args()

    docs = read_jsonl(config.DATA_DIR / f"{a.split}.jsonl")[: a.limit]
    run_name = a.run_name or f"baseline_zs_{a.model}_{a.split}" + (f"_n{a.limit}" if a.limit else "")
    out = config.RUNS_DIR / run_name
    out.mkdir(parents=True, exist_ok=True)
    llm = LLM(a.model)

    def work(doc):
        reply = llm.chat(baseline_all_in_one(doc["text"]))
        obj, err = parse_json(reply)
        return to_prediction(doc["id"], obj), {"id": doc["id"], "reply": reply, "parse_error": err}

    t0 = time.time()
    preds, raws = [], []
    with ThreadPoolExecutor(max_workers=1 if a.model == "qwen3b" else a.workers) as ex:
        for i, (p, r) in enumerate(ex.map(work, docs), 1):
            preds.append(p); raws.append(r)
            print(f"\r{i}/{len(docs)} documents", end="", flush=True)
    print()

    write_jsonl(preds, out / "predictions.jsonl")
    write_jsonl(raws, out / "raw.jsonl")
    res = score(docs, preds)
    (out / "metrics.json").write_text(json.dumps(res, indent=2))
    n_fail = sum(r["parse_error"] is not None for r in raws)
    (out / "run.json").write_text(json.dumps({
        "method": "baseline_zero_shot_all_in_one", "model": a.model, "model_id": llm.model,
        "split": a.split, "n_docs": len(docs), "parse_failures": n_fail,
        "usage": llm.usage, "seconds": round(time.time() - t0, 1),
    }, indent=2))
    print(format_table(res))
    print(f"parse failures: {n_fail}/{len(docs)}   usage: {llm.usage}")
    print(f"saved to {out}")


if __name__ == "__main__":
    main()
