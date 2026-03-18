"""
judge/ — The 4-stage intelligent evaluation engine.

Stage 1 — static_analysis : score the prompt text (clarity, specificity, etc.)
Stage 2 — output_eval     : run the prompt on an LLM, score the actual output
Stage 3 — compare         : compare to previous version, declare winner + regressions
Stage 4 — suggest         : return an auto-improved version with change list

Each stage is independent and can be called alone.
The orchestrate() function runs all four and returns a FullJudgeResult.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Optional

from .static  import static_analysis, StaticScore
from .runner  import output_eval, OutputEval
from .compare import compare_versions, CompareResult
from .suggest import suggest_improvement, SuggestResult
from .client  import get_client


@dataclass
class FullJudgeResult:
    static:     StaticScore
    outputs:    list[OutputEval]
    compare:    Optional[CompareResult]
    suggestion: Optional[SuggestResult]
    provider:   str
    overall_score: float          # 0–10 composite

    def to_dict(self) -> dict:
        return {
            "static":        self.static.to_dict(),
            "outputs":       [o.to_dict() for o in self.outputs],
            "compare":       self.compare.to_dict() if self.compare else None,
            "suggestion":    self.suggestion.to_dict() if self.suggestion else None,
            "provider":      self.provider,
            "overall_score": self.overall_score,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "FullJudgeResult":
        from .static  import StaticScore
        from .runner  import OutputEval
        from .compare import CompareResult
        from .suggest import SuggestResult
        return cls(
            static        = StaticScore.from_dict(d["static"]),
            outputs       = [OutputEval.from_dict(o) for o in d.get("outputs", [])],
            compare       = CompareResult.from_dict(d["compare"]) if d.get("compare") else None,
            suggestion    = SuggestResult.from_dict(d["suggestion"]) if d.get("suggestion") else None,
            provider      = d.get("provider", ""),
            overall_score = d.get("overall_score", 0),
        )


def orchestrate(
    prompt_content: str,
    test_inputs: list[str] = None,
    previous_content: str = None,
    auto_suggest: bool = True,
    provider: str = None,
    progress_cb=None,          # called with (stage_name, done: bool)
) -> FullJudgeResult:
    """
    Run all 4 judge stages.

    progress_cb(stage, done) is called before and after each stage
    so the CLI can show a live progress indicator.
    """
    def _prog(stage, done=False):
        if progress_cb:
            progress_cb(stage, done)

    client, detected_provider = get_client(provider)

    # ── Stage 1: Static Analysis ──────────────────────────────────────────────
    _prog("static_analysis")
    static = static_analysis(prompt_content, client)
    _prog("static_analysis", done=True)

    # ── Stage 2: Output Evaluation ────────────────────────────────────────────
    outputs: list[OutputEval] = []
    if test_inputs:
        for i, inp in enumerate(test_inputs):
            _prog(f"output_eval:{i+1}/{len(test_inputs)}")
            ev = output_eval(prompt_content, inp, client)
            outputs.append(ev)
            _prog(f"output_eval:{i+1}/{len(test_inputs)}", done=True)

    # ── Stage 3: Compare ──────────────────────────────────────────────────────
    compare: Optional[CompareResult] = None
    if previous_content:
        _prog("compare")
        compare = compare_versions(previous_content, prompt_content, client)
        _prog("compare", done=True)

    # ── Stage 4: Suggest ──────────────────────────────────────────────────────
    suggestion: Optional[SuggestResult] = None
    if auto_suggest:
        _prog("suggest")
        suggestion = suggest_improvement(prompt_content, static, client)
        _prog("suggest", done=True)

    # ── Composite score ───────────────────────────────────────────────────────
    overall = _compute_overall(static, outputs, compare)

    return FullJudgeResult(
        static        = static,
        outputs       = outputs,
        compare       = compare,
        suggestion    = suggestion,
        provider      = detected_provider,
        overall_score = overall,
    )


def _compute_overall(
    static: StaticScore,
    outputs: list[OutputEval],
    compare: Optional[CompareResult],
) -> float:
    """
    Weighted composite score:
      50% static overall
      35% output quality (average across test inputs)
      15% compare delta bonus (if compared to previous)
    """
    score = static.overall * 0.50

    if outputs:
        avg_output = sum(o.quality for o in outputs) / len(outputs)
        score += avg_output * 0.35
    else:
        # No test inputs — redistribute weight to static
        score = static.overall * 0.85

    if compare and compare.delta > 0:
        # Small bonus for improving over previous version (max 1.5 pts)
        score += min(compare.delta * 0.15, 1.5)

    return round(min(score, 10.0), 1)
