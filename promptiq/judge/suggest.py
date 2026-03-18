"""
Stage 4 — Auto-Improvement.

Takes the prompt + its static score and returns:
- An improved version that addresses the specific weaknesses found
- A changelog explaining every change made
- Expected quality gain

This is the feature that turns PromptIQ from a measurement tool
into a co-pilot for prompt engineering.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from .static  import StaticScore
from .client  import call, parse_json


def _build_system(static: StaticScore) -> str:
    weaknesses_str = "\n".join(f"  - {w}" for w in static.weaknesses) or "  - None identified"
    return f"""You are a world-class prompt engineer.

You will receive a prompt that has been evaluated with these specific weaknesses:
{weaknesses_str}

The weakest scoring dimensions are:
  - Clarity:        {static.clarity}/10
  - Specificity:    {static.specificity}/10
  - Conciseness:    {static.conciseness}/10
  - Instruction Q:  {static.instruction_q}/10
  - Robustness:     {static.robustness}/10

Your task:
1. Rewrite the prompt to address EACH weakness directly
2. Do NOT change the prompt's core purpose or persona
3. Preserve what's already working (strengths)
4. List each specific change you made and why (be concrete)
5. Estimate the quality gain per weak dimension

Return ONLY valid JSON:
{{
  "improved": "the full improved prompt text",
  "changes": [
    "Changed X to Y because Z",
    "Added X to fix Y weakness",
    "Removed X which caused Y issue"
  ],
  "expected_gain": "e.g. +2 pts specificity, +1 pt robustness"
}}"""


@dataclass
class SuggestResult:
    original: str
    improved: str
    changes: list[str]
    expected_gain: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "SuggestResult":
        return cls(**d)


def suggest_improvement(
    prompt_content: str,
    static: StaticScore,
    client_tuple,
) -> SuggestResult:
    # Only suggest if there's meaningful room for improvement
    if static.overall >= 9.0:
        return SuggestResult(
            original      = prompt_content,
            improved      = prompt_content,
            changes       = ["No improvements needed — score is already exceptional."],
            expected_gain = "0 pts — already at peak quality",
        )

    client, provider = client_tuple
    system = _build_system(static)
    raw    = call(client, provider, system, f"Prompt to improve:\n\n---\n{prompt_content}\n---", max_tokens=2000)
    data   = parse_json(raw)

    return SuggestResult(
        original      = prompt_content,
        improved      = data.get("improved",      prompt_content),
        changes       = data.get("changes",       []),
        expected_gain = data.get("expected_gain", ""),
    )
