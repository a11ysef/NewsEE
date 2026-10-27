"""Dictionary (lexicon) baseline: no LLM, no API calls.

  python scripts/run_lexicon.py --split test

A word list is built from the annotated training documents (data/pool.jsonl), the same
documents the framework draws its demonstrations from:
  trigger lexicon  every word annotated as a trigger -> its most frequent event type
  entity lexicon   every annotated entity mention    -> its most frequent entity type
A target document is labelled by looking up every occurrence of every lexicon entry.
This is the classic keyword-dictionary approach (as used for comment sentiment analysis),
so it shows what the LLM adds beyond word lookup. It cannot produce argument roles.

Two variants
  lexicon_all       every entry is used
  lexicon_rate50    an entry is used only if, in the training texts, it is annotated in at
                    least 50% of its occurrences (e.g. "fire" is often not an event)
"""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee import config  # noqa: E402
from newsee.io_utils import read_jsonl, write_jsonl  # noqa: E402
from newsee.scorer import format_table, norm, score  # noqa: E402


def build(pool):
    trig_types, ent_types = defaultdict(Counter), defaultdict(Counter)
    for d in pool:
        for e in d["events"]:
            for t in e["triggers"]:
                if norm(t):
                    trig_types[norm(t)][e["type"]] += 1
        for e in d["entities"]:
            for m in e["mentions"]:
                if norm(m):
                    ent_types[norm(m)][e["type"]] += 1
    texts = [f" {norm(d['text'])} " for d in pool]

    def rate(lex):
        out = {}
        for w, c in lex.items():
            seen = sum(t.count(f" {w} ") for t in texts)
            out[w] = (c.most_common(1)[0][0], sum(c.values()) / seen if seen else 0.0)
        return out
    return rate(trig_types), rate(ent_types)


def label(doc, trig_lex, ent_lex, min_rate):
    t = f" {norm(doc['text'])} "
    ents, evs = [], []
    for w, (typ, r) in ent_lex.items():
        if r >= min_rate:
            ents += [{"text": w, "type": typ}] * t.count(f" {w} ")
    for w, (typ, r) in trig_lex.items():
        if r >= min_rate:
            evs += [{"trigger": w, "type": typ, "arguments": {}}] * t.count(f" {w} ")
    return {"id": doc["id"], "entities": ents, "events": evs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test", choices=["dev", "test"])
    a = ap.parse_args()
    pool = read_jsonl(config.DATA_DIR / "pool.jsonl")
    gold = read_jsonl(config.DATA_DIR / f"{a.split}.jsonl")
    trig_lex, ent_lex = build(pool)
    print(f"lexicon from {len(pool)} training documents: {len(trig_lex)} trigger words, {len(ent_lex)} entity strings")
    for name, min_rate in (("lexicon_all", 0.0), ("lexicon_rate50", 0.5)):
        preds = [label(d, trig_lex, ent_lex, min_rate) for d in gold]
        res = score(gold, preds)
        out = config.RUNS_DIR / f"{name}_{a.split}"
        out.mkdir(parents=True, exist_ok=True)
        write_jsonl(preds, out / "predictions.jsonl")
        (out / "metrics.json").write_text(json.dumps(res, indent=2))
        (out / "run.json").write_text(json.dumps({
            "method": "lexicon", "variant": name, "min_rate": min_rate, "split": a.split, "n_docs": len(gold),
            "trigger_entries": sum(r >= min_rate for _, r in trig_lex.values()),
            "entity_entries": sum(r >= min_rate for _, r in ent_lex.values()), "llm_calls": 0}, indent=2))
        print(f"\n== {name} ({a.split}, {len(gold)} documents)\n" + format_table(res))


if __name__ == "__main__":
    main()
