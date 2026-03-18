"""
export.py — Export prompt history to Markdown, JSON, or score report.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


def export_json(data: dict, output_path: Optional[str] = None) -> str:
    name = data["name"]
    output_path = output_path or f"{name}_history.json"
    clean = {
        "name":        name,
        "exported_at": datetime.utcnow().isoformat() + "Z",
        "branches":    {},
    }
    for branch, commits in data.get("branches", {}).items():
        clean["branches"][branch] = [
            {k: v for k, v in c.items()}
            for c in commits
        ]
    Path(output_path).write_text(json.dumps(clean, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def export_markdown(data: dict, output_path: Optional[str] = None) -> str:
    name        = data["name"]
    output_path = output_path or f"{name}_changelog.md"
    current_br  = data.get("current_branch", "main")
    lines       = []

    lines += [
        f"# Prompt Changelog: `{name}`\n",
        f"> Exported: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n",
        f"**Current branch:** `{current_br}`  ",
        f"**Branches:** {', '.join(f'`{b}`' for b in data.get('branches', {}).keys())}\n",
        "---\n",
    ]

    for branch, commits in data.get("branches", {}).items():
        if not commits:
            continue
        lines.append(f"## Branch: `{branch}`\n")
        for c in reversed(commits):
            semver = c.get("semver", "?")
            lines.append(f"### v{semver} — `{c['hash']}` — {c['message']}\n")
            lines.append(f"**Date:** {c['timestamp'][:19].replace('T',' ')} UTC  ")
            if c.get("model"):  lines.append(f"**Model:** `{c['model']}`  ")
            if c.get("tags"):   lines.append(f"**Tags:** {' '.join(f'`{t}`' for t in c['tags'])}  ")
            lines.append("")

            jr = c.get("judge_result")
            if jr:
                s = jr.get("static", {})
                lines += [
                    "**Quality Scores:**\n",
                    "| Dimension | Score |",
                    "|-----------|-------|",
                    f"| Clarity | {s.get('clarity','—')}/10 |",
                    f"| Specificity | {s.get('specificity','—')}/10 |",
                    f"| Conciseness | {s.get('conciseness','—')}/10 |",
                    f"| Instruction Q | {s.get('instruction_q','—')}/10 |",
                    f"| Robustness | {s.get('robustness','—')}/10 |",
                    f"| **Overall** | **{jr.get('overall_score','—')}/10** |",
                    "",
                ]
                if s.get("feedback"):
                    lines.append(f"> {s['feedback']}\n")
                if s.get("strengths"):
                    lines += ["**Strengths:**"] + [f"- ✅ {st}" for st in s["strengths"]] + [""]
                if s.get("weaknesses"):
                    lines += ["**Weaknesses:**"] + [f"- ⚠️ {w}" for w in s["weaknesses"]] + [""]

                outputs = jr.get("outputs", [])
                if outputs:
                    lines.append("**Test Results:**\n")
                    for i, ev in enumerate(outputs, 1):
                        avg = round((ev.get("relevance",0)+ev.get("instruction_follow",0)+ev.get("quality",0))/3,1)
                        lines += [
                            f"_Test {i}:_ `{ev.get('test_input','')[:60]}`",
                            f"Score: {avg}/10 — {ev.get('verdict','')}",
                            "",
                        ]

                comp = jr.get("compare")
                if comp:
                    delta = comp.get("delta", 0)
                    trend = f"📈 +{delta}" if delta > 0 else (f"📉 {delta}" if delta < 0 else "➡️  0")
                    lines += [
                        f"**vs Previous Version:** {trend} ({comp.get('score_a','?')} → {comp.get('score_b','?')})",
                        f"> {comp.get('reasoning','')}",
                        "",
                    ]

            lines += [
                "**Prompt Content:**\n",
                "```",
                c["content"],
                "```\n",
                "---\n",
            ]

    Path(output_path).write_text("\n".join(lines), encoding="utf-8")
    return output_path


def export_score_report(data: dict, output_path: Optional[str] = None) -> str:
    name        = data["name"]
    output_path = output_path or f"{name}_score_report.md"
    lines       = [
        f"# Score Evolution Report: `{name}`\n",
        f"> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n",
    ]

    for branch, commits in data.get("branches", {}).items():
        scored = [c for c in commits if c.get("judge_result")]
        if not scored:
            continue
        lines += [
            f"## Branch: `{branch}`\n",
            "| Version | Hash | Message | Clarity | Spec. | Concise | Instr. | Robust | Overall |",
            "|---------|------|---------|---------|-------|---------|--------|--------|---------|",
        ]
        for c in scored:
            s  = c["judge_result"].get("static", {})
            ov = c["judge_result"].get("overall_score", "—")
            lines.append(
                f"| v{c.get('semver','?')} | `{c['hash']}` | {c['message']} "
                f"| {s.get('clarity','—')} | {s.get('specificity','—')} "
                f"| {s.get('conciseness','—')} | {s.get('instruction_q','—')} "
                f"| {s.get('robustness','—')} | **{ov}** |"
            )
        scores = [c["judge_result"].get("overall_score", 0) for c in scored]
        if len(scores) >= 2:
            delta = scores[-1] - scores[0]
            trend = f"📈 +{delta:.1f}" if delta > 0 else (f"📉 {delta:.1f}" if delta < 0 else "➡️  No change")
            lines.append(f"\n**Trend:** {trend} (v{scored[0].get('semver','?')} {scores[0]} → v{scored[-1].get('semver','?')} {scores[-1]})\n")

    Path(output_path).write_text("\n".join(lines), encoding="utf-8")
    return output_path
