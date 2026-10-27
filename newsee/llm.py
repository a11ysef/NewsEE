"""Thin wrapper around OpenAI-compatible chat APIs (DeepSeek, Zhipu GLM, Ollama).

Every reply is cached on disk, keyed by model + messages + parameters, so re-running
an experiment costs nothing and reproduces the same outputs exactly.
"""
import hashlib
import json
import os
import threading
import time

import httpx
from openai import OpenAI

from . import config


def load_env():
    path = config.ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            # .env wins over variables already set in the shell (an old key exported in
            # ~/.zshrc would otherwise silently take priority)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")


class LLM:
    def __init__(self, name, temperature=0.0, max_tokens=config.MAX_TOKENS, json_mode=True, seed=config.SEED,
                 cache_tag=""):
        # cache_tag: a separate cache for repeated independent runs (stability check)
        load_env()
        if name not in config.MODELS:
            raise ValueError(f"unknown model '{name}', choose from {list(config.MODELS)}")
        provider, self.model, self.extra = config.MODELS[name]
        p = config.PROVIDERS[provider]
        key = os.environ.get(p["key_env"]) if p["key_env"] else "ollama"
        if not key:
            raise RuntimeError(f"{p['key_env']} is not set. Put it in the .env file.")
        # Local Ollama must bypass any system proxy (e.g. V2rayU), otherwise localhost -> 502
        http_client = httpx.Client(trust_env=False, timeout=600) if provider == "ollama" else None
        self.client = OpenAI(api_key=key, base_url=p["base_url"], timeout=180, http_client=http_client)
        self.name, self.provider = name, provider
        max_tokens = config.MAX_TOKENS_BY_MODEL.get(name, max_tokens)
        self.temperature, self.max_tokens, self.seed = temperature, max_tokens, seed
        self.json_mode = json_mode
        self.cache_tag = cache_tag
        self.cache_dir = config.CACHE_DIR / name / cache_tag if cache_tag else config.CACHE_DIR / name
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.usage = {"calls": 0, "cached": 0, "prompt_tokens": 0, "completion_tokens": 0,
                      "reasoning_tokens": 0, "truncated": 0, "empty": 0, "filtered": 0}
        self._lock = threading.Lock()

    def _key(self, messages):
        blob = json.dumps([self.model, self.extra, messages, self.temperature, self.max_tokens, self.json_mode]
                          + ([self.cache_tag] if self.cache_tag else []),
                          ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(blob.encode()).hexdigest()

    def chat(self, messages):
        """Return the reply text (str). Uses the disk cache when possible."""
        path = self.cache_dir / f"{self._key(messages)}.json"
        if path.exists():
            rec = json.loads(path.read_text())
            with self._lock:
                self.usage["cached"] += 1
                if rec.get("filtered"):
                    self.usage["filtered"] += 1
            return rec["text"]

        kwargs = dict(model=self.model, messages=messages, temperature=self.temperature,
                      max_tokens=self.max_tokens)
        if self.provider != "zhipu":
            kwargs["seed"] = self.seed
        if self.json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        if self.extra:
            kwargs["extra_body"] = self.extra

        last_err = None
        for attempt in range(10):  # ~6 minutes of back-off in total, enough for rate limits (429)
            try:
                resp = self.client.chat.completions.create(**kwargs)
                choice = resp.choices[0]
                text = choice.message.content or ""
                u = resp.usage
                with self._lock:
                    self.usage["calls"] += 1
                    if u:
                        self.usage["prompt_tokens"] += u.prompt_tokens or 0
                        self.usage["completion_tokens"] += u.completion_tokens or 0
                        det = getattr(u, "completion_tokens_details", None)
                        self.usage["reasoning_tokens"] += (getattr(det, "reasoning_tokens", 0) or 0) if det else 0
                    if choice.finish_reason == "length":
                        self.usage["truncated"] += 1
                    if not text.strip():
                        self.usage["empty"] += 1
                if not text.strip():
                    return text  # do not cache empty replies, so a re-run tries again
                path.write_text(json.dumps({"model": self.model, "messages": messages, "text": text},
                                           ensure_ascii=False))
                return text
            except Exception as e:  # noqa: BLE001
                last_err = e
                msg = str(e).lower()
                status = getattr(e, "status_code", None)
                if status == 400 and ("1301" in msg or "contentfilter" in msg or "content_filter" in msg
                                      or "sensitive" in msg or "不安全或敏感" in str(e)):
                    # provider safety filter (war / killing news can trigger it): record it as an
                    # empty reply and cache that, so re-runs are identical and cost nothing
                    with self._lock:
                        self.usage["filtered"] += 1
                    path.write_text(json.dumps({"model": self.model, "messages": messages, "text": "",
                                                "filtered": True, "error": str(e)[:300]}, ensure_ascii=False))
                    return ""
                if status in (401, 402, 403, 404):
                    # auth / balance / unknown model: retrying will not help
                    raise RuntimeError(f"{self.name} ({self.model}) error {status}: {e}") from None
                if "response_format" in msg and "response_format" in kwargs:
                    kwargs.pop("response_format")  # provider does not support JSON mode
                    continue
                if "seed" in msg and "seed" in kwargs:
                    kwargs.pop("seed")
                    continue
                time.sleep(min(60, 2 ** attempt * 2))
        raise RuntimeError(f"{self.name} failed after retries: {last_err}")
