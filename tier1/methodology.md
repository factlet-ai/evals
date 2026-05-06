# Tier 1 methodology

This document describes how Tier 1 evals are designed, run, and scored. It is locked at pre-registration time (see `PREREG.md`); changes require a new pre-reg + diff in the published report.

## Design summary

| Dimension | Choice | Rationale |
|---|---|---|
| Task count | **6 in current scaffold** (target before seal: 20 — 7 payments + 7 frontend + 6 ML pipeline) | Methodology validation; not statistically significant at any size. Tier 2 grows to N≥100. |
| Conditions | 3: baseline (no factbook) / naive grounding (markdown) / Factlet-grounded | The primary comparison is **with-factbook (any rendering) vs no-factbook**. The naive-vs-grounded split is reported as a diagnostic on whether the structured per-vendor render provides additional lift at the rendering layer beyond naive markdown grounding. |
| Models | 3: Claude Sonnet 4.6, GPT-4.1, Gemini 2.0 Flash (snapshots pinned in PREREG.md) | Cross-vendor coverage; pinned snapshots for reproducibility. |
| Temperature | 0 (capability measurement) | One purpose. K=1 acknowledges Tier 1 doesn't characterize stochasticity. Tier 2 adds K=10 at temp=1. Note: temp=0 ≠ bitwise reproducibility (none of the 3 providers guarantee it). |
| Replicates | K=1 | See above. |
| Judge architecture | 3-judge: GPT-4.1 (primary), Claude Sonnet 4.6 (secondary), Gemini 2.0 Flash (secondary) | Different family from primary generator. Inter-judge agreement reported per metric. Same-family Claude judging Claude is acknowledged risk; mitigated by 2/3 majority requirement. |
| Per-metric judge calls | Yes (no single multi-dim call) | Avoids halo bias. |
| Sub-metrics | Citation correctness, contradiction count, coverage honesty, quality (1-5), risk-of-shipping | Three of four are objective-heavy. |
| Composite headline (Tier 2 only) | Task pass-rate = `must_cite ✓ AND contradictions == 0 AND coverage_honesty ✓ AND quality ≥ 4` | Three of four components are objective. Pre-registered. |
| Position-bias control | Random shuffle of (baseline, naive, grounded) order in judge prompts | Standard practice for pairwise judging. |
| Calibration anchors | 2-3 worked examples per metric in each judge prompt | Reduces score variance. |

## What Tier 1 publishes

- Eval infrastructure (this repo)
- The current task set (with author provenance per task) — see `tasks/`
- Raw runs as JSONL in `results/YYYY-MM-DD/raw.jsonl` (when runs are committed)
- Scored runs in `results/YYYY-MM-DD/scored.jsonl`
- Per-task qualitative writeups for representative tasks (one per domain)
- Sub-metric distributions per (model, condition) — without aggregate "headline" claims

## What Tier 1 does NOT publish

- Aggregate "X% → Y%" headline numbers (see `docs/why-no-headline-yet.md`)
- Statistical significance tests
- Confidence intervals on aggregate proportions (would be misleading at N=20)
- Cost claims (single-turn evals can't capture multi-turn correction loops)

## Known limitations (transparent)

1. **N=20 is small.** Per (model, condition) cell after analysis, you have 20 binary outcomes — Wilson 95% CI is roughly ±20pp. We don't claim significance.
2. **Author bias risk.** Tier 1 tasks are mostly authored by the protocol author. The construct-validity fix (≥5 externally-authored tasks) is a Tier 2 ship-gate.
3. **Factbook size is small.** Each example factbook has 5-8 factlets. Real factbooks have 50-200. Tier 2 will use larger factbooks.
4. **Distractor injection not tested in Tier 1.** Tier 2 adds tasks with irrelevant factlets in the context to test attention.
5. **No vanilla-RAG comparison in Tier 1.** Tier 2 adds an `embedding-RAG` arm.
6. **Judge-prompt design effect.** 80% of LLM-as-judge variance lives in prompt design; we mitigate via per-metric calls and calibration anchors but don't eliminate.
7. **Data-leakage check is heuristic.** We can't verify whether example factbook content is in any specific model's training set.

## Why no headline number yet

See [`../docs/why-no-headline-yet.md`](../docs/why-no-headline-yet.md).

## Sample-size analysis (back-of-envelope)

Detecting a 15-percentage-point delta in a binary outcome at 80% power requires N ≈ 80 per condition (Wilson). At N=20, our minimum detectable effect is ~25-30pp. Real protocol effects are likely 10-20pp on most tasks → undetectable at this sample size. This is why Tier 1 ships methodology without a headline number.

Tier 2 grows N to ≥100 per condition.
