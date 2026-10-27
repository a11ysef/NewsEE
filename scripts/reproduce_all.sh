#!/usr/bin/env bash
# Re-runs every reported experiment in order. With .cache/ present this makes no API calls.
# Without it, the DeepSeek runs cost roughly 50 RMB in total (see README).
set -e
cd "$(dirname "$0")/.."
python scripts/prepare_data.py
python scripts/evaluate.py --oracle --gold data/dev.jsonl

# development set: ablation and demonstration count
for m in ds-flash glm-air; do python scripts/run_ablation.py --model $m --split dev; done
python scripts/run_ablation.py --model glm-air --split dev --shots 0,1,3,5

# test set: main results (baseline, framework, gold triggers)
for m in ds-flash glm-4.7 ds-pro glm-air; do python scripts/run_main.py --model $m; done
python scripts/run_unseen.py --model glm-air
python scripts/run_main.py --model ds-flash-think --skip-goldtrig
python scripts/run_repeat.py --model ds-flash --runs 2

# analysis (no API calls)
python scripts/run_lexicon.py --split test
python scripts/compare_lexicon.py --split test
python scripts/run_lexicon.py --split dev
python scripts/run_hybrid.py --split dev
python scripts/run_hybrid.py --split test
python scripts/summarize.py
python scripts/cost_analysis.py
for m in ds-flash glm-4.7 ds-pro glm-air; do python scripts/error_analysis.py --model $m; done
python scripts/verify_results.py
