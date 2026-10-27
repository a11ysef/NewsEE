"""Unseen event types (RQ3): can the framework handle event types it never saw an example of?

One type per news theme is held out: every demonstration hides its triggers and no argument
demonstrations are given for it; the model only gets its definition from the guidelines.
We compare held-out types with the normal (all types seen) framework run.

  python scripts/run_unseen.py --model glm-air
  python scripts/run_unseen.py --model glm-air --split dev
"""
import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee import config  # noqa: E402
from newsee.framework import FINAL  # noqa: E402
from newsee.io_utils import read_jsonl  # noqa: E402
from newsee.llm import LLM  # noqa: E402
from newsee.runner import run_framework  # noqa: E402
from newsee.schema import EVENT_TYPES  # noqa: E402
from newsee.scorer import score, score_by_type  # noqa: E402
from newsee.stats import paired_bootstrap, restrict_types  # noqa: E402


HELD_OUT = ("Conquering", "Bodily_harm", "Damaging", "Change_of_leadership")  # one per theme
SEEN = tuple(t for t in EVENT_TYPES if t not in HELD_OUT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=list(config.MODELS))
    ap.add_argument("--split", default="test", choices=["dev", "test"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    llm = LLM(a.model)
    golds = read_jsonl(config.DATA_DIR / f"{a.split}.jsonl")[: a.limit]
    _, _, out_seen = run_framework(llm, FINAL, a.split, a.limit, a.workers)
    _, info_u, out_unseen = run_framework(llm, replace(FINAL, unseen=HELD_OUT), a.split, a.limit, a.workers)
    p_seen = read_jsonl(out_seen / "predictions.jsonl")
    p_unseen = read_jsonl(out_unseen / "predictions.jsonl")

    lines = [f"# Unseen event types: {a.model} on {a.split} ({len(golds)} documents)", "",
             f"Held out (no examples, definition only): {', '.join(HELD_OUT)}", "",
             "| group | Trig-C all seen | Trig-C held out | diff | 95% CI | Arg-C all seen | Arg-C held out | diff | 95% CI |",
             "|---|---|---|---|---|---|---|---|---|"]
    summary = {"model": a.model, "split": a.split, "held_out": HELD_OUT, "groups": {}}
    for label, types in (("held-out types", HELD_OUT), ("seen types", SEEN)):
        g, ps, pu = restrict_types(golds, types), restrict_types(p_seen, types), restrict_types(p_unseen, types)
        sig = paired_bootstrap(g, ps, pu, metrics=["Trig-C", "Arg-C (EM)"])
        summary["groups"][label] = sig
        t, r = sig["Trig-C"], sig["Arg-C (EM)"]
        lines.append(f"| {label} | {t['A']:.1f} | {t['B']:.1f} | {t['diff']:+.1f} | [{t['lo']:+.1f}, {t['hi']:+.1f}] | "
                     f"{r['A']:.1f} | {r['B']:.1f} | {r['diff']:+.1f} | [{r['lo']:+.1f}, {r['hi']:+.1f}] |")
    bs, bu = score_by_type(golds, p_seen, HELD_OUT), score_by_type(golds, p_unseen, HELD_OUT)
    summary["per_type"] = {"all_seen": bs, "held_out": bu}
    lines += ["", "| held-out type | gold triggers | Trig-C all seen | Trig-C held out | Arg-C all seen | Arg-C held out |",
              "|---|---|---|---|---|---|"]
    for t in HELD_OUT:
        lines.append(f"| {t} | {bs[t]['n_gold_triggers']} | {bs[t]['Trig-C']:.1f} | {bu[t]['Trig-C']:.1f} | "
                     f"{bs[t]['Arg-C (EM)']:.1f} | {bu[t]['Arg-C (EM)']:.1f} |")
    overall = score(golds, p_unseen)
    lines += ["", f"Overall with held-out setting: Trig-C {overall['Trig-C']['F1']}, Arg-C {overall['Arg-C (EM)']['F1']}",
              f"Blocked by filter: {info_u['usage'].get('filtered', 0)}"]
    out_dir = config.ROOT / "results"
    out_dir.mkdir(exist_ok=True)
    stem = out_dir / (f"unseen_{a.model}_{a.split}" + (f"_n{a.limit}" if a.limit else ""))
    Path(f"{stem}.md").write_text("\n".join(lines) + "\n")
    Path(f"{stem}.json").write_text(json.dumps(summary, indent=2))
    print("\n" + "\n".join(lines))
    print(f"\nsaved {stem}.md / .json")


if __name__ == "__main__":
    main()
