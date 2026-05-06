"""Aggregate scored.jsonl into a per-task / per-condition table + markdown report.

For each (task, model, condition) record:
  - For each metric, take median (ordinal) or majority (binary/categorical)
    across the 3 judges as the "consensus" score.
  - Track per-judge scores too (audit trail; for inter-judge agreement reporting).

Tier 1 explicitly does NOT publish a headline aggregate — see
docs/why-no-headline-yet.md. This script writes:
  - scored_summary.md      — per-task table; deltas if you want to look but
                             clearly labeled "indicative, not headline-grade"
  - inter_judge_agreement.md — per-metric agreement %
  - PER_TASK_DETAIL.md     — full per-judge breakdown for transparency
"""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path


def consensus(metric: str, judge_scores: list):
    parsed = [s["parsed"] for s in judge_scores if s.get("parsed") is not None]
    if not parsed:
        return None
    if metric in ("citation", "coverage"):
        return Counter(parsed).most_common(1)[0][0]
    if metric == "contradiction":
        return int(statistics.median(parsed))
    if metric == "quality":
        return float(statistics.median(parsed))
    if metric == "risk":
        return Counter(parsed).most_common(1)[0][0]
    return None


def load_scored(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def per_record_consensus(rec: dict) -> dict | None:
    if not rec.get("scores"):
        return None
    metrics = ["citation", "contradiction", "coverage", "quality", "risk"]
    out = {}
    for m in metrics:
        per_judge = [j[m] for j in rec["scores"].values() if m in j]
        out[m] = consensus(m, per_judge)
    return out


def write_summary(records: list[dict], out_dir: Path) -> None:
    rows: dict[tuple[str, str, str], dict] = {}
    for rec in records:
        c = per_record_consensus(rec)
        if c is None:
            continue
        rows[(rec["task_id"], rec["model"], rec["condition"])] = c

    lines = [
        "# Tier 1 — Indicative Summary (NOT a headline)",
        "",
        "**Read this first:** the numbers below come from N=20 tasks per condition. "
        "Per the methodology doc, this sample is below the threshold for publishing "
        "an aggregate headline (need ~80/condition for 15pp detection at 80% power). "
        "These rows exist for raw transparency and for the next-tier scope decisions, "
        "not for marketing.",
        "",
        "## Per-task consensus (median across 3 judges)",
        "",
        "| Task | Model | Condition | Citation | Contradictions | Coverage | Quality | Risk |",
        "|------|-------|-----------|----------|----------------|----------|---------|------|",
    ]
    for (task, model, cond), c in sorted(rows.items()):
        lines.append(
            f"| {task} | {model} | {cond} | "
            f"{c.get('citation')} | {c.get('contradiction')} | {c.get('coverage')} | "
            f"{c.get('quality')} | {c.get('risk')} |"
        )

    (out_dir / "scored_summary.md").write_text("\n".join(lines) + "\n")
    print(f"Wrote {out_dir / 'scored_summary.md'}")


def write_agreement(records: list[dict], out_dir: Path) -> None:
    metrics = ["citation", "contradiction", "coverage", "quality", "risk"]
    agreement_counts: dict[str, list[float]] = defaultdict(list)
    for rec in records:
        if not rec.get("scores"):
            continue
        for m in metrics:
            parsed = [j[m].get("parsed") for j in rec["scores"].values()
                      if m in j and j[m].get("parsed") is not None]
            if len(parsed) < 2:
                continue
            top, _ = Counter(parsed).most_common(1)[0]
            agreement_counts[m].append(parsed.count(top) / len(parsed))

    lines = [
        "# Inter-judge agreement (per-metric)",
        "",
        "Fraction of judges that match the modal score, averaged across all (task, model, condition) records.",
        "Lower numbers = more judge disagreement = lower confidence in that metric for headline use.",
        "",
        "| Metric | Mean agreement | N records |",
        "|--------|----------------|-----------|",
    ]
    for m in metrics:
        vals = agreement_counts[m]
        if not vals:
            lines.append(f"| {m} | — | 0 |")
            continue
        lines.append(f"| {m} | {statistics.mean(vals):.2f} | {len(vals)} |")

    (out_dir / "inter_judge_agreement.md").write_text("\n".join(lines) + "\n")
    print(f"Wrote {out_dir / 'inter_judge_agreement.md'}")


def write_detail(records: list[dict], out_dir: Path) -> None:
    lines = ["# Per-task detail (raw judge scores)", ""]
    for rec in records:
        if not rec.get("scores"):
            continue
        lines.append(f"## {rec['task_id']} / {rec['model']} / {rec['condition']}")
        lines.append("")
        for judge, mscores in rec["scores"].items():
            row = ", ".join(f"{m}={s.get('parsed')}" for m, s in mscores.items())
            lines.append(f"- **{judge}**: {row}")
        lines.append("")
        lines.append(f"<details><summary>Response (truncated)</summary>\n\n```\n{rec['text'][:600]}\n```\n\n</details>")
        lines.append("")

    (out_dir / "PER_TASK_DETAIL.md").write_text("\n".join(lines) + "\n")
    print(f"Wrote {out_dir / 'PER_TASK_DETAIL.md'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scored", required=True, help="Path to scored.jsonl from score.py")
    ap.add_argument("--output", required=True, help="Output directory for markdown reports")
    args = ap.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    records = load_scored(Path(args.scored))

    write_summary(records, out_dir)
    write_agreement(records, out_dir)
    write_detail(records, out_dir)


if __name__ == "__main__":
    main()
