"""
differ.py — Word-level and line-level diff engine.
Pure functions. Zero side effects.
"""

import difflib
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class DiffLine:
    kind: str           # "added" | "removed" | "unchanged"
    content: str
    line_a: Optional[int] = None
    line_b: Optional[int] = None


def line_diff(text_a: str, text_b: str) -> list[DiffLine]:
    lines_a = text_a.splitlines(keepends=True)
    lines_b = text_b.splitlines(keepends=True)
    result: list[DiffLine] = []
    matcher = difflib.SequenceMatcher(None, lines_a, lines_b, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for k, ln in enumerate(lines_a[i1:i2]):
                result.append(DiffLine("unchanged", ln.rstrip("\n"), i1+k+1, j1+k+1))
        elif tag in ("replace", "delete"):
            for k, ln in enumerate(lines_a[i1:i2]):
                result.append(DiffLine("removed", ln.rstrip("\n"), i1+k+1, None))
            if tag == "replace":
                for k, ln in enumerate(lines_b[j1:j2]):
                    result.append(DiffLine("added", ln.rstrip("\n"), None, j1+k+1))
        elif tag == "insert":
            for k, ln in enumerate(lines_b[j1:j2]):
                result.append(DiffLine("added", ln.rstrip("\n"), None, j1+k+1))
    return result


def word_diff(text_a: str, text_b: str) -> list[tuple[str, str]]:
    """Returns list of (kind, token) — kind ∈ {equal, added, removed}."""
    wa = _tokenize(text_a)
    wb = _tokenize(text_b)
    result = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, wa, wb, autojunk=False).get_opcodes():
        if tag == "equal":
            for w in wa[i1:i2]: result.append(("equal", w))
        elif tag in ("replace", "delete"):
            for w in wa[i1:i2]: result.append(("removed", w))
            if tag == "replace":
                for w in wb[j1:j2]: result.append(("added", w))
        elif tag == "insert":
            for w in wb[j1:j2]: result.append(("added", w))
    return result


def stats(text_a: str, text_b: str) -> dict:
    lines = line_diff(text_a, text_b)
    words = word_diff(text_a, text_b)
    return {
        "lines_added":    sum(1 for l in lines if l.kind == "added"),
        "lines_removed":  sum(1 for l in lines if l.kind == "removed"),
        "lines_unchanged":sum(1 for l in lines if l.kind == "unchanged"),
        "words_added":    sum(1 for k, _ in words if k == "added"),
        "words_removed":  sum(1 for k, _ in words if k == "removed"),
    }


def similarity(text_a: str, text_b: str) -> float:
    return difflib.SequenceMatcher(None, text_a, text_b).ratio()


def _tokenize(text: str) -> list[str]:
    return re.findall(r'\S+|\s+', text)
