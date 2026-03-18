# PromptIQ Judge — Complete Guide

The judge is the feature that separates PromptIQ from every other prompt tool.
It doesn't just store your prompts — it understands them.

---

## The 4 Stages

```
Stage 1 ─── Static Analysis    Who you are, before you do anything
Stage 2 ─── Output Evaluation  What you actually produce
Stage 3 ─── Version Compare    How you compare to your past self
Stage 4 ─── Auto-Improvement   How to become better
```

Each stage is independent and can be called alone or combined.

---

## Stage 1 — Static Analysis

**What it does:** Scores the prompt text itself across 5 dimensions.

**When to use it:** When you want a quick quality check without spending API calls on actual runs.

```bash
promptiq judge prompt.txt --no-suggest
```

### Dimensions

| Dimension | Weight | What it measures |
|---|---|---|
| Clarity | 1x | Unambiguous? Two engineers would interpret it identically? |
| Specificity | 1x | Instructions are concrete, not vague? |
| Conciseness | 1x | Free of filler, redundancy, and padding? |
| Instruction Quality | 1.5x | Effectively guides the model toward the intended behavior? |
| Robustness | 1.5x | Handles edge cases, off-topic inputs, and failure modes? |

**Overall** = weighted average of all 5.

### How to improve each dimension

**Low Clarity (<6):** Your prompt contains ambiguous words or instructions that could be interpreted multiple ways.
- ❌ `"Be helpful and professional"`
- ✅ `"Answer questions about our product. Use a friendly, professional tone. Do not discuss competitors."`

**Low Specificity (<6):** Your instructions don't tell the model *exactly* what to do.
- ❌ `"Format your response nicely"`
- ✅ `"Format your response as a JSON object with keys 'summary' (1 sentence) and 'details' (bullet list)"`

**Low Conciseness (<6):** Your prompt has redundant phrases, filler, or over-explained instructions.
- ❌ `"As a helpful AI assistant, your goal and purpose is to assist users by helping them with their questions..."`
- ✅ `"Answer user questions about X."`

**Low Instruction Quality (<6):** The model can satisfy the prompt's literal instructions while still producing unhelpful outputs.
- ❌ `"Be an expert in cooking"` (vague persona, no behavioral guidance)
- ✅ `"You are a professional chef. When asked about recipes, always specify ingredients first, then steps. Estimate prep time."`

**Low Robustness (<6):** Your prompt doesn't handle situations the model is likely to encounter.
- ❌ *(no off-topic handling)*
- ✅ `"If the user asks about something outside your scope, say: 'I can only help with X. For other topics, please contact support.'"`

---

## Stage 2 — Output Evaluation

**What it does:** Actually runs your prompt against test inputs, captures real outputs, and evaluates them.

**When to use it:** When you want to know how the prompt performs in practice, not just on paper.

```bash
promptiq judge prompt.txt --test-cases inputs.json
```

### Test Inputs Format

Two formats supported:

**JSON array** (recommended):
```json
[
  "Explain machine learning to a 10-year-old.",
  "What are the risks of AI in healthcare?",
  "Write a function that reverses a string."
]
```

**Plain text** (one per line):
```
Explain machine learning to a 10-year-old.
What are the risks of AI in healthcare?
Write a function that reverses a string.
```

### Evaluation Dimensions

| Dimension | What it measures |
|---|---|
| Relevance | Did the output actually address the user's input? |
| Instruction Follow | Did the model follow ALL instructions in the system prompt? |
| Quality | Is the output accurate, well-structured, and useful? |

### Reading the Results

```
  Test 1: Explain machine learning to a 10-year-old.
    Relevance:     ████████░░ 8/10   ← addressed the question well
    Instructions:  ██████░░░░ 6/10   ← missed the "10-year-old" constraint
    Quality:       ███████░░░ 7/10   ← good but slightly technical
    Verdict: Output explained ML correctly but used jargon inappropriate
             for the specified age group.
    ⚠️  Used term "gradient descent" without explanation
```

A **low Instruction Follow** score (< 6) means your prompt's instructions aren't strong enough — the model is ignoring them. Fix: make the instructions more explicit and add examples.

A **low Relevance** score (< 6) means the model is going off-topic or misunderstanding the input. Fix: add more context about what the model should focus on.

---

## Stage 3 — Version Compare

**What it does:** Compares the new version to the previous one and declares a winner.

**Runs automatically** when you use `--judge` on a prompt that already has commits.

Can also be run standalone:
```bash
promptiq judge prompt_v2.txt --compare-with chatbot
```

### Reading the Results

```
  STAGE 3 — Version Comparison
  ────────────────────────────────────────────────────────
  Old version:  6.2/10
  New version:  8.4/10
  Delta:        ▲ 2.2 pts

  New version wins ✓
  The new version adds explicit JSON format requirements that were absent
  before, eliminating the model's tendency to produce unstructured text.

  Improvements:
  ✅ Added explicit output format requirement
  ✅ Defined maximum response length with "max 3 sentences"

  Regressions:
  ❌ Persona definition became vague ("be helpful" vs specific role)
```

**Regressions are valuable.** They tell you what you broke while fixing something else. A common pattern: improving specificity at the cost of conciseness.

---

## Stage 4 — Auto-Improvement

**What it does:** Rewrites your prompt to address its specific weaknesses.

The rewrite is *targeted* — it uses the actual weakness list and scores from Stage 1 to build its instructions. It's not generic advice.

```bash
# Run as part of judge
promptiq judge prompt.txt    # suggest is on by default

# Or run standalone on any committed version
promptiq improve chatbot
promptiq improve chatbot 1.0.0
```

### Reading the Results

```
  STAGE 4 — Auto-Improvement
  ────────────────────────────────────────────────────────
  Expected gain: +2 pts specificity, +1.5 pts robustness

  Changes:
  → Replaced "be helpful" with "answer in under 3 sentences" (specificity +2)
  → Added "If you don't know, say 'I don't know'" (robustness +1.5)
  → Removed "as an AI language model" filler (conciseness +1)

  💡 Improved version saved → suggested.txt
```

### The Right Workflow

```bash
# 1. Commit your current version
promptiq commit chatbot system.txt -m "draft v1"

# 2. Run the judge
promptiq judge system.txt

# 3. Review the suggestion
cat suggested.txt

# 4. Edit if needed, then commit the improvement
promptiq commit chatbot suggested.txt -m "apply AI improvements" --judge

# 5. Compare: did it actually get better?
promptiq diff chatbot 1.0.0 1.0.1
```

---

## Composite Score Formula

```
overall = static.overall × 0.50
        + avg(output.quality) × 0.35        ← only if test inputs provided
        + min(compare.delta × 0.15, 1.5)    ← only if delta > 0

If no test inputs:
overall = static.overall × 0.85
        + min(compare.delta × 0.15, 1.5)
```

The composite score is **always lower than the static score alone** unless your outputs are excellent. This is intentional — a prompt that looks good on paper but produces bad outputs should not score highly.

---

## API Cost Estimate

Per `promptiq commit --judge --test-cases inputs.json` with N test inputs:

| Stage | LLM Calls | Notes |
|---|---|---|
| Static Analysis | 1 | ~500 tokens in, ~200 out |
| Output Eval | N × 2 | run + judge per input |
| Compare | 1 | only if previous version exists |
| Suggest | 1 | ~800 tokens out |
| **Total** | **3 + N×2** | e.g. 3 inputs = 9 calls |

At GPT-4o-mini prices (~$0.00015/1K tokens), a full evaluation with 3 test cases costs roughly **$0.02–0.05**.
