"""Build NewsEE evaluation data from raw MAVEN-Arg.

Outputs (in data/):
  dev.jsonl   - 30 validation documents for prompt development
  test.jsonl  - 120 validation documents for reported results
  pool.jsonl  - training documents used as few-shot demonstrations
  stats.json  - dataset statistics for the thesis (Chapter 4)

Each output line is a simplified document:
  {"id", "title", "text",
   "entities": [{"id", "type", "mentions": [str, ...]}],
   "events":   [{"id", "type", "triggers": [str, ...],
                 "arguments": {role: [[acceptable strings], ...]}}]}
Only events of the 12 selected types are kept. For an entity argument every
coreferent mention is an acceptable answer.

Usage:  python scripts/prepare_data.py  [--maven_dir ~/Downloads/MAVEN-Arg]
"""
import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee import config  # noqa: E402
from newsee.schema import EVENT_TYPES, roles_of  # noqa: E402


def simplify(doc):
    ents = {e["id"]: e for e in doc.get("entities", [])}
    out_ents = [
        {"id": e["id"], "type": e["type"], "mentions": [m["mention"] for m in e["mention"]]}
        for e in doc.get("entities", [])
    ]
    out_events = []
    for ev in doc.get("events", []):
        if ev["type"] not in EVENT_TYPES:
            continue
        args = {}
        for role in roles_of(ev["type"]):
            items = []
            for a in ev["argument"].get(role, []):
                if "entity_id" in a:
                    ent = ents.get(a["entity_id"])
                    if ent:
                        items.append([m["mention"] for m in ent["mention"]])
                else:
                    items.append([a["content"]])
            if items:
                args[role] = items
        out_events.append({
            "id": ev["id"],
            "type": ev["type"],
            "triggers": [m["trigger_word"] for m in ev["mention"]],
            "offsets": [m["offset"] for m in ev["mention"]],  # char offsets, parallel to triggers
            "arguments": args,
        })
    return {"id": doc["id"], "title": doc["title"], "text": doc["document"],
            "entities": out_ents, "events": out_events}


def load(path, max_words):
    docs = []
    with open(path) as f:
        for line in f:
            d = simplify(json.loads(line))
            if d["events"] and len(d["text"].split()) <= max_words:
                docs.append(d)
    return docs


def stats(docs):
    ev = Counter(e["type"] for d in docs for e in d["events"])
    return {
        "documents": len(docs),
        "avg_words": round(sum(len(d["text"].split()) for d in docs) / len(docs), 1),
        "entities": sum(len(d["entities"]) for d in docs),
        "entity_mentions": sum(len(e["mentions"]) for d in docs for e in d["entities"]),
        "events": sum(ev.values()),
        "trigger_mentions": sum(len(e["triggers"]) for d in docs for e in d["events"]),
        "arguments": sum(len(v) for d in docs for e in d["events"] for v in e["arguments"].values()),
        "events_per_type": dict(ev.most_common()),
    }


def dump(docs, path):
    with open(path, "w") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--maven_dir", default=str(config.MAVEN_DIR))
    args = ap.parse_args()
    src = Path(args.maven_dir).expanduser()
    config.DATA_DIR.mkdir(exist_ok=True)

    valid = load(src / "valid.jsonl", config.MAX_WORDS_EVAL)
    rng = random.Random(config.SEED)
    rng.shuffle(valid)
    dev, test = valid[:config.N_DEV], valid[config.N_DEV:config.N_DEV + config.N_TEST]
    pool = load(src / "train.jsonl", config.MAX_WORDS_POOL)

    dump(dev, config.DATA_DIR / "dev.jsonl")
    dump(test, config.DATA_DIR / "test.jsonl")
    dump(pool, config.DATA_DIR / "pool.jsonl")
    st = {"dev": stats(dev), "test": stats(test), "pool": stats(pool)}
    with open(config.DATA_DIR / "stats.json", "w") as f:
        json.dump(st, f, indent=2)
    for k, v in st.items():
        print(f"{k:5s} docs={v['documents']:4d} words/doc={v['avg_words']:6.1f} "
              f"events={v['events']:5d} triggers={v['trigger_mentions']:5d} args={v['arguments']:5d}")


if __name__ == "__main__":
    main()
