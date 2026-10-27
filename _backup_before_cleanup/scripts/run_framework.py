"""Run the NewsEE framework with one configuration.

  python scripts/run_framework.py --model glm-air --split dev --limit 3         # quick check
  python scripts/run_framework.py --model glm-air --split dev                  # full framework
  python scripts/run_framework.py --model glm-air --no-decompose --demos none  # custom switches
  python scripts/run_framework.py --model glm-air --setting gold_trigger       # arguments only
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from newsee import config  # noqa: E402
from newsee.framework import FrameworkConfig  # noqa: E402
from newsee.llm import LLM  # noqa: E402
from newsee.runner import run_framework  # noqa: E402
from newsee.scorer import format_table  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="glm-air", choices=list(config.MODELS))
    ap.add_argument("--split", default="dev", choices=["dev", "test"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--no-decompose", action="store_true")
    ap.add_argument("--no-guidelines", action="store_true")
    ap.add_argument("--demos", default="retrieval", choices=["retrieval", "random", "none"])
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--no-verify", action="store_true")
    ap.add_argument("--setting", default="end2end", choices=["end2end", "gold_trigger"])
    a = ap.parse_args()
    cfg = FrameworkConfig(decompose=not a.no_decompose, guidelines=not a.no_guidelines,
                          demos=a.demos, k=a.k, verify=not a.no_verify, setting=a.setting)
    llm = LLM(a.model)
    res, info, out = run_framework(llm, cfg, a.split, a.limit, a.workers)
    print(format_table(res))
    print(f"LLM calls {info['llm_calls']}, parse failures {info['parse_failures']}, "
          f"removed by verification {info['verification_removed']}")
    print(f"usage {info['usage']}\nsaved to {out}")


if __name__ == "__main__":
    main()
