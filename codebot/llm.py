"""Talk to an OpenAI-compatible chat API (Groq by default) with the standard library only.

Settings (dashboard > Settings > AI): ai_api_key, ai_base_url, ai_model.
The key can also come from the GROQ_API_KEY environment variable.
"""

import json
import os
import time
import urllib.error
import urllib.request

DEFAULT_BASE = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "llama-3.3-70b-versatile"
SUGGESTED_MODELS = [
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-120b",
    "moonshotai/kimi-k2-instruct",
    "qwen/qwen3-32b",
    "llama-3.1-8b-instant",
]


class LLMError(RuntimeError):
    pass


class LLM:
    def __init__(self, api_key="", base_url=DEFAULT_BASE, model=DEFAULT_MODEL, timeout=90):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self.base_url = (base_url or DEFAULT_BASE).rstrip("/")
        self.model = model or DEFAULT_MODEL
        self.timeout = timeout
        self.usage = {"prompt": 0, "completion": 0, "calls": 0}

    @classmethod
    def from_config(cls, cfg):
        return cls(getattr(cfg, "ai_api_key", ""), getattr(cfg, "ai_base_url", DEFAULT_BASE),
                   getattr(cfg, "ai_model", DEFAULT_MODEL))

    @property
    def ready(self):
        return bool(self.api_key)

    def _request(self, path, payload=None):
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.base_url + path, data=data, method="POST" if data else "GET", headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "invotech360",
        })
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", "replace")
                try:
                    message = json.loads(body)["error"]["message"]
                except (ValueError, KeyError, TypeError):
                    message = body[:300]
                if exc.code in (429, 500, 502, 503) and attempt < 3:
                    wait = float(exc.headers.get("retry-after") or 2 * (attempt + 1))
                    time.sleep(min(30.0, wait))
                    continue
                if exc.code == 401:
                    raise LLMError("The AI key was refused - check it in Settings > AI") from None
                # some models produce a tool call the API can't parse: report it, the agent retries
                raise LLMError(f"AI service error {exc.code}: {message}") from None
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt < 3:
                    time.sleep(2 * (attempt + 1))
                    continue
                raise LLMError(f"Can't reach the AI service ({exc})") from None
        raise LLMError("AI service busy, try again")

    def models(self):
        data = self._request("/models")
        return sorted(m["id"] for m in data.get("data", []))

    def chat(self, messages, tools=None, temperature=0.2, max_tokens=4096, model=None):
        """One completion. Returns the assistant message dict (content and/or tool_calls)."""
        if not self.ready:
            raise LLMError("No AI key yet - add your Groq API key in Settings > AI")
        payload = {"model": model or self.model, "messages": messages,
                   "temperature": temperature, "max_tokens": max_tokens}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        data = self._request("/chat/completions", payload)
        usage = data.get("usage") or {}
        self.usage["prompt"] += usage.get("prompt_tokens", 0)
        self.usage["completion"] += usage.get("completion_tokens", 0)
        self.usage["calls"] += 1
        return data["choices"][0]["message"]
