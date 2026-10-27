"""Shared experiment runner: run a method over a split, save outputs, score."""
import json
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict

from . import config
from .framework import Framework
from .io_utils import read_jsonl, write_jsonl
from .retrieval import Retriever
from .scorer import score

_RETRIEVER = None


def get_retriever():
    global _RETRIEVER
    if _RETRIEVER is None:
        _RETRIEVER = Retriever(read_jsonl(config.DATA_DIR / "pool.jsonl"))
    return _RETRIEVER


def run_framework(llm, cfg, split, limit=None, workers=4, run_name=None, quiet=False):
    docs = read_jsonl(config.DATA_DIR / f"{split}.jsonl")[:limit]
    name = run_name or f"{cfg.name()}_{llm.name}_{split}" + (f"_n{limit}" if limit else "")
    out = config.RUNS_DIR / name
    out.mkdir(parents=True, exist_ok=True)
    fw = Framework(llm, cfg, get_retriever() if cfg.demos != "none" else None)
    usage0 = dict(llm.usage)
    t0 = time.time()
    preds, traces = [], []
    workers = min(workers, config.MAX_WORKERS.get(llm.name, workers))
    with ThreadPoolExecutor(max_workers=1 if llm.provider == "ollama" else workers) as ex:
        for i, (p, tr) in enumerate(ex.map(fw.run, docs), 1):
            preds.append(p)
            traces.append({"id": p["id"], **tr})
            if not quiet:
                print(f"\r  {name}: {i}/{len(docs)}", end="", flush=True)
    if not quiet:
        print()
    res = score(docs, preds)
    calls = [c for t in traces for c in t["calls"]]
    removed = Counter()
    for t in traces:
        removed.update(t.get("removed", {}))
    usage = {k: llm.usage[k] - usage0.get(k, 0) for k in llm.usage}
    info = {
        "method": "framework", "config": asdict(cfg), "config_name": cfg.name(),
        "model": llm.name, "model_id": llm.model, "split": split, "n_docs": len(docs),
        "llm_calls": len(calls),
        "parse_failures": sum(c["parse_error"] is not None and c["reply_chars"] > 0 for c in calls),
        "empty_replies": sum(c["reply_chars"] == 0 for c in calls),
        "verification_removed": dict(removed), "usage": usage, "seconds": round(time.time() - t0, 1),
    }
    write_jsonl(preds, out / "predictions.jsonl")
    write_jsonl(traces, out / "traces.jsonl")
    (out / "metrics.json").write_text(json.dumps(res, indent=2))
    (out / "run.json").write_text(json.dumps(info, indent=2))
    return res, info, out


def run_baseline_zs(llm, split, limit=None, workers=4, quiet=False):
    """Naive zero-shot all-in-one baseline (same prompts as scripts/run_baseline.py, so it
    shares the cache with earlier baseline runs)."""
    from .io_utils import parse_json
    from .prompts import baseline_all_in_one, to_prediction

    docs = read_jsonl(config.DATA_DIR / f"{split}.jsonl")[:limit]
    name = f"baseline_zs_{llm.name}_{split}" + (f"_n{limit}" if limit else "")
    out = config.RUNS_DIR / name
    out.mkdir(parents=True, exist_ok=True)
    usage0 = dict(llm.usage)
    t0 = time.time()

    def work(doc):
        reply = llm.chat(baseline_all_in_one(doc["text"]))
        obj, err = parse_json(reply)
        return to_prediction(doc["id"], obj), {"id": doc["id"], "reply": reply, "parse_error": err}

    preds, raws = [], []
    workers = min(workers, config.MAX_WORKERS.get(llm.name, workers))
    with ThreadPoolExecutor(max_workers=1 if llm.provider == "ollama" else workers) as ex:
        for i, (p, r) in enumerate(ex.map(work, docs), 1):
            preds.append(p)
            raws.append(r)
            if not quiet:
                print(f"\r  {name}: {i}/{len(docs)}", end="", flush=True)
    if not quiet:
        print()
    res = score(docs, preds)
    usage = {k: llm.usage[k] - usage0.get(k, 0) for k in llm.usage}
    info = {"method": "baseline_zero_shot_all_in_one", "model": llm.name, "model_id": llm.model,
            "split": split, "n_docs": len(docs), "llm_calls": len(docs),
            "parse_failures": sum(r["parse_error"] is not None and bool(r["reply"]) for r in raws),
            "empty_replies": sum(not r["reply"] for r in raws),
            "usage": usage, "seconds": round(time.time() - t0, 1)}
    write_jsonl(preds, out / "predictions.jsonl")
    write_jsonl(raws, out / "raw.jsonl")
    (out / "metrics.json").write_text(json.dumps(res, indent=2))
    (out / "run.json").write_text(json.dumps(info, indent=2))
    return res, info, out
