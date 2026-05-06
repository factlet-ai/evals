"""Tier 1 eval runner — generates model responses across conditions × tasks × models.

For each task, runs 9 conditions (3 grounding strategies × 3 models):
  C1-C3: Baseline (no factbook)              — Claude / GPT / Gemini
  C4-C6: Naive grounding (factbook as MD)    — Claude / GPT / Gemini
  C7-C9: Factlet-grounded (vendor renderer)  — Claude / GPT / Gemini

Outputs JSONL to <output>/raw.jsonl with one line per (task, condition) run.

Usage:
  export ANTHROPIC_API_KEY=sk-ant-...
  export OPENAI_API_KEY=sk-...
  export GOOGLE_API_KEY=AIza...
  python run.py --tasks ../tier1/tasks --factbooks ../tier1/factbooks --output ../results/2026-05-DD
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# Pinned model snapshots — change requires PREREG amendment
MODELS = {
    "claude": {"provider": "anthropic", "snapshot": "claude-sonnet-4-6"},
    "gpt": {"provider": "openai", "snapshot": "gpt-4-1"},
    "gemini": {"provider": "google", "snapshot": "gemini-2.0-flash"},
}

CONDITIONS = ["baseline", "naive", "grounded"]


def load_factbook(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def render_factbook_for_naive(factbook: dict) -> str:
    """Naive grounding — factbook content as flat markdown.

    Mimics what a developer would do if they pasted their docs into
    the system prompt without using the protocol's renderers.
    """
    lines = ["# Project knowledge", ""]
    for f in factbook["content"]:
        lines.append(f"- {f['statement']}")
        if f.get("sources"):
            lines.append(f"  (sources: {', '.join(str(s) for s in f['sources'])})")
    return "\n".join(lines)


def render_factbook_for_claude(factlets: list[dict]) -> str:
    """Per the Factlet Protocol §8 — XML for Claude system blocks."""
    parts = ["<factbook>"]
    for f in factlets:
        parts.append(
            f'  <factlet id="{f["id"]}" confidence="{f["confidence"]:.2f}">'
            f"\n    <statement>{f['statement']}</statement>"
            f"\n    <sources>{', '.join(str(s) for s in f['sources'])}</sources>"
            f"\n  </factlet>"
        )
    parts.append("</factbook>")
    return "\n".join(parts)


def render_factbook_for_gpt(factlets: list[dict]) -> str:
    """Per the Factlet Protocol §8 — markdown for GPT."""
    lines = ["## Factbook (private team facts — defer over training data)"]
    for f in factlets:
        lines.append(
            f"- **{f['id']}** ({f['confidence']:.2f}): {f['statement']} "
            f"_(sources: {', '.join(str(s) for s in f['sources'])})_"
        )
    return "\n".join(lines)


def render_factbook_for_gemini(factlets: list[dict]) -> str:
    """Per the Factlet Protocol §8 — systemInstruction for Gemini."""
    lines = [
        "You have access to a private Factbook with team-specific truths.",
        "When answering, defer to factlets over your training data.",
        "Cite the factlet id (e.g. 'per f001') when you use one.",
        "If no factlet covers part of the question, say so explicitly.",
        "",
        "## Factbook",
    ]
    for f in factlets:
        lines.append(
            f"- {f['id']} (confidence {f['confidence']:.2f}): {f['statement']} "
            f"[sources: {', '.join(str(s) for s in f['sources'])}]"
        )
    return "\n".join(lines)


def build_system(model: str, condition: str, factbook: dict) -> str | None:
    if condition == "baseline":
        return None
    facts = [f for f in factbook["content"] if not f.get("archived", False)]
    if condition == "naive":
        return render_factbook_for_naive(factbook)
    # grounded
    if model == "claude":
        return render_factbook_for_claude(facts)
    if model == "gpt":
        return render_factbook_for_gpt(facts)
    if model == "gemini":
        return render_factbook_for_gemini(facts)
    raise ValueError(f"unknown model: {model}")


def call_claude(system: str | None, user: str, model_snapshot: str) -> dict:
    import anthropic

    client = anthropic.Anthropic()
    kwargs = {"model": model_snapshot, "max_tokens": 1024, "temperature": 0,
              "messages": [{"role": "user", "content": user}]}
    if system:
        kwargs["system"] = system
    t0 = time.time()
    resp = client.messages.create(**kwargs)
    return {
        "text": resp.content[0].text,
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
        "latency_ms": int((time.time() - t0) * 1000),
    }


def call_gpt(system: str | None, user: str, model_snapshot: str) -> dict:
    import openai

    client = openai.OpenAI()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    t0 = time.time()
    resp = client.chat.completions.create(
        model=model_snapshot, messages=messages, max_tokens=1024, temperature=0,
    )
    return {
        "text": resp.choices[0].message.content,
        "input_tokens": resp.usage.prompt_tokens,
        "output_tokens": resp.usage.completion_tokens,
        "latency_ms": int((time.time() - t0) * 1000),
    }


def call_gemini(system: str | None, user: str, model_snapshot: str) -> dict:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY") or os.environ["GOOGLE_API_KEY"])
    config = types.GenerateContentConfig(
        system_instruction=system, max_output_tokens=1024, temperature=0,
    ) if system else types.GenerateContentConfig(max_output_tokens=1024, temperature=0)
    t0 = time.time()
    resp = client.models.generate_content(
        model=model_snapshot, contents=user, config=config,
    )
    usage = resp.usage_metadata
    return {
        "text": resp.text,
        "input_tokens": getattr(usage, "prompt_token_count", 0) or 0,
        "output_tokens": getattr(usage, "candidates_token_count", 0) or 0,
        "latency_ms": int((time.time() - t0) * 1000),
    }


CALLERS = {"claude": call_claude, "gpt": call_gpt, "gemini": call_gemini}


def run_one(task: dict, factbook: dict, model: str, condition: str) -> dict:
    snapshot = MODELS[model]["snapshot"]
    system = build_system(model, condition, factbook)
    user = task["query"]
    try:
        result = CALLERS[model](system, user, snapshot)
        return {
            "task_id": task["id"], "model": model, "condition": condition,
            "snapshot": snapshot, "system_provided": system is not None,
            "ok": True, **result,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "task_id": task["id"], "model": model, "condition": condition,
            "snapshot": snapshot, "system_provided": system is not None,
            "ok": False, "error": str(e),
            "ts": datetime.now(timezone.utc).isoformat(),
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True, help="Path to tier1/tasks/")
    ap.add_argument("--factbooks", required=True, help="Path to tier1/factbooks/")
    ap.add_argument("--output", required=True, help="Output directory (raw.jsonl will land here)")
    ap.add_argument("--models", default="claude,gpt,gemini",
                    help="Comma-separated subset of {claude,gpt,gemini} to run")
    ap.add_argument("--conditions", default="baseline,naive,grounded",
                    help="Comma-separated subset of conditions")
    ap.add_argument("--task-filter", default=None,
                    help="Substring filter on task IDs (e.g. payments)")
    args = ap.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / "raw.jsonl"

    models = args.models.split(",")
    conditions = args.conditions.split(",")
    tasks_root = Path(args.tasks)
    factbook_root = Path(args.factbooks)

    task_files = sorted(tasks_root.rglob("*.yaml"))
    tasks = []
    for tp in task_files:
        t = yaml.safe_load(tp.read_text())
        if args.task_filter and args.task_filter not in t["id"]:
            continue
        tasks.append(t)

    factbook_cache: dict[str, dict] = {}

    print(f"Tasks: {len(tasks)}  Models: {models}  Conditions: {conditions}")
    total = len(tasks) * len(models) * len(conditions)
    print(f"Total runs: {total}")

    n = 0
    with open(raw_path, "w") as out:
        for task in tasks:
            fb_path = factbook_root / task["factbook"]
            if str(fb_path) not in factbook_cache:
                factbook_cache[str(fb_path)] = load_factbook(fb_path)
            fb = factbook_cache[str(fb_path)]
            for model in models:
                for condition in conditions:
                    n += 1
                    print(f"[{n}/{total}] {task['id']} / {model} / {condition}")
                    result = run_one(task, fb, model, condition)
                    out.write(json.dumps(result) + "\n")
                    out.flush()

    print(f"\nDone. Raw output: {raw_path}")


if __name__ == "__main__":
    sys.exit(main())
