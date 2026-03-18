"""
tests/test_store.py — Full test coverage for store.py

Tests:
  - Commit creation and retrieval
  - Semver auto-bump (patch, minor, major)
  - Log ordering (newest first)
  - get_by_ref: hash prefix + semver string
  - Branches: create, switch, isolation
  - previous() helper
  - list_prompts() aggregate
  - delete_prompt()
  - JSON persistence (write → reload → verify)
"""

import json
import tempfile
from pathlib import Path

import pytest
import promptiq.store as store


@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    """Redirect storage to a fresh temp dir for every test."""
    monkeypatch.setattr(store, "PROMPTIQ_DIR", tmp_path / ".promptiq")
    monkeypatch.setattr(store, "PROMPTS_DIR",  tmp_path / ".promptiq" / "prompts")


# ── Commit & retrieval ────────────────────────────────────────────────────────

def test_commit_returns_record():
    r = store.commit("p", "You are helpful.", "initial")
    assert r["hash"]
    assert r["message"] == "initial"
    assert r["content"] == "You are helpful."
    assert r["semver"]  == "1.0.0"


def test_commit_stores_all_fields():
    score = {"overall_score": 8.0, "static": {}}
    r = store.commit("p", "content", "msg",
                     model="gpt-4", tags=["prod", "v1"], judge_result=score)
    assert r["model"]        == "gpt-4"
    assert r["tags"]         == ["prod", "v1"]
    assert r["judge_result"] == score


def test_commit_persists_to_disk():
    store.commit("p", "hello", "v1")
    # Force a fresh load from disk
    data = json.loads((store.PROMPTS_DIR / "p.json").read_text())
    assert data["name"] == "p"
    assert data["branches"]["main"][0]["content"] == "hello"


# ── Semver auto-bump ──────────────────────────────────────────────────────────

def test_semver_default_patch():
    store.commit("p", "a", "v1")
    r2 = store.commit("p", "b", "v2")
    assert r2["semver"] == "1.0.1"


def test_semver_minor_bump():
    store.commit("p", "a", "v1")
    r2 = store.commit("p", "b", "v2", bump="minor")
    assert r2["semver"] == "1.1.0"


def test_semver_major_bump():
    store.commit("p", "a", "v1")
    r2 = store.commit("p", "b", "v2", bump="major")
    assert r2["semver"] == "2.0.0"


def test_semver_explicit_override():
    r = store.commit("p", "a", "v1", semver="5.0.0")
    assert r["semver"] == "5.0.0"


def test_semver_chain():
    store.commit("p", "a", "v1")
    store.commit("p", "b", "v2", bump="minor")
    store.commit("p", "c", "v3", bump="patch")
    store.commit("p", "d", "v4", bump="major")
    versions = [c["semver"] for c in reversed(store.log("p"))]
    assert versions == ["1.0.0", "1.1.0", "1.1.1", "2.0.0"]


# ── Log ordering ──────────────────────────────────────────────────────────────

def test_log_newest_first():
    store.commit("p", "v1", "first")
    store.commit("p", "v2", "second")
    store.commit("p", "v3", "third")
    log = store.log("p")
    assert log[0]["message"] == "third"
    assert log[-1]["message"] == "first"


def test_log_empty_for_new_prompt():
    assert store.log("nonexistent") == []


# ── get_by_ref ────────────────────────────────────────────────────────────────

def test_get_by_hash_prefix():
    r = store.commit("p", "hello", "v1")
    found = store.get_by_ref("p", r["hash"][:6])
    assert found is not None
    assert found["content"] == "hello"


def test_get_by_semver():
    store.commit("p", "a", "v1")
    store.commit("p", "b", "v2", bump="minor")
    found = store.get_by_ref("p", "1.1.0")
    assert found is not None
    assert found["content"] == "b"


def test_get_by_ref_missing_returns_none():
    store.commit("p", "a", "v1")
    assert store.get_by_ref("p", "zzzzz") is None


# ── latest / previous ─────────────────────────────────────────────────────────

def test_latest_returns_most_recent():
    store.commit("p", "a", "v1")
    store.commit("p", "b", "v2")
    assert store.latest("p")["message"] == "v2"


def test_latest_none_for_empty():
    assert store.latest("new_prompt") is None


def test_previous_returns_second_most_recent():
    store.commit("p", "a", "v1")
    store.commit("p", "b", "v2")
    store.commit("p", "c", "v3")
    assert store.previous("p")["message"] == "v2"


def test_previous_none_when_only_one_commit():
    store.commit("p", "a", "v1")
    assert store.previous("p") is None


# ── Branches ──────────────────────────────────────────────────────────────────

def test_create_branch_copies_history():
    store.commit("p", "main content", "v1")
    store.create_branch("p", "exp")
    assert len(store.log("p", "exp")) == 1


def test_create_branch_from_another():
    store.commit("p", "main", "v1", branch="main")
    store.create_branch("p", "exp", from_branch="main")
    store.commit("p", "exp content", "exp-v1", branch="exp")
    assert len(store.log("p", "main")) == 1
    assert len(store.log("p", "exp"))  == 2


def test_switch_branch():
    store.commit("p", "main", "v1")
    store.create_branch("p", "feature")
    store.switch_branch("p", "feature")
    store.commit("p", "feature content", "f1")
    assert store.latest("p")["content"] == "feature content"


def test_branch_isolation():
    store.commit("p", "main content", "v1")
    store.create_branch("p", "exp")
    store.commit("p", "exp content", "e1", branch="exp")
    store.commit("p", "exp content 2", "e2", branch="exp")
    assert len(store.log("p", "main")) == 1
    assert len(store.log("p", "exp"))  == 3


def test_create_duplicate_branch_raises():
    store.commit("p", "a", "v1")
    store.create_branch("p", "exp")
    with pytest.raises(ValueError):
        store.create_branch("p", "exp")


def test_switch_nonexistent_branch_raises():
    store.commit("p", "a", "v1")
    with pytest.raises(ValueError):
        store.switch_branch("p", "ghost")


def test_list_branches():
    store.commit("p", "a", "v1")
    store.create_branch("p", "b1")
    store.create_branch("p", "b2")
    info = store.list_branches("p")
    assert "main" in info["branches"]
    assert "b1"   in info["branches"]
    assert "b2"   in info["branches"]


# ── list_prompts ──────────────────────────────────────────────────────────────

def test_list_prompts_returns_all():
    store.commit("alpha", "a", "v1")
    store.commit("beta",  "b", "v1")
    store.commit("gamma", "c", "v1")
    names = {p["name"] for p in store.list_prompts()}
    assert {"alpha", "beta", "gamma"} == names


def test_list_prompts_includes_latest_info():
    store.commit("p", "content", "the message")
    prompts = store.list_prompts()
    assert prompts[0]["latest_message"] == "the message"
    assert prompts[0]["count"] == 1


# ── delete ────────────────────────────────────────────────────────────────────

def test_delete_removes_all_history():
    store.commit("p", "a", "v1")
    store.delete_prompt("p")
    assert store.log("p") == []


def test_delete_nonexistent_is_safe():
    store.delete_prompt("ghost")   # should not raise
