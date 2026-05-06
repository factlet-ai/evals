# Results — Tier 1 scaffold run (N=6, May 2026)

> **Read this first.** N=6 tasks per condition. Single-author task set. This run is published as transparency over result-quality — the eval was pre-registered, run, and the data is shown even though N is too small for a headline aggregate claim. Do not extract a single-percentage figure from this document.
>
> The point of publishing it: pre-registration without published runs is incomplete, and the per-task heterogeneity (where it works, where it doesn't) is more interesting than any aggregate would be.

## What was run

- **6 tasks**, 3 domains (payments / frontend / ml-pipeline), all authored by the protocol author. **Single-author construct-validity gap acknowledged.** Tier 2 ship-gate is ≥5 externally-authored tasks before any further publish.
- **3 conditions × 3 models** = 9 cells per task → 54 generations
- **3 judges, per-metric**, 5 metrics each → 810 judge calls (0 parse failures)
- temp=0, K=1 (capability measurement, not stochasticity characterization)
- Pinned snapshots: `claude-sonnet-4-6`, `gpt-4.1`, `gemini-2.0-flash`
- Cost ~$2.50; wall clock ~50 min serial

Raw data: [`../results/v2/raw.jsonl`](../results/v2/raw.jsonl). Per-judge per-metric scores: [`../results/v2/scored.jsonl`](../results/v2/scored.jsonl). Inter-judge agreement: [`../results/v2/inter_judge_agreement.md`](../results/v2/inter_judge_agreement.md). Per-cell consensus: [`../results/v2/scored_summary.md`](../results/v2/scored_summary.md).

## What we found

### 1. With-factbook vs no-factbook

Pooling naive + grounded as a single "with-factbook" arm, since both put the same content in the model's context using different rendering formats:

| Metric | no factbook (n=18) | with factbook (n=36) | Δ |
|---|---:|---:|---:|
| Quality (1–5, median consensus) | 2.72 | 4.11 | **+1.39** |
| Contradictions (count, lower better) | 0.67 | 0.00 | **−0.67** |
| Coverage honesty (0/1) | 0.39 | 0.86 | +0.47 |
| Citation (0/1) | 0.17 | 0.69 | +0.52 |

Quality bins:
- Harmful answers (would actively cause damage if shipped): 61% → 14%
- Good-or-better (≥4): 33% → 78%

Risk: 11/18 cells without factbook were rated `high` shipping-risk; 1/36 with factbook.

**Robustness against same-family contamination.** One of the three judges (Claude Sonnet 4.6) shares a model family with one of the generators (also Claude Sonnet 4.6). Re-computing the consensus excluding the Claude judge — using only GPT-4.1 + Gemini 2.0 Flash judges — keeps the direction and magnitude of every delta within 0.06pts:

| Metric | full 3-judge | GPT+Gemini only |
|---|---:|---:|
| Quality Δ | +1.39 | +1.33 |
| Citation Δ | +0.52 | +0.50 |
| Coverage Δ | +0.47 | +0.39 |
| Contradiction Δ | −0.67 | −0.61 |

The same-family judge is not driving the lift.

### 2. Naive markdown grounding vs structured per-vendor rendering

The pooling above combines two grounding styles. The split:

| Metric | naive markdown | structured renderer | Δ |
|---|---:|---:|---:|
| Quality | 4.22 | 4.00 | −0.22 |
| Contradictions | 0.00 | 0.00 | 0 |
| Coverage | 0.83 | 0.89 | +0.06 |
| Citation | 0.44 | 0.94 | +0.50 ⚠️ |

The citation jump is a renderer artifact: the naive renderer in this run does not include factlet IDs (`f001`, `f002`, …), so models given naive grounding cannot cite IDs they were never shown. On the outcome metrics that don't depend on ID surfacing — quality, contradictions, coverage — naive markdown and structured rendering produce comparable results at this N.

### 3. Where the factbook helps and where it doesn't

Per-task quality delta (no-factbook → with-factbook, averaged across 3 models):

| Task | qual without | qual with | Δ | Reading |
|---|---:|---:|---:|---|
| ml-pipeline-001 (S3 data loading) | 1.67 | 4.67 | **+3.00** | Models defaulted to direct S3 read; factbook redirected to dataset registry |
| frontend-001 (state management) | 2.00 | 4.67 | **+2.67** | Models reached for Redux; factbook said TanStack Query |
| payments-001 (90-day refund) | 1.67 | 3.83 | **+2.17** | Models auto-refunded; factbook required ops approval |
| frontend-002 (image component) | 4.33 | 4.67 | +0.33 | Models already used next/Image; factbook just confirmed |
| ml-pipeline-002 (outside coverage) | 2.33 | 2.50 | +0.17 | Outside the factbook's coverage; ceiling effect |
| payments-002 (customer ID type) | 4.33 | 4.33 | 0 | Models already used strings; factbook redundant |

**Pattern:** the lift is proportional to how often the model's training prior diverges from the team-specific decision encoded in the factbook. On tasks where general knowledge already aligns with team policy, the factbook is neutral. On tasks where the model's prior conflicts with the team's documented decision (incidents, retired libraries, compliance rules), the factbook is decisive.

This is the substantive engineering finding worth taking forward: the lift is task-dependent, not uniform.

## Inter-judge agreement

| Metric | Agreement |
|---|---:|
| contradiction | 0.98 |
| coverage | 0.95 |
| citation | 0.88 |
| risk | 0.85 |
| quality | 0.77 |

Quality at 0.77 is the weakest; treat it as the lowest-confidence metric in the table.

## Limitations (the things that change at Tier 2)

1. **N=6 tasks.** Wilson 95% CI on a binary outcome at N=18 cells is roughly ±25pp. Direction-of-effect signals are visible; magnitudes are not pinned.
2. **Single-author task set.** The most important construct-validity issue. Tier 2 gates on ≥5 externally-authored tasks. Until then, every finding here reflects what one person who knows the protocol thinks the protocol does.
3. **K=1 at temp=0.** No characterization of provider-side stochasticity. Anthropic, OpenAI, and Google all decline to guarantee bitwise determinism even at temp=0. A reader rerunning these tasks will get *similar* but not *identical* numbers.
4. **No vanilla-RAG comparator.** "With factbook" is compared to "no factbook," not to retrieval-augmented baselines. Tier 2 adds a vanilla-RAG arm.
5. **No comparator against vendor memory features** (Anthropic Memory, OpenAI Memory). Tier 2 adds them.
6. **Factbooks are small** (5–8 factlets each). Real factbooks are 50–200 factlets. Tier 2 expands.
7. **Distractor injection not tested** — no irrelevant factlets in the context to test attention. Tier 2 adds.

## How to interpret this run

The run is best read as a methodology demonstration with directional evidence, not a benchmark. Useful interpretive frame:

- The data is consistent with the hypothesis that providing team-specific truth in the model's context reduces task-specific failure modes when the team's truth diverges from what general training would predict.
- The data is **not** sufficient to support a single-percentage headline, a "% better than alternatives" claim, per-vendor rankings, or statistical significance.
- The per-task table is more informative than any aggregate: it shows which tasks the lift comes from and which tasks are no-ops.

## Reproducing

```bash
git clone https://github.com/factlet-ai/evals
cd evals/runner && pip install -e .
export ANTHROPIC_API_KEY=… OPENAI_API_KEY=… GOOGLE_API_KEY=…
python validate.py --tasks ../tier1/tasks --factbooks ../tier1/factbooks
python run.py --tasks ../tier1/tasks --factbooks ../tier1/factbooks \
              --output ../results/$(date +%Y-%m-%d)
python score.py --raw ../results/$(date +%Y-%m-%d)/raw.jsonl \
                --tasks ../tier1/tasks --factbooks ../tier1/factbooks \
                --prompts ../tier1/judge-prompts \
                --output ../results/$(date +%Y-%m-%d)/scored.jsonl
python aggregate.py --scored ../results/$(date +%Y-%m-%d)/scored.jsonl \
                    --output ../results/$(date +%Y-%m-%d)
```

Cost ≈ $2.50, wall clock ≈ 50 min serial.

## Contributing tasks

To address the single-author limitation directly: pick a task in your domain, write the YAML following [`../tier1/task-schema.md`](../tier1/task-schema.md), open a PR. Externally-authored tasks are the highest-leverage contribution at this stage. See [`../README.md#contributing-tasks`](../README.md#contributing-tasks).
