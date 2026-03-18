# PromptIQ — Architecture Guide

## Overview

PromptIQ is built on one principle: **each layer knows nothing about the others.**

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI (cli.py)                         │
│         Pure I/O. Calls other modules. Zero logic.          │
└────────┬───────────┬───────────┬────────────┬──────────────┘
         │           │           │            │
    ┌────▼───┐  ┌────▼───┐  ┌───▼────┐  ┌───▼────┐
    │ store  │  │ differ │  │   ab   │  │ export │
    │  .py   │  │  .py   │  │  .py   │  │  .py   │
    └────────┘  └────────┘  └───┬────┘  └────────┘
                                │
                        ┌───────▼────────────────┐
                        │      judge/             │
                        │                         │
                        │  __init__.py            │
                        │  (orchestrator)         │
                        │                         │
                        │  client.py  ←── LLM     │
                        │  static.py  ←── Stage 1 │
                        │  runner.py  ←── Stage 2 │
                        │  compare.py ←── Stage 3 │
                        │  suggest.py ←── Stage 4 │
                        └─────────────────────────┘
```

---

## Module Responsibilities

### `cli.py`
The entry point. Contains all Click commands. Has **zero business logic** — it only:
- Reads files from disk
- Calls other modules
- Renders output to the terminal via `display.py`

Adding a new command = one function in `cli.py`. No other file changes required.

---

### `store.py`
The only module that touches disk. Responsible for:
- Reading and writing JSON files to `~/.promptiq/prompts/`
- Semver auto-increment logic
- Branch management
- Hash computation (SHA-256, 12 chars)

**Storage format:**
```json
{
  "name": "chatbot",
  "current_branch": "main",
  "branches": {
    "main": [
      {
        "hash": "a3f92c1b9e4d",
        "semver": "1.2.0",
        "message": "improved tone",
        "model": "gpt-4",
        "tags": ["prod"],
        "timestamp": "2025-01-01T10:00:00+00:00",
        "content": "You are...",
        "judge_result": { ... }
      }
    ]
  }
}
```

Every prompt = one `.json` file. Human-readable. Git-friendly.

---

### `differ.py`
Pure functions. Zero side effects. No imports beyond stdlib.

- `line_diff(a, b)` — unified line-level diff
- `word_diff(a, b)` — token-level diff (words + whitespace)
- `stats(a, b)` — added/removed line/word counts
- `similarity(a, b)` — 0.0–1.0 similarity ratio

The word-level diff preserves whitespace, so tokens can be directly concatenated to reconstruct original text.

---

### `judge/` — The 4-Stage Intelligence Engine

#### `client.py`
Provider detection and unified LLM call interface.
- Auto-detects `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
- `call(client, provider, system, user)` — works identically for both
- `parse_json(raw)` — strips markdown fences, parses safely

#### `judge/__init__.py` — Orchestrator
Runs all 4 stages in sequence. Accepts a `progress_cb` callback so the CLI can show live progress. Computes a **composite overall score**:

```
overall = static.overall * 0.50
        + avg(output.quality) * 0.35
        + min(compare.delta * 0.15, 1.5)   # only if delta > 0
```

If no test inputs: static weight becomes 0.85.

#### `static.py` — Stage 1
Scores the prompt text on 5 dimensions via LLM:
- **Clarity** — unambiguous, consistent interpretation
- **Specificity** — concrete, actionable instructions
- **Conciseness** — no filler, no redundancy
- **Instruction Quality** — effectively guides model behavior (weight: 1.5x)
- **Robustness** — handles edge cases, failure modes (weight: 1.5x)

#### `runner.py` — Stage 2
Two LLM calls per test input:
1. **Run** — sends `system=prompt, user=test_input` to the LLM
2. **Judge** — sends the system prompt + input + output to a judge model

Scores: `relevance`, `instruction_follow`, `quality` (each 0–10).

#### `compare.py` — Stage 3
Sends both versions to a judge. Returns:
- `winner`: "a" | "b" | "tie"
- `score_a`, `score_b`, `delta`
- `improvements`, `regressions` (specific, cited)

#### `suggest.py` — Stage 4
Uses the static score to build a targeted rewrite prompt. The system prompt explicitly lists the weaknesses and their scores, so the LLM improvement is grounded in the actual analysis, not generic advice.

Returns: `improved` (full text), `changes` (bullet list), `expected_gain`.

---

### `ab.py`
A/B testing engine. For each test input:
1. Runs `output_eval` on both versions in sequence
2. Calls a pairwise judge to compare the two outputs
3. Aggregates into overall winner + summary

Uses the same `client_tuple` pattern as the judge module.

---

### `display.py`
All terminal rendering. Every `click.secho` call that isn't in `cli.py` lives here.
- `show_commit()` — single commit with score bars
- `show_full_judge()` — full 4-stage report
- `show_ab_result()` — A/B test results
- `show_diff()` — colored word-level diff
- `score_bar()`, `score_stars()`, `score_color()` — visual helpers

---

### `export.py`
Three export formats:
- `export_json()` — raw history, machine-readable
- `export_markdown()` — full changelog with scores, team-readable
- `export_score_report()` — score evolution table with trend arrows

---

## Data Flow: `promptiq commit chatbot prompt.txt -m "v2" --judge --test-cases inputs.json`

```
cli.commit()
  │
  ├── read prompt.txt → content
  ├── load test inputs from inputs.json
  ├── store.latest("chatbot") → previous_content
  │
  ├── judge.orchestrate(content, test_inputs, previous_content)
  │     │
  │     ├── [Stage 1] static.static_analysis(content, client)
  │     │       └── 1 LLM call → StaticScore
  │     │
  │     ├── [Stage 2] runner.output_eval(content, input, client) × N
  │     │       └── 2 LLM calls per input → OutputEval
  │     │
  │     ├── [Stage 3] compare.compare_versions(prev, content, client)
  │     │       └── 1 LLM call → CompareResult
  │     │
  │     ├── [Stage 4] suggest.suggest_improvement(content, static, client)
  │     │       └── 1 LLM call → SuggestResult
  │     │
  │     └── → FullJudgeResult (composite score computed locally)
  │
  ├── store.commit(name, content, message, judge_result=result.to_dict())
  │       └── writes ~/.promptiq/prompts/chatbot.json
  │
  └── display output + save suggested.txt if improvement exists
```

**Total LLM calls per commit with 3 test inputs:** `1 + (3×2) + 1 + 1 = 9 calls`

---

## Design Decisions

**Why JSON instead of SQLite?**
JSON files are human-readable, can be committed to git, diffed in any editor, and require zero setup. A developer can open any prompt file and read their entire history without tooling. SQLite requires a viewer and creates binary diffs.

**Why semver instead of sequential IDs?**
Semver communicates intent. `v2.0.0` signals a breaking change. `v1.1.0` signals a new feature. Sequential IDs (`v12`) communicate nothing. Users can also reference versions by either hash prefix or semver — whichever is more natural.

**Why composite scoring?**
A prompt that scores 9/10 on static analysis but produces bad outputs in practice is not a 9/10 prompt. The composite score weights real-world output quality (35%) alongside static analysis (50%), giving a more accurate picture of actual performance.

**Why a separate `display.py`?**
Separating rendering from logic means the CLI commands stay readable, the rendering can be changed without touching business logic, and the same judge results can be displayed differently in future (e.g., web UI, JSON output mode).
