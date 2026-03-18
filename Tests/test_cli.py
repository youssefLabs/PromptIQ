"""
tests/test_cli.py — CLI integration tests via Click's CliRunner.

All tests run in full isolation — each test gets its own temp store.
No LLM calls are made (judge/improve/ab require real API keys).
"""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

import promptiq.store as store
from promptiq.cli import cli


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "PROMPTIQ_DIR", tmp_path / ".promptiq")
    monkeypatch.setattr(store, "PROMPTS_DIR",  tmp_path / ".promptiq" / "prompts")


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def prompt_file(tmp_path):
    f = tmp_path / "prompt.txt"
    f.write_text("You are a helpful assistant. Be concise.")
    return str(f)


@pytest.fixture()
def prompt_file_v2(tmp_path):
    f = tmp_path / "prompt_v2.txt"
    f.write_text("You are an expert assistant. Answer in JSON format. Be concise.")
    return str(f)


# ── commit ────────────────────────────────────────────────────────────────────

def test_commit_basic(runner, prompt_file):
    res = runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "initial draft"])
    assert res.exit_code == 0
    assert "Committed"     in res.output
    assert "v1.0.0"        in res.output
    assert "initial draft" in res.output


def test_commit_auto_increments_version(runner, prompt_file, prompt_file_v2):
    runner.invoke(cli, ["commit", "bot", prompt_file,    "-m", "v1"])
    res = runner.invoke(cli, ["commit", "bot", prompt_file_v2, "-m", "v2"])
    assert "v1.0.1" in res.output


def test_commit_minor_bump(runner, prompt_file, prompt_file_v2):
    runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "v1"])
    res = runner.invoke(cli, ["commit", "bot", prompt_file_v2, "-m", "v2", "--bump", "minor"])
    assert "v1.1.0" in res.output


def test_commit_major_bump(runner, prompt_file, prompt_file_v2):
    runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "v1"])
    res = runner.invoke(cli, ["commit", "bot", prompt_file_v2, "-m", "v2", "--bump", "major"])
    assert "v2.0.0" in res.output


def test_commit_explicit_semver(runner, prompt_file):
    res = runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "v1", "--semver", "3.1.4"])
    assert "v3.1.4" in res.output


def test_commit_with_tags(runner, prompt_file):
    res = runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "tagged", "--tags", "prod,stable"])
    assert res.exit_code == 0


def test_commit_with_model(runner, prompt_file):
    res = runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "with model", "--model", "gpt-4"])
    assert res.exit_code == 0


def test_commit_missing_message_fails(runner, prompt_file):
    res = runner.invoke(cli, ["commit", "bot", prompt_file])
    assert res.exit_code != 0


# ── log ───────────────────────────────────────────────────────────────────────

def test_log_shows_all_commits(runner, prompt_file, prompt_file_v2):
    runner.invoke(cli, ["commit", "bot", prompt_file,    "-m", "first"])
    runner.invoke(cli, ["commit", "bot", prompt_file_v2, "-m", "second"])
    res = runner.invoke(cli, ["log", "bot"])
    assert res.exit_code == 0
    assert "first"  in res.output
    assert "second" in res.output


def test_log_newest_first(runner, prompt_file, prompt_file_v2):
    runner.invoke(cli, ["commit", "bot", prompt_file,    "-m", "first"])
    runner.invoke(cli, ["commit", "bot", prompt_file_v2, "-m", "second"])
    res = runner.invoke(cli, ["log", "bot"])
    assert res.output.index("second") < res.output.index("first")


def test_log_empty_prompt(runner):
    res = runner.invoke(cli, ["log", "nonexistent"])
    assert res.exit_code == 0
    assert "No commits" in res.output


def test_log_limit(runner, prompt_file, prompt_file_v2):
    runner.invoke(cli, ["commit", "bot", prompt_file,    "-m", "a"])
    runner.invoke(cli, ["commit", "bot", prompt_file_v2, "-m", "b"])
    runner.invoke(cli, ["commit", "bot", prompt_file,    "-m", "c"])
    res = runner.invoke(cli, ["log", "bot", "-n", "1"])
    assert "c" in res.output
    assert "a" not in res.output


def test_log_show_content(runner, prompt_file):
    runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "v1"])
    res = runner.invoke(cli, ["log", "bot", "--show-content"])
    assert "helpful assistant" in res.output


# ── diff ──────────────────────────────────────────────────────────────────────

def test_diff_by_semver(runner, prompt_file, prompt_file_v2):
    runner.invoke(cli, ["commit", "bot", prompt_file,    "-m", "v1"])
    runner.invoke(cli, ["commit", "bot", prompt_file_v2, "-m", "v2"])
    res = runner.invoke(cli, ["diff", "bot", "1.0.0", "1.0.1"])
    assert res.exit_code == 0


def test_diff_by_hash(runner, prompt_file, prompt_file_v2):
    runner.invoke(cli, ["commit", "bot", prompt_file,    "-m", "v1"])
    runner.invoke(cli, ["commit", "bot", prompt_file_v2, "-m", "v2"])
    h1 = store.log("bot")[-1]["hash"]
    h2 = store.log("bot")[0]["hash"]
    res = runner.invoke(cli, ["diff", "bot", h1[:6], h2[:6]])
    assert res.exit_code == 0


def test_diff_shows_similarity(runner, prompt_file, prompt_file_v2):
    runner.invoke(cli, ["commit", "bot", prompt_file,    "-m", "v1"])
    runner.invoke(cli, ["commit", "bot", prompt_file_v2, "-m", "v2"])
    res = runner.invoke(cli, ["diff", "bot", "1.0.0", "1.0.1"])
    assert "similar" in res.output


def test_diff_invalid_ref(runner, prompt_file):
    runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "v1"])
    res = runner.invoke(cli, ["diff", "bot", "9.9.9", "8.8.8"])
    assert res.exit_code != 0


# ── status ────────────────────────────────────────────────────────────────────

def test_status_shows_prompt_name(runner, prompt_file):
    runner.invoke(cli, ["commit", "mybot", prompt_file, "-m", "v1"])
    res = runner.invoke(cli, ["status", "mybot"])
    assert "mybot" in res.output


def test_status_shows_version(runner, prompt_file):
    runner.invoke(cli, ["commit", "mybot", prompt_file, "-m", "v1"])
    res = runner.invoke(cli, ["status", "mybot"])
    assert "v1.0.0" in res.output


def test_status_shows_content_preview(runner, prompt_file):
    runner.invoke(cli, ["commit", "mybot", prompt_file, "-m", "v1"])
    res = runner.invoke(cli, ["status", "mybot"])
    assert "helpful assistant" in res.output


def test_status_empty_prompt(runner):
    res = runner.invoke(cli, ["status", "ghost"])
    assert res.exit_code == 0
    assert "No commits" in res.output


# ── checkout ──────────────────────────────────────────────────────────────────

def test_checkout_by_semver(runner, prompt_file, tmp_path):
    runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "v1"])
    out = str(tmp_path / "recovered.txt")
    res = runner.invoke(cli, ["checkout", "bot", "1.0.0", "--output", out])
    assert res.exit_code == 0
    assert Path(out).read_text() == "You are a helpful assistant. Be concise."


def test_checkout_restores_exact_content(runner, prompt_file, prompt_file_v2, tmp_path):
    runner.invoke(cli, ["commit", "bot", prompt_file,    "-m", "v1"])
    runner.invoke(cli, ["commit", "bot", prompt_file_v2, "-m", "v2"])
    out = str(tmp_path / "old.txt")
    runner.invoke(cli, ["checkout", "bot", "1.0.0", "--output", out])
    assert "You are a helpful" in Path(out).read_text()


def test_checkout_invalid_ref(runner, prompt_file):
    runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "v1"])
    res = runner.invoke(cli, ["checkout", "bot", "9.9.9"])
    assert res.exit_code != 0


# ── ls ────────────────────────────────────────────────────────────────────────

def test_ls_shows_all_prompts(runner, prompt_file):
    runner.invoke(cli, ["commit", "alpha", prompt_file, "-m", "v1"])
    runner.invoke(cli, ["commit", "beta",  prompt_file, "-m", "v1"])
    runner.invoke(cli, ["commit", "gamma", prompt_file, "-m", "v1"])
    res = runner.invoke(cli, ["ls"])
    assert "alpha" in res.output
    assert "beta"  in res.output
    assert "gamma" in res.output


def test_ls_empty_state(runner):
    res = runner.invoke(cli, ["ls"])
    assert res.exit_code == 0
    assert "No prompts" in res.output


# ── branch ────────────────────────────────────────────────────────────────────

def test_branch_create(runner, prompt_file):
    runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "v1"])
    res = runner.invoke(cli, ["branch", "create", "bot", "exp"])
    assert res.exit_code == 0
    assert "exp" in res.output


def test_branch_switch(runner, prompt_file):
    runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "v1"])
    runner.invoke(cli, ["branch", "create", "bot", "exp"])
    res = runner.invoke(cli, ["branch", "switch", "bot", "exp"])
    assert res.exit_code == 0


def test_branch_ls(runner, prompt_file):
    runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "v1"])
    runner.invoke(cli, ["branch", "create", "bot", "exp"])
    res = runner.invoke(cli, ["branch", "ls", "bot"])
    assert "main" in res.output
    assert "exp"  in res.output


def test_branch_create_duplicate_fails(runner, prompt_file):
    runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "v1"])
    runner.invoke(cli, ["branch", "create", "bot", "exp"])
    res = runner.invoke(cli, ["branch", "create", "bot", "exp"])
    assert res.exit_code != 0


# ── export ────────────────────────────────────────────────────────────────────

def test_export_markdown(runner, prompt_file, tmp_path):
    runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "v1"])
    out = str(tmp_path / "changelog.md")
    res = runner.invoke(cli, ["export", "bot", "--output", out])
    assert res.exit_code == 0
    assert Path(out).exists()


def test_export_json(runner, prompt_file, tmp_path):
    runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "v1"])
    out = str(tmp_path / "history.json")
    res = runner.invoke(cli, ["export", "bot", "--format", "json", "--output", out])
    assert res.exit_code == 0
    parsed = json.loads(Path(out).read_text())
    assert parsed["name"] == "bot"


def test_export_scores(runner, prompt_file, tmp_path):
    runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "v1"])
    out = str(tmp_path / "scores.md")
    res = runner.invoke(cli, ["export", "bot", "--format", "scores", "--output", out])
    assert res.exit_code == 0


# ── delete ────────────────────────────────────────────────────────────────────

def test_delete_removes_prompt(runner, prompt_file):
    runner.invoke(cli, ["commit", "bot", prompt_file, "-m", "v1"])
    res = runner.invoke(cli, ["delete", "bot"], input="y\n")
    assert res.exit_code == 0
    assert store.log("bot") == []
