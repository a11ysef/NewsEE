import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RUNS_DIR = ROOT / "runs"
CACHE_DIR = ROOT / ".cache"

# Where the raw MAVEN-Arg files (train.jsonl / valid.jsonl) live.
MAVEN_DIR = Path(os.environ.get("MAVEN_DIR", "~/Downloads/MAVEN-Arg")).expanduser()

SEED = 42
N_DEV = 30          # documents used for prompt development / debugging
N_TEST = 120        # documents used for the reported results
MAX_WORDS_EVAL = 600  # skip very long documents to keep cost predictable
MAX_WORDS_POOL = 400  # shorter documents make better few-shot demonstrations

# OpenAI-compatible endpoints. Keys are read from .env
PROVIDERS = {
    "deepseek": {"base_url": "https://api.deepseek.com", "key_env": "DEEPSEEK_API_KEY"},
    "zhipu": {"base_url": "https://open.bigmodel.cn/api/paas/v4", "key_env": "ZHIPU_API_KEY"},
    "ollama": {"base_url": "http://localhost:11434/v1", "key_env": None},
}

# short name -> (provider, model id, extra request body).
# DeepSeek models think by default; in thinking mode temperature is ignored, which
# breaks reproducibility, so the main experiments switch thinking off.
_NO_THINK = {"thinking": {"type": "disabled"}}
_THINK = {"thinking": {"type": "enabled"}}
MODELS = {
    "glm-flash": ("zhipu", "glm-4-flash", {}),
    # Zhipu resource packs: glm-4.5-air (12M tokens) and glm-4.7 (5M) + 8.9M general tokens
    "glm-air": ("zhipu", "glm-4.5-air", _NO_THINK),
    "glm-4.7": ("zhipu", "glm-4.7", _NO_THINK),
    "ds-flash": ("deepseek", "deepseek-flash", _NO_THINK),
    "ds-pro": ("deepseek", "deepseek-v4-pro", _NO_THINK),
    "ds-flash-think": ("deepseek", "deepseek-flash", _THINK),  # optional extra experiment
    "qwen3b": ("ollama", "qwen2.5:3b", {}),
}

MAX_TOKENS = 8192

# DeepSeek list prices, RMB per million tokens: ((input, output) peak, (input, output) off-peak).
# Peak = Beijing time weekdays 09-12 and 14-18. Cache-miss input prices, so costs are upper bounds.
# Zhipu runs used prepaid resource packs and are reported in tokens only.
PRICES = {"ds-flash": ((2, 8), (1, 4)), "ds-flash-think": ((2, 8), (1, 4)), "ds-pro": ((9, 27), (4.5, 13.5))}
# Thinking models spend output tokens on reasoning before the answer: give them more room
MAX_TOKENS_BY_MODEL = {"ds-flash-think": 32768}

# Some models have low rate limits on this account: cap parallel requests per model
MAX_WORKERS = {"glm-4.7": 1, "ds-pro": 2}
