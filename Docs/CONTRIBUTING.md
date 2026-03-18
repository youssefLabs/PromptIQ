# Contributing to PromptIQ

## Philosophy

PromptIQ is a craftsman's tool. It should do one thing — intelligent prompt management — and do it exceptionally well.

**We will never add:**
- A web dashboard (use the terminal)
- User accounts or cloud sync (everything stays local)
- Framework lock-in (it works with any LLM, any codebase)

**We welcome contributions that:**
- Fix bugs
- Add new judge dimensions or improve scoring logic
- Improve the A/B test engine
- Add export formats
- Improve test coverage
- Fix documentation

---

## Setup

```bash
git clone https://github.com/youssefLabs/promptvc
cd promptvc
pip install -e ".[dev]"
```

---

## Running Tests

```bash
# All tests (no API key required)
pytest tests/ -v

# Specific module
pytest tests/test_store.py -v
pytest tests/test_differ.py -v
pytest tests/test_cli.py -v
pytest tests/test_export.py -v
```

No API key is needed to run the test suite — the judge and A/B tests are not tested automatically (they require real LLM calls). To test those locally, set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` and run:

```bash
promptiq judge examples/sample_prompt.txt --test-cases examples/test_cases.json
```

---

## Code Style

- **No circular imports.** Each layer only imports from layers below it.
- **No logic in `cli.py`.** It calls other modules and renders output. Nothing else.
- **Pure functions in `differ.py`.** No side effects, no globals.
- **Dataclasses for all structured results.** Every judge stage returns a `@dataclass` with a `.to_dict()` method.
- Type hints on all public functions.

---

## Commit Style

```
feat:     new feature
fix:      bug fix
refactor: code change with no behavior change
test:     adding or fixing tests
docs:     documentation only
chore:    build system, CI, dependencies
```

---

## Adding a New Judge Dimension

1. Edit `promptiq/judge/static.py` — add the dimension to `SYSTEM` prompt and `StaticScore` dataclass
2. Update the `_compute_overall` weighted average
3. Update `display.py` to render the new dimension
4. Add the dimension to all export templates in `export.py`
5. Add tests in `tests/test_store.py` (for storage) and update `conftest.py`

---

## Opening a Pull Request

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Make your changes + add tests
4. Run `pytest tests/ -v` — all tests must pass
5. Open a PR with a clear description

Please open an issue before starting large changes.
