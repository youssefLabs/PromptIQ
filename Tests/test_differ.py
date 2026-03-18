"""
tests/test_differ.py — Full test coverage for differ.py
"""

import pytest
from promptiq.differ import line_diff, word_diff, stats, similarity, _tokenize


# ── line_diff ─────────────────────────────────────────────────────────────────

def test_line_diff_no_changes():
    result = line_diff("hello\nworld", "hello\nworld")
    assert all(l.kind == "unchanged" for l in result)


def test_line_diff_addition():
    result = line_diff("line one", "line one\nline two")
    kinds = [l.kind for l in result]
    assert "added" in kinds
    assert "removed" not in kinds


def test_line_diff_removal():
    result = line_diff("line one\nline two", "line one")
    kinds = [l.kind for l in result]
    assert "removed" in kinds
    assert "added" not in kinds


def test_line_diff_replacement():
    result = line_diff("hello world", "hello earth")
    kinds = {l.kind for l in result}
    assert "added" in kinds
    assert "removed" in kinds


def test_line_diff_multiline():
    a = "You are helpful.\nAnswer briefly.\nBe polite."
    b = "You are an expert.\nAnswer in JSON.\nBe polite."
    diffs = line_diff(a, b)
    added   = [l for l in diffs if l.kind == "added"]
    removed = [l for l in diffs if l.kind == "removed"]
    unchanged = [l for l in diffs if l.kind == "unchanged"]
    assert len(added)     == 2
    assert len(removed)   == 2
    assert len(unchanged) == 1


def test_line_diff_empty_to_content():
    result = line_diff("", "new content")
    assert all(l.kind == "added" for l in result if l.content)


def test_line_diff_content_to_empty():
    result = line_diff("old content", "")
    assert all(l.kind == "removed" for l in result if l.content)


# ── word_diff ─────────────────────────────────────────────────────────────────

def test_word_diff_no_changes():
    result = word_diff("hello world", "hello world")
    assert all(k == "equal" for k, _ in result)


def test_word_diff_addition():
    result = word_diff("hello", "hello world")
    kinds = {k for k, _ in result}
    assert "added" in kinds
    assert "removed" not in kinds


def test_word_diff_removal():
    result = word_diff("hello world", "hello")
    kinds = {k for k, _ in result}
    assert "removed" in kinds
    assert "added" not in kinds


def test_word_diff_substitution():
    result = word_diff("You are helpful", "You are expert")
    removed = [w for k, w in result if k == "removed"]
    added   = [w for k, w in result if k == "added"]
    assert "helpful" in removed
    assert "expert"  in added


def test_word_diff_tokens_reconstruct_inputs():
    """Joining equal+added tokens should reconstruct text_b."""
    a = "You are a helpful assistant"
    b = "You are an expert engineer"
    result = word_diff(a, b)
    reconstructed_b = "".join(w for k, w in result if k in ("equal", "added"))
    assert reconstructed_b == b


# ── stats ─────────────────────────────────────────────────────────────────────

def test_stats_unchanged():
    s = stats("same", "same")
    assert s["lines_added"]    == 0
    assert s["lines_removed"]  == 0
    assert s["words_added"]    == 0
    assert s["words_removed"]  == 0


def test_stats_counts_correctly():
    a = "line one\nline two"
    b = "line one\nline three\nline four"
    s = stats(a, b)
    assert s["lines_added"]   == 2
    assert s["lines_removed"] == 1
    assert s["words_added"]   > 0
    assert s["words_removed"] > 0


def test_stats_keys_present():
    s = stats("a", "b")
    assert all(k in s for k in [
        "lines_added", "lines_removed", "lines_unchanged",
        "words_added", "words_removed"
    ])


# ── similarity ────────────────────────────────────────────────────────────────

def test_similarity_identical():
    assert similarity("hello world", "hello world") == 1.0


def test_similarity_completely_different():
    assert similarity("aaa bbb ccc", "zzz yyy xxx") < 0.3


def test_similarity_partial():
    a = "You are a helpful assistant"
    b = "You are an expert assistant"
    s = similarity(a, b)
    assert 0.5 < s < 1.0


def test_similarity_range():
    s = similarity("some text", "completely different")
    assert 0.0 <= s <= 1.0


def test_similarity_empty_strings():
    assert similarity("", "") == 1.0


# ── _tokenize ─────────────────────────────────────────────────────────────────

def test_tokenize_preserves_whitespace():
    tokens = _tokenize("hello   world")
    assert "hello" in tokens
    assert "world" in tokens
    assert any(t.strip() == "" for t in tokens)


def test_tokenize_roundtrip():
    text = "You are a helpful\nassistant. Be concise."
    tokens = _tokenize(text)
    assert "".join(tokens) == text
