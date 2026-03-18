"""
store.py — Local JSON storage for PromptIQ.

Storage layout:
  ~/.promptiq/
  └── prompts/
      ├── summarizer.json
      └── chatbot.json

Every prompt file contains:
  - name, current_branch
  - branches: { branch_name: [ commit, ... ] }

Each commit contains:
  - hash (12-char SHA256)
  - semver (e.g. "1.2.0")
  - message, model, tags, timestamp
  - content (full snapshot)
  - judge_result (optional — full 4-stage evaluation)
"""

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

PROMPTIQ_DIR = Path.home() / ".promptiq"
PROMPTS_DIR  = PROMPTIQ_DIR / "prompts"


# ── Internal helpers ──────────────────────────────────────────────────────────

def _ensure_dirs():
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)


def _prompt_path(name: str) -> Path:
    safe = re.sub(r"[^\w\-]", "_", name)
    return PROMPTS_DIR / f"{safe}.json"


def _sha(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def _load(name: str) -> dict:
    path = _prompt_path(name)
    if not path.exists():
        return {"name": name, "branches": {"main": []}, "current_branch": "main"}
    return json.loads(path.read_text(encoding="utf-8"))


def _save(data: dict):
    _ensure_dirs()
    _prompt_path(data["name"]).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _next_semver(commits: list[dict], bump: str) -> str:
    """Auto-increment version based on existing commits."""
    if not commits:
        return "1.0.0"
    last = commits[-1].get("semver", "1.0.0")
    try:
        major, minor, patch = map(int, last.split("."))
    except Exception:
        return "1.0.0"
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


# ── Public API ────────────────────────────────────────────────────────────────

def commit(
    name: str,
    content: str,
    message: str,
    model: str = "",
    tags: list = None,
    semver: str = None,
    bump: str = "patch",           # "major" | "minor" | "patch"
    judge_result: dict = None,
    branch: str = None,
) -> dict:
    """Save a new version. Returns the commit record."""
    data  = _load(name)
    br    = branch or data.get("current_branch", "main")
    if br not in data["branches"]:
        data["branches"][br] = []

    commits = data["branches"][br]
    ver     = semver or _next_semver(commits, bump)
    h       = _sha(content)

    record = {
        "hash":         h,
        "semver":       ver,
        "message":      message,
        "model":        model,
        "tags":         tags or [],
        "timestamp":    datetime.now(timezone.utc).isoformat(),
        "content":      content,
        "judge_result": judge_result,
    }
    commits.append(record)
    _save(data)
    return record


def log(name: str, branch: str = None) -> list[dict]:
    """Return all commits newest-first."""
    data = _load(name)
    br   = branch or data.get("current_branch", "main")
    return list(reversed(data["branches"].get(br, [])))


def latest(name: str, branch: str = None) -> Optional[dict]:
    entries = log(name, branch)
    return entries[0] if entries else None


def previous(name: str, branch: str = None) -> Optional[dict]:
    """Return the second-most-recent commit (for auto-compare)."""
    entries = log(name, branch)
    return entries[1] if len(entries) > 1 else None


def get_by_ref(name: str, ref: str, branch: str = None) -> Optional[dict]:
    """Find a commit by hash prefix OR semver string."""
    data = _load(name)
    br   = branch or data.get("current_branch", "main")
    for c in data["branches"].get(br, []):
        if c["hash"].startswith(ref) or c.get("semver") == ref:
            return c
    return None


def list_prompts() -> list[dict]:
    _ensure_dirs()
    result = []
    for path in sorted(PROMPTS_DIR.glob("*.json")):
        data    = json.loads(path.read_text(encoding="utf-8"))
        name    = data["name"]
        br      = data.get("current_branch", "main")
        commits = data["branches"].get(br, [])
        last    = commits[-1] if commits else None
        result.append({
            "name":           name,
            "branch":         br,
            "branches":       list(data["branches"].keys()),
            "count":          len(commits),
            "latest_semver":  last.get("semver")   if last else None,
            "latest_hash":    last["hash"]          if last else None,
            "latest_message": last["message"]       if last else None,
            "latest_score":   (last.get("judge_result") or {}).get("overall_score"),
        })
    return result


def create_branch(name: str, branch: str, from_branch: str = None):
    data = _load(name)
    if branch in data["branches"]:
        raise ValueError(f"Branch '{branch}' already exists.")
    src = from_branch or data.get("current_branch", "main")
    data["branches"][branch] = list(data["branches"].get(src, []))
    _save(data)


def switch_branch(name: str, branch: str):
    data = _load(name)
    if branch not in data["branches"]:
        raise ValueError(f"Branch '{branch}' does not exist.")
    data["current_branch"] = branch
    _save(data)


def list_branches(name: str) -> dict:
    data    = _load(name)
    current = data.get("current_branch", "main")
    return {
        "current":  current,
        "branches": {b: len(c) for b, c in data["branches"].items()},
    }


def delete_prompt(name: str):
    p = _prompt_path(name)
    if p.exists():
        p.unlink()


def raw(name: str) -> dict:
    return _load(name)
