"""
client.py — LLM client factory.

Auto-detects provider from environment variables.
Returns (client_object, provider_name).
"""

import os
from typing import Any


def get_client(provider: str = None) -> tuple[Any, str]:
    """Return (client, provider_name). Raises if no key found."""
    detected = provider or _detect()
    if detected == "anthropic":
        return _anthropic_client(), "anthropic"
    if detected == "openai":
        return _openai_client(), "openai"
    raise RuntimeError(
        "No LLM provider found.\n"
        "Set ANTHROPIC_API_KEY or OPENAI_API_KEY and try again."
    )


def call(client: Any, provider: str, system: str, user: str, max_tokens: int = 1500) -> str:
    """Unified LLM call that works with both providers."""
    if provider == "anthropic":
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return msg.content[0].text

    if provider == "openai":
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=max_tokens,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        )
        return resp.choices[0].message.content

    raise ValueError(f"Unknown provider: {provider}")


def _detect() -> str | None:
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    return None


def _anthropic_client():
    try:
        import anthropic
        return anthropic.Anthropic()
    except ImportError:
        raise RuntimeError("Run: pip install 'promptiq[anthropic]'")


def _openai_client():
    try:
        import openai
        return openai.OpenAI()
    except ImportError:
        raise RuntimeError("Run: pip install 'promptiq[openai]'")


def parse_json(raw: str) -> dict:
    """Strip markdown fences and parse JSON safely."""
    import json
    text = raw.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1]
        if text.startswith("json"):
            text = text[4:]
    try:
        return json.loads(text.strip())
    except Exception as e:
        raise RuntimeError(f"LLM returned invalid JSON:\n{raw[:300]}\n\nError: {e}")
