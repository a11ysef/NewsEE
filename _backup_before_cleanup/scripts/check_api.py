"""Check that each API key in .env works (sends one tiny request per model).

  python scripts/check_api.py              # check every configured model
  python scripts/check_api.py glm-flash    # check one

For Zhipu it also tries the international endpoint (api.z.ai), because a key
created on z.ai does not work on open.bigmodel.cn and vice versa.
Key values are never printed.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import httpx
from openai import OpenAI  # noqa: E402

from newsee import config  # noqa: E402
from newsee.llm import load_env  # noqa: E402

ZHIPU_ENDPOINTS = ["https://open.bigmodel.cn/api/paas/v4", "https://api.z.ai/api/paas/v4"]


def try_call(base_url, key, model, extra=None):
    try:
        local = "localhost" in base_url
        c = OpenAI(api_key=key, base_url=base_url, timeout=60, max_retries=0,
                   http_client=httpx.Client(trust_env=False, timeout=120) if local else None)
        r = c.chat.completions.create(model=model, max_tokens=20, extra_body=extra or None,
                                      messages=[{"role": "user", "content": "Reply OK"}])
        return True, (r.choices[0].message.content or "").strip()
    except Exception as e:  # noqa: BLE001
        return False, f"{getattr(e, 'status_code', '')} {str(e)[:200]}"


def describe_key(key):
    if not key:
        return "EMPTY"
    k = key.strip()
    notes = [f"length {len(k)}"]
    if k != key:
        notes.append("has leading/trailing spaces")
    if k[:1] in "\"'":
        notes.append("wrapped in quotes")
    return ", ".join(notes)


def main():
    load_env()
    names = sys.argv[1:] or list(config.MODELS)
    for name in names:
        provider, model, extra = config.MODELS[name]
        p = config.PROVIDERS[provider]
        key = os.environ.get(p["key_env"], "") if p["key_env"] else "ollama"
        print(f"\n== {name}  ({provider} / {model})")
        if p["key_env"]:
            print(f"   {p['key_env']}: {describe_key(key)}")
            if not key:
                continue
        bases = ZHIPU_ENDPOINTS if provider == "zhipu" else [p["base_url"]]
        for base in bases:
            ok, msg = try_call(base, key.strip(), model, extra)
            print(f"   {'OK  ' if ok else 'FAIL'} {base}  ->  {msg}")


if __name__ == "__main__":
    main()
