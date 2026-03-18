"""
display.py — Terminal rendering for PromptIQ.

All visual output lives here. Nothing else imports Click styling.
"""

import click
from typing import Optional


# ── Color helpers ─────────────────────────────────────────────────────────────

def score_color(value: float) -> str:
    if value >= 8:  return "green"
    if value >= 5:  return "yellow"
    return "red"


def score_bar(value: float, width: int = 12) -> str:
    filled = round(value * width / 10)
    return "█" * filled + "░" * (width - filled)


def score_stars(value: float) -> str:
    full  = int(value / 2)
    half  = 1 if (value % 2) >= 1 else 0
    empty = 5 - full - half
    return "★" * full + "◐" * half + "☆" * empty


# ── Commit display ─────────────────────────────────────────────────────────────

def show_commit(c: dict, show_content: bool = False):
    click.echo()
    click.secho(f"  commit  {c['hash']}  v{c.get('semver','?')}", fg="yellow", bold=True)
    if c.get("model"):
        click.secho(f"  Model:  {c['model']}", fg="cyan")
    if c.get("tags"):
        click.secho(f"  Tags:   {', '.join(c['tags'])}", fg="magenta")
    click.secho(f"  Date:   {c['timestamp'][:19].replace('T', ' ')}")
    click.echo()
    click.secho(f"      {c['message']}", bold=True)

    jr = c.get("judge_result")
    if jr:
        show_judge_summary(jr)

    if show_content:
        click.echo()
        click.secho("  " + "─" * 58, dim=True)
        for line in c["content"].splitlines():
            click.echo(f"  {line}")
        click.secho("  " + "─" * 58, dim=True)


def show_judge_summary(jr: dict):
    """Compact judge result for log view."""
    s = jr.get("static", {})
    if not s:
        return
    overall = jr.get("overall_score", s.get("overall", 0))
    click.echo()
    click.secho(f"  Quality Score  {score_stars(overall)}  {overall}/10",
                fg=score_color(overall), bold=True)


# ── Full judge report ─────────────────────────────────────────────────────────

def show_full_judge(jr: dict, name: str = ""):
    s       = jr.get("static", {})
    outputs = jr.get("outputs", [])
    compare = jr.get("compare")
    suggest = jr.get("suggestion")
    overall = jr.get("overall_score", 0)

    header = f" PromptIQ Report{' — ' + name if name else ''} "
    click.echo()
    click.secho("╔" + "═" * (len(header)) + "╗", fg="blue")
    click.secho("║" + header + "║", fg="blue", bold=True)
    click.secho("╚" + "═" * (len(header)) + "╝", fg="blue")
    click.echo()

    # ── Stage 1: Static ───────────────────────────────────────────────────────
    click.secho("  STAGE 1 — Static Analysis", fg="blue", bold=True)
    click.secho("  " + "─" * 50, dim=True)
    dims = [
        ("Clarity",        s.get("clarity",       0)),
        ("Specificity",    s.get("specificity",   0)),
        ("Conciseness",    s.get("conciseness",   0)),
        ("Instruction Q",  s.get("instruction_q", 0)),
        ("Robustness",     s.get("robustness",    0)),
    ]
    for label, val in dims:
        bar = score_bar(val)
        click.secho(f"  {label:<18} {bar} {val}/10", fg=score_color(val))

    click.echo()
    click.secho(f"  Feedback:", dim=True)
    click.echo(f"  {s.get('feedback','')}")

    if s.get("strengths"):
        click.echo()
        click.secho("  Strengths:", fg="green")
        for st in s["strengths"]:
            click.secho(f"  ✅ {st}", fg="green")

    if s.get("weaknesses"):
        click.echo()
        click.secho("  Weaknesses:", fg="red")
        for w in s["weaknesses"]:
            click.secho(f"  ⚠️  {w}", fg="yellow")

    # ── Stage 2: Output evals ─────────────────────────────────────────────────
    if outputs:
        click.echo()
        click.secho("  STAGE 2 — Output Evaluation", fg="blue", bold=True)
        click.secho("  " + "─" * 50, dim=True)
        for i, ev in enumerate(outputs, 1):
            avg = round((ev.get("relevance",0) + ev.get("instruction_follow",0) + ev.get("quality",0)) / 3, 1)
            click.secho(f"  Test {i}: {ev['test_input'][:55]}{'...' if len(ev['test_input'])>55 else ''}", bold=True)
            click.secho(f"    Relevance:     {score_bar(ev.get('relevance',0),8)} {ev.get('relevance',0)}/10", fg=score_color(ev.get("relevance",0)))
            click.secho(f"    Instructions:  {score_bar(ev.get('instruction_follow',0),8)} {ev.get('instruction_follow',0)}/10", fg=score_color(ev.get("instruction_follow",0)))
            click.secho(f"    Quality:       {score_bar(ev.get('quality',0),8)} {ev.get('quality',0)}/10", fg=score_color(ev.get("quality",0)))
            click.secho(f"    Verdict:       {ev.get('verdict','')}", dim=True)
            if ev.get("issues"):
                for iss in ev["issues"]:
                    click.secho(f"    ⚠️  {iss}", fg="yellow")
            click.echo()

    # ── Stage 3: Compare ──────────────────────────────────────────────────────
    if compare:
        click.secho("  STAGE 3 — Version Comparison", fg="blue", bold=True)
        click.secho("  " + "─" * 50, dim=True)
        delta     = compare.get("delta", 0)
        winner    = compare.get("winner", "tie")
        delta_col = "green" if delta > 0 else ("red" if delta < 0 else "yellow")
        delta_sym = "▲" if delta > 0 else ("▼" if delta < 0 else "─")

        click.secho(f"  Old version:  {compare.get('score_a',0):.1f}/10", fg=score_color(compare.get("score_a",0)))
        click.secho(f"  New version:  {compare.get('score_b',0):.1f}/10", fg=score_color(compare.get("score_b",0)))
        click.secho(f"  Delta:        {delta_sym} {abs(delta):.1f} pts", fg=delta_col, bold=True)
        click.echo()
        winner_text = {"a": "Old version wins ✗", "b": "New version wins ✓", "tie": "Tie —"}.get(winner, "")
        click.secho(f"  {winner_text}", bold=True, fg="green" if winner=="b" else ("red" if winner=="a" else "yellow"))
        click.echo(f"  {compare.get('reasoning','')}")

        if compare.get("improvements"):
            click.echo()
            click.secho("  Improvements:", fg="green")
            for im in compare["improvements"]:
                click.secho(f"  ✅ {im}", fg="green")

        if compare.get("regressions"):
            click.echo()
            click.secho("  Regressions:", fg="red")
            for rg in compare["regressions"]:
                click.secho(f"  ❌ {rg}", fg="red")

    # ── Stage 4: Suggestion ───────────────────────────────────────────────────
    if suggest:
        click.echo()
        click.secho("  STAGE 4 — Auto-Improvement", fg="blue", bold=True)
        click.secho("  " + "─" * 50, dim=True)
        click.secho(f"  Expected gain: {suggest.get('expected_gain','')}", fg="green")
        click.echo()
        click.secho("  Changes made:", bold=True)
        for ch in suggest.get("changes", []):
            click.secho(f"  → {ch}", fg="cyan")
        click.echo()
        click.secho("  Improved prompt saved to: suggested.txt", fg="green")

    # ── Overall ───────────────────────────────────────────────────────────────
    click.echo()
    click.secho("  " + "═" * 50, fg="blue")
    click.secho(
        f"  OVERALL  {score_stars(overall)}  {overall}/10",
        fg=score_color(overall), bold=True
    )
    click.secho("  " + "═" * 50, fg="blue")
    click.secho(f"  Provider: {jr.get('provider','')}", dim=True)
    click.echo()


# ── A/B display ───────────────────────────────────────────────────────────────

def show_ab_result(result: dict, label_a: str, label_b: str):
    click.echo()
    click.secho("  A/B TEST RESULTS", fg="blue", bold=True)
    click.secho("  " + "═" * 50, fg="blue")
    click.echo()

    for i, tc in enumerate(result.get("test_cases", []), 1):
        w = tc.get("winner", "tie")
        w_label = {"a": f"→ {label_a}", "b": f"→ {label_b}", "tie": "→ Tie"}.get(w, "")
        w_color = {"a": "yellow", "b": "green", "tie": "cyan"}.get(w, "white")
        click.secho(f"  Case {i}  {tc['test_input'][:50]}{'...' if len(tc['test_input'])>50 else ''}", bold=True)
        click.secho(f"  {label_a}: {tc.get('score_a',0)}/10  {label_b}: {tc.get('score_b',0)}/10  {w_label}", fg=w_color)
        click.secho(f"  {tc.get('reasoning','')}", dim=True)
        click.echo()

    click.secho("  " + "─" * 50, dim=True)
    click.secho(f"  {label_a} wins:    {result.get('wins_a',0)}")
    click.secho(f"  {label_b} wins:    {result.get('wins_b',0)}")
    click.secho(f"  Ties:         {result.get('ties',0)}")
    click.echo()

    avg_a   = result.get("avg_score_a", 0)
    avg_b   = result.get("avg_score_b", 0)
    delta   = result.get("delta", 0)
    winner  = result.get("overall_winner", "tie")
    d_color = "green" if delta > 0 else ("red" if delta < 0 else "yellow")

    click.secho(f"  Avg {label_a}: {avg_a}/10", fg=score_color(avg_a))
    click.secho(f"  Avg {label_b}: {avg_b}/10", fg=score_color(avg_b))
    click.secho(f"  Delta:    {'▲' if delta>0 else '▼'} {abs(delta):.1f} pts", fg=d_color, bold=True)
    click.echo()

    winner_name = label_b if winner=="b" else (label_a if winner=="a" else "Tie")
    winner_color = "green" if winner=="b" else ("yellow" if winner=="a" else "cyan")
    click.secho(f"  WINNER: {winner_name}", fg=winner_color, bold=True)
    click.echo()
    click.echo(f"  {result.get('summary','')}")
    click.echo()


# ── Diff display ──────────────────────────────────────────────────────────────

def show_diff(tokens, stats: dict, hash_a: str, hash_b: str, sim: float):
    click.echo()
    click.secho(f"  --- {hash_a}", fg="red")
    click.secho(f"  +++ {hash_b}", fg="green")
    click.echo()
    for kind, token in tokens:
        if kind == "equal":
            click.echo(token, nl=False)
        elif kind == "added":
            click.secho(token, fg="green", nl=False)
        elif kind == "removed":
            click.secho(token, fg="red", nl=False)
    click.echo("\n")
    click.secho(
        f"  +{stats['words_added']} words  "
        f"-{stats['words_removed']} words  "
        f"+{stats['lines_added']} lines  "
        f"-{stats['lines_removed']} lines  "
        f"{sim*100:.0f}% similar",
        dim=True,
    )
    click.echo()
