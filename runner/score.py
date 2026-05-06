"""Multi-judge LLM-as-judge scorer for Tier 1 raw runs.

Reads <output>/raw.jsonl produced by run.py and writes <output>/scored.jsonl
with per-judge per-metric scores attached to each (task, condition) record.

Judges (3 — primary + 2 secondary, no same-family for this run):
  - GPT-4.1     (primary; cross-family vs Claude target, hardest grader)
  - Claude 4.6  (secondary)
  - Gemini 2.0  (secondary)

For each (task, condition) record we evaluate 5 metrics with one judge call
each (per metric per judge — keeps prompts focused and aids calibration):
  - citation        (0/1)  — must_cite factlets present
  - contradiction   (int)  — count of factlets contradicted
  - coverage        (0/1)  — coverage_honesty
  - quality         (1-5)  — overall quality
  - risk            (low|medium|high) — risk of shipping

Aggregation across judges = simple majority for binary/categorical, median
for ordinal — the rules live in aggregate.py so this stage stays raw.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

JUDGES = {
    "gpt": {"snapshot": "gpt-4-1", "role": "primary"},
    "claude": {"snapshot": "claude-sonnet-4-6", "role": "secondary"},
    "gemini": {"snapshot": "gemini-2.0-flash", "role": "secondary"},
}

METRICS = ["citation", "contradiction", "coverage", "quality", "risk"]


def load_prompt(prompts_dir: Path, metric: str) -> str:
    name = "coverage" if metric == "coverage" else metric
    return (prompts_dir / f"{name}.md").read_text()


def load_tasks(tasks_root: Path) -> dict[str, dict]:
    out = {}
    for tp in tasks_root.rglob("*.yaml"):
        t = yaml.safe_load(tp.read_text())
        out[t["id"]] = t
    return out


def load_factbooks(factbook_root: Path, tasks: dict[str, dict]) -> dict[str, dict]:
    cache: dict[str, dict] = {}
    for t in tasks.values():
        fp = factbook_root / t["factbook"]
        if str(fp) not in cache:
            cache[str(fp)] = yaml.safe_load(fp.read_text())
    return cache


def relevant_factlets(task: dict, factbook: dict) -> list[dict]:
    keep = set(task["expected_behavior"].get("must_cite", []))
    keep |= set(task["expected_behavior"].get("must_not_contradict", []))
    return [f for f in factbook["content"] if f["id"] in keep]


def build_judge_input(metric: str, task: dict, factbook: dict, response_text: str) -> str:
    facts = relevant_factlets(task, factbook)
    fb_summary = "\n".join(f"- {f['id']}: {f['statement']}" for f in facts) or "(none in scope)"
    parts = [f"## Query\n{task['query']}", f"## Factbook (in-scope facts)\n{fb_summary}"]

    if metric == "citation":
        parts.append(
            f"## must_cite factlet ids\n{task['expected_behavior'].get('must_cite', [])}"
        )
    if metric == "contradiction":
        parts.append(
            f"## must_not_contradict factlet ids\n"
            f"{task['expected_behavior'].get('must_not_contradict', [])}"
        )
    if metric == "coverage":
        parts.append(
            f"## must_acknowledge_uncovered\n"
            f"{task['expected_behavior'].get('must_acknowledge_uncovered', False)}"
        )
    if metric == "quality":
        parts.append(f"## ground_truth_answer\n{task.get('ground_truth_answer', '(none)')}")

    parts.append(f"## Response to evaluate\n{response_text}")
    return "\n\n".join(parts)


def call_judge_gpt(system: str, user: str, snapshot: str) -> str:
    import openai
    client = openai.OpenAI()
    resp = client.chat.completions.create(
        model=snapshot,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=64, temperature=0,
    )
    return resp.choices[0].message.content.strip()


def call_judge_claude(system: str, user: str, snapshot: str) -> str:
    import anthropic
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=snapshot, max_tokens=64, temperature=0,
        system=system, messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text.strip()


def call_judge_gemini(system: str, user: str, snapshot: str) -> str:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY") or os.environ["GOOGLE_API_KEY"])
    config = types.GenerateContentConfig(
        system_instruction=system, max_output_tokens=64, temperature=0,
    )
    resp = client.models.generate_content(model=snapshot, contents=user, config=config)
    return resp.text.strip()


JUDGE_CALLERS = {"gpt": call_judge_gpt, "claude": call_judge_claude, "gemini": call_judge_gemini}


def parse_score(metric: str, raw: str):
    raw = raw.strip().lower()
    if metric in ("citation", "coverage"):
        return 1 if raw.startswith("1") else 0
    if metric == "contradiction":
        try:
            return int("".join(c for c in raw if c.isdigit()) or "0")
        except ValueError:
            return 0
    if metric == "quality":
        for c in raw:
            if c in "12345":
                return int(c)
        return None
    if metric == "risk":
        for k in ("high", "medium", "low"):
            if k in raw:
                return k
        return None
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True, help="Path to raw.jsonl produced by run.py")
    ap.add_argument("--tasks", required=True, help="Path to tier1/tasks/")
    ap.add_argument("--factbooks", required=True, help="Path to tier1/factbooks/")
    ap.add_argument("--prompts", required=True, help="Path to tier1/judge-prompts/")
    ap.add_argument("--output", required=True, help="Path to write scored.jsonl")
    ap.add_argument("--judges", default="gpt,claude,gemini")
    ap.add_argument("--metrics", default=",".join(METRICS))
    args = ap.parse_args()

    tasks = load_tasks(Path(args.tasks))
    factbooks = load_factbooks(Path(args.factbooks), tasks)
    prompts = {m: load_prompt(Path(args.prompts), m) for m in args.metrics.split(",")}

    judges = args.judges.split(",")
    metrics = args.metrics.split(",")

    raw_lines = [json.loads(line) for line in Path(args.raw).read_text().splitlines() if line.strip()]
    print(f"Records to score: {len(raw_lines)} × {len(judges)} judges × {len(metrics)} metrics "
          f"= {len(raw_lines) * len(judges) * len(metrics)} judge calls")

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(out_path, "w") as out:
        for rec in raw_lines:
            if not rec.get("ok"):
                rec["scores"] = None
                out.write(json.dumps(rec) + "\n")
                continue
            task = tasks[rec["task_id"]]
            fb_path = Path(args.factbooks) / task["factbook"]
            fb = factbooks[str(fb_path)]
            scores: dict = {}
            for judge in judges:
                snap = JUDGES[judge]["snapshot"]
                caller = JUDGE_CALLERS[judge]
                scores[judge] = {}
                for metric in metrics:
                    n += 1
                    user = build_judge_input(metric, task, fb, rec["text"])
                    try:
                        raw_score = caller(prompts[metric], user, snap)
                        scores[judge][metric] = {"raw": raw_score, "parsed": parse_score(metric, raw_score)}
                    except Exception as e:
                        scores[judge][metric] = {"raw": None, "parsed": None, "error": str(e)}
                    if n % 25 == 0:
                        print(f"[{n} judge calls done]")
            rec["scores"] = scores
            rec["scored_at"] = datetime.now(timezone.utc).isoformat()
            out.write(json.dumps(rec) + "\n")
            out.flush()

    print(f"Done. Scored output: {out_path}")


if __name__ == "__main__":
    sys.exit(main())
