"""
Stage 1 — Static Analysis.
Scores the prompt text itself across 5 dimensions.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from .client import call, parse_json


SYSTEM = """You are a world-class prompt engineer who evaluates LLM system prompts.

Score the prompt on exactly 5 dimensions (each 0–10):

1. clarity          — Is it unambiguous? Would two engineers interpret it identically?
2. specificity      — Are instructions concrete and actionable, not vague?
3. conciseness      — Free of redundancy and filler? Every word earns its place?
4. instruction_q    — How precisely does it guide model behavior toward the goal?
5. robustness       — Does it handle edge cases, off-topic requests, and failure modes?

Rules:
- Be brutally honest. A score of 10 is exceptional and rare.
- Scores below 5 mean a real, fixable problem exists.
- Quote SPECIFIC phrases (under 10 words) when noting weaknesses.
- strengths: 2–3 items. weaknesses: 2–3 items. Be concrete.

Return ONLY valid JSON (no markdown fences, no preamble):
{
  "clarity": int,
  "specificity": int,
  "conciseness": int,
  "instruction_q": int,
  "robustness": int,
  "feedback": "2-3 sentences of actionable feedback",
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."]
}"""


@dataclass
class StaticScore:
    clarity: int
    specificity: int
    conciseness: int
    instruction_q: int
    robustness: int
    overall: float        # weighted
    feedback: str
    strengths: list[str]
    weaknesses: list[str]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "StaticScore":
        return cls(**d)


def static_analysis(prompt_content: str, client_tuple) -> StaticScore:
    """
    client_tuple = (client_obj, provider_str)
    returned by judge.client.get_client()
    """
    client, provider = client_tuple
    raw  = call(client, provider, SYSTEM, f"Evaluate this prompt:\n\n---\n{prompt_content}\n---")
    data = parse_json(raw)

    scores = [
        data.get("clarity",       0),
        data.get("specificity",   0),
        data.get("conciseness",   0),
        data.get("instruction_q", 0),
        data.get("robustness",    0),
    ]
    # instruction_q and robustness count double
    overall = round(
        (scores[0] + scores[1] + scores[2] + scores[3] * 1.5 + scores[4] * 1.5) / 6.0,
        1
    )

    return StaticScore(
        clarity       = int(data.get("clarity",       0)),
        specificity   = int(data.get("specificity",   0)),
        conciseness   = int(data.get("conciseness",   0)),
        instruction_q = int(data.get("instruction_q", 0)),
        robustness    = int(data.get("robustness",    0)),
        overall       = overall,
        feedback      = data.get("feedback",  ""),
        strengths     = data.get("strengths", []),
        weaknesses    = data.get("weaknesses", []),
    )
