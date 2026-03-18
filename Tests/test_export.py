"""
tests/test_export.py — Full test coverage for export.py
"""

import json
import tempfile
from pathlib import Path

import pytest
import promptiq.store as store
from promptiq import export as exp


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "PROMPTIQ_DIR", tmp_path / ".promptiq")
    monkeypatch.setattr(store, "PROMPTS_DIR",  tmp_path / ".promptiq" / "prompts")


def _make_full_prompt(name="testprompt"):
    """Create a prompt with a judge result for richer export testing."""
    store.commit(name, "You are a helpful assistant.", "initial draft")
    store.commit(name, "You are an expert assistant. Be concise.", "improved",
                 model="gpt-4", tags=["prod"],
                 judge_result={
                     "static": {
                         "clarity": 8, "specificity": 7, "conciseness": 9,
                         "instruction_q": 8, "robustness": 7,
                         "overall": 7.8, "feedback": "Good prompt.",
                         "strengths": ["Clear persona"], "weaknesses": ["No format spec"],
                     },
                     "outputs": [{
                         "test_input": "Explain AI",
                         "raw_output": "AI is...",
                         "relevance": 9, "instruction_follow": 8, "quality": 8,
                         "issues": [], "verdict": "Good output"
                     }],
                     "compare": {
                         "winner": "b", "score_a": 6.0, "score_b": 7.8,
                         "delta": 1.8, "reasoning": "B is more specific.",
                         "improvements": ["Added conciseness"], "regressions": [],
                     },
                     "suggestion": {
                         "original": "...", "improved": "...",
                         "changes": ["Made it more specific"], "expected_gain": "+1 pt"
                     },
                     "provider": "anthropic",
                     "overall_score": 7.8,
                 })
    return store.raw(name)


# ── export_json ───────────────────────────────────────────────────────────────

def test_export_json_creates_file(tmp_path):
    data = _make_full_prompt()
    out  = str(tmp_path / "out.json")
    exp.export_json(data, out)
    assert Path(out).exists()


def test_export_json_valid_json(tmp_path):
    data = _make_full_prompt()
    out  = str(tmp_path / "out.json")
    exp.export_json(data, out)
    parsed = json.loads(Path(out).read_text())
    assert isinstance(parsed, dict)


def test_export_json_has_required_keys(tmp_path):
    data = _make_full_prompt()
    out  = str(tmp_path / "out.json")
    exp.export_json(data, out)
    parsed = json.loads(Path(out).read_text())
    assert "name"        in parsed
    assert "branches"    in parsed
    assert "exported_at" in parsed


def test_export_json_preserves_content(tmp_path):
    data = _make_full_prompt("myprompt")
    out  = str(tmp_path / "out.json")
    exp.export_json(data, out)
    parsed = json.loads(Path(out).read_text())
    assert parsed["name"] == "myprompt"
    commits = parsed["branches"]["main"]
    assert any("helpful" in c["content"] for c in commits)


def test_export_json_default_filename():
    store.commit("autoprompt", "content", "v1")
    data = store.raw("autoprompt")
    out  = exp.export_json(data)
    assert Path(out).exists()
    Path(out).unlink()


# ── export_markdown ───────────────────────────────────────────────────────────

def test_export_markdown_creates_file(tmp_path):
    data = _make_full_prompt()
    out  = str(tmp_path / "out.md")
    exp.export_markdown(data, out)
    assert Path(out).exists()


def test_export_markdown_contains_name(tmp_path):
    data = _make_full_prompt("myprompt")
    out  = str(tmp_path / "out.md")
    exp.export_markdown(data, out)
    content = Path(out).read_text()
    assert "myprompt" in content


def test_export_markdown_contains_commit_messages(tmp_path):
    data = _make_full_prompt()
    out  = str(tmp_path / "out.md")
    exp.export_markdown(data, out)
    content = Path(out).read_text()
    assert "initial draft" in content
    assert "improved"      in content


def test_export_markdown_contains_scores(tmp_path):
    data = _make_full_prompt()
    out  = str(tmp_path / "out.md")
    exp.export_markdown(data, out)
    content = Path(out).read_text()
    assert "7.8" in content


def test_export_markdown_contains_prompt_content(tmp_path):
    data = _make_full_prompt()
    out  = str(tmp_path / "out.md")
    exp.export_markdown(data, out)
    content = Path(out).read_text()
    assert "helpful assistant" in content


def test_export_markdown_contains_strengths_weaknesses(tmp_path):
    data = _make_full_prompt()
    out  = str(tmp_path / "out.md")
    exp.export_markdown(data, out)
    content = Path(out).read_text()
    assert "Clear persona"  in content
    assert "No format spec" in content


# ── export_score_report ───────────────────────────────────────────────────────

def test_export_score_report_creates_file(tmp_path):
    data = _make_full_prompt()
    out  = str(tmp_path / "scores.md")
    exp.export_score_report(data, out)
    assert Path(out).exists()


def test_export_score_report_contains_table(tmp_path):
    data = _make_full_prompt()
    out  = str(tmp_path / "scores.md")
    exp.export_score_report(data, out)
    content = Path(out).read_text()
    assert "|" in content  # markdown table


def test_export_score_report_contains_overall_score(tmp_path):
    data = _make_full_prompt()
    out  = str(tmp_path / "scores.md")
    exp.export_score_report(data, out)
    content = Path(out).read_text()
    assert "7.8" in content


def test_export_score_report_shows_trend(tmp_path):
    data = _make_full_prompt()
    out  = str(tmp_path / "scores.md")
    exp.export_score_report(data, out)
    content = Path(out).read_text()
    # Should show trend arrow
    assert any(sym in content for sym in ["📈", "📉", "➡️"])


def test_export_empty_prompt_no_crash(tmp_path):
    store.commit("empty", "no judge", "v1")
    data = store.raw("empty")
    out  = str(tmp_path / "empty.md")
    exp.export_score_report(data, out)  # should not raise
    assert Path(out).exists()
