"""
Stage 2 — Output Evaluation.

Actually sends the prompt + test_input to an LLM, captures the output,
then sends that output to a judge model for quality assessment.

This is what no other local tool does — we test real behavior, not theory.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from .client import call, parse_json


RUN_SYSTEM = "You are a helpful AI assistant. Follow the system prompt provided."

JUDGE_SYSTEM = """You are an expert evaluator of LLM outputs.

You will receive:
1. A system prompt (the instructions given to the model)
2. A user input (the test case)
3. The model's output (what the model actually produced)

Evaluate the output on 3 dimensions (each 0–10):

1. relevance         — Did the output actually address the user's input?
2. instruction_follow— Did the model follow ALL instructions in the system prompt?
3. quality           — Is the output accurate, well-structured, and useful?

Also list specific issues found (empty list if none).
Write a one-sentence verdict.

Return ONLY valid JSON:
{
  "relevance": int,
  "instruction_follow": int,
  "quality": int,
  "issues": ["specific issue 1", "specific issue 2"],
  "verdict": "one sentence"
}"""


@dataclass
class OutputEval:
    test_input: str
    raw_output: str
    relevance: int
    instruction_follow: int
    quality: int
    issues: list[str]
    verdict: str

    @property
    def avg_score(self) -> float:
        return round((self.relevance + self.instruction_follow + self.quality) / 3.0, 1)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "OutputEval":
        return cls(**d)


def output_eval(prompt_content: str, test_input: str, client_tuple) -> OutputEval:
    """Run prompt on test_input, then judge the output."""
    client, provider = client_tuple

    # ── Step 1: Run the prompt ────────────────────────────────────────────────
    raw_output = call(
        client, provider,
        system     = prompt_content,
        user       = test_input,
        max_tokens = 800,
    )

    # ── Step 2: Judge the output ──────────────────────────────────────────────
    judge_input = (
        f"System prompt:\n---\n{prompt_content}\n---\n\n"
        f"User input:\n---\n{test_input}\n---\n\n"
        f"Model output:\n---\n{raw_output}\n---"
    )
    raw_eval = call(client, provider, JUDGE_SYSTEM, judge_input)
    data     = parse_json(raw_eval)

    return OutputEval(
        test_input          = test_input,
        raw_output          = raw_output,
        relevance           = int(data.get("relevance",           0)),
        instruction_follow  = int(data.get("instruction_follow",  0)),
        quality             = int(data.get("quality",             0)),
        issues              = data.get("issues",  []),
        verdict             = data.get("verdict", ""),
    )
