"""LLM abstraction: one call() for Anthropic + every OpenAI-compatible endpoint (OpenAI, DeepSeek, Zhipu, Doubao/Ark, Moonshot, Ollama).
stdlib only (urllib). Keys from env. Routes + budget from config/llm.json. Disk cache keyed by (provider, model, prompt)."""
import json, os, hashlib, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "config/llm.json").read_text())

class LLMError(RuntimeError): pass

def _post(url, headers, body, timeout=120):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r: return json.loads(r.read())

def _call_anthropic(p, system, prompt, max_tokens):
    key = os.environ.get(p["env_key"] or ""); 
    if not key: raise LLMError(f"missing {p['env_key']}")
    r = _post("https://api.anthropic.com/v1/messages", {"x-api-key": key, "anthropic-version": "2023-06-01"},
              {"model": p["model"], "max_tokens": max_tokens, "system": system, "messages": [{"role": "user", "content": prompt}]})
    return "".join(b.get("text", "") for b in r["content"]), r.get("usage", {})

def _call_openai(p, system, prompt, max_tokens):
    key = os.environ.get(p["env_key"]) if p.get("env_key") else "ollama"
    if not key: raise LLMError(f"missing {p['env_key']}")
    r = _post(p["base_url"].rstrip("/") + "/chat/completions", {"Authorization": f"Bearer {key}"},
              {"model": p["model"], "max_tokens": max_tokens, "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}]})
    return r["choices"][0]["message"]["content"], r.get("usage", {})

def call(task, prompt, system="You are a precise assistant. Answer with only what is asked.", max_tokens=2000, provider=None):
    """Try the route's providers in order; return text. Cached on disk."""
    chain = [provider] if provider else CFG["routes"].get(task, ["anthropic"])
    if len(prompt) > CFG["budget"]["max_input_tokens_per_call"] * 3:
        raise LLMError(f"prompt too long for task {task}: send a summary/index, not raw data (see config/llm.json budget)")
    cache = ROOT / CFG["budget"]["cache_dir"]; cache.mkdir(parents=True, exist_ok=True)
    errs = []
    for name in chain:
        p = CFG["providers"][name]
        key = hashlib.sha256(f"{name}|{p['model']}|{system}|{prompt}".encode()).hexdigest()[:24]
        hit = cache / f"{key}.json"
        if hit.exists(): return json.loads(hit.read_text())["text"]
        try:
            fn = _call_anthropic if p["kind"] == "anthropic" else _call_openai
            text, usage = fn(p, system, prompt, max_tokens)
            hit.write_text(json.dumps({"provider": name, "model": p["model"], "text": text, "usage": usage}, ensure_ascii=False))
            with open(ROOT / CFG["budget"]["log_usage_to"], "a") as f:
                f.write(json.dumps({"t": time.time(), "task": task, "provider": name, "usage": usage}) + "\n")
            return text
        except Exception as e: errs.append(f"{name}: {e}")
    raise LLMError("all providers failed: " + "; ".join(errs))

if __name__ == "__main__":
    import sys; print(call(sys.argv[1], sys.argv[2]))
