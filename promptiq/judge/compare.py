"""
Stage 3 — Version Comparison.

Compares two versions of a prompt head-to-head:
- Which is better overall?
- What specifically improved?
- What regressed?
- What's the quality delta?
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from .client import call, parse_json


SYSTEM = """You are an expert prompt engineer comparing two versions of a system prompt.

Version A is the OLD version. Version B is the NEW version.

Analyze them carefully and answer:
1. Which is better overall? ("a", "b", or "tie")
2. Estimated quality score for A (0–10)
3. Estimated quality score for B (0–10)
4. Your reasoning (2–3 sentences, specific, cite actual phrases)
5. Improvements in B (what got better — be specific, empty list if none)
6. Regressions in B (what got worse — be specific, empty list if none)

Return ONLY valid JSON:
{
  "winner": "a" | "b" | "tie",
  "score_a": float,
  "score_b": float,
  "reasoning": "2-3 sentences",
  "improvements": ["...", "..."],
  "regressions": ["...", "..."]
}"""


@dataclass
class CompareResult:
    winner: str              # "a" | "b" | "tie"
    score_a: float
    score_b: float
    delta: float             # score_b - score_a
    reasoning: str
    improvements: list[str]
    regressions: list[str]

    @property
    def winner_label(self) -> str:
        if self.winner == "b":  return "New version wins ✓"
        if self.winner == "a":  return "Old version wins ✗"
        return "Tie —"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "CompareResult":
        return cls(**d)


def compare_versions(content_a: str, content_b: str, client_tuple) -> CompareResult:
    client, provider = client_tuple
    user = (
        f"VERSION A (old):\n---\n{content_a}\n---\n\n"
        f"VERSION B (new):\n---\n{content_b}\n---"
    )
    raw  = call(client, provider, SYSTEM, user)
    data = parse_json(raw)

    score_a = float(data.get("score_a", 5.0))
    score_b = float(data.get("score_b", 5.0))

    return CompareResult(
        winner       = data.get("winner",       "tie"),
        score_a      = score_a,
        score_b      = score_b,
        delta        = round(score_b - score_a, 1),
        reasoning    = data.get("reasoning",    ""),
        improvements = data.get("improvements", []),
        regressions  = data.get("regressions",  []),
    )
