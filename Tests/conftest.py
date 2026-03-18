"""
conftest.py — Shared pytest fixtures for PromptIQ tests.
"""

import tempfile
from pathlib import Path

import pytest
import promptiq.store as store


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    """
    Redirects all storage to a fresh temp dir for every single test.
    This ensures zero state leakage between tests.
    """
    monkeypatch.setattr(store, "PROMPTIQ_DIR", tmp_path / ".promptiq")
    monkeypatch.setattr(store, "PROMPTS_DIR",  tmp_path / ".promptiq" / "prompts")


@pytest.fixture()
def sample_prompt():
    return "You are a helpful assistant. Answer concisely in 2-3 sentences."


@pytest.fixture()
def sample_prompt_v2():
    return (
        "You are an expert assistant. "
        "Answer in JSON format with keys 'answer' and 'confidence'. "
        "Be precise and concise."
    )


@pytest.fixture()
def committed_prompt(sample_prompt):
    return store.commit("chatbot", sample_prompt, "initial draft", model="gpt-4")


@pytest.fixture()
def prompt_with_history(sample_prompt, sample_prompt_v2):
    store.commit("chatbot", sample_prompt,    "initial draft", model="gpt-4")
    store.commit("chatbot", sample_prompt_v2, "improved",      model="gpt-4", bump="minor")
    return "chatbot"


@pytest.fixture()
def prompt_file(tmp_path, sample_prompt):
    f = tmp_path / "prompt.txt"
    f.write_text(sample_prompt, encoding="utf-8")
    return str(f)


@pytest.fixture()
def prompt_file_v2(tmp_path, sample_prompt_v2):
    f = tmp_path / "prompt_v2.txt"
    f.write_text(sample_prompt_v2, encoding="utf-8")
    return str(f)


@pytest.fixture()
def test_cases_file(tmp_path):
    cases = [
        "Explain machine learning to a 10-year-old.",
        "What are the risks of using AI in healthcare?",
        "Write a short poem about Python programming.",
    ]
    f = tmp_path / "test_cases.json"
    import json
    f.write_text(json.dumps(cases), encoding="utf-8")
    return str(f)
