# Results — Tier 1 scaffold run (N=6, May 2026)

> **Read this first.** N=6 tasks per condition. Single-author task set. This run is published as **transparency over result-quality** — we pre-registered, ran, and are showing you the data even though it's too small for a headline aggregate claim. If you take a single percentage from this doc and put it in marketing copy, you are doing a thing this doc explicitly does not authorize.
>
> The point of publishing it: pre-registration without published runs is theater, and the per-task heterogeneity (where it works, where it doesn't) is more interesting than any aggregate would be.

## What was run

- **6 tasks**, 3 domains (payments / frontend / ml-pipeline), all authored by the protocol author. **Single-author construct-validity hole acknowledged.** Tier 2 ship-gate is ≥5 externally-authored tasks before any further publish.
- **3 conditions × 3 models** = 9 cells per task → 54 generations
- **3 judges, per-metric**, 5 metrics each → 810 judge calls (0 parse failures)
- temp=0, K=1 (capability measurement, not stochasticity characterization)
- Pinned snapshots: `claude-sonnet-4-6`, `gpt-4.1`, `gemini-2.0-flash`
- Cost ~$2.50; wall clock ~50 min serial

Raw data: [`../results/v2/raw.jsonl`](../results/v2/raw.jsonl). Per-judge per-metric scores: [`../results/v2/scored.jsonl`](../results/v2/scored.jsonl). Inter-judge agreement: [`../results/v2/inter_judge_agreement.md`](../results/v2/inter_judge_agreement.md). Per-cell consensus: [`../results/v2/scored_summary.md`](../results/v2/scored_summary.md).

## What we found

### 1. With-factbook beats no-factbook (consistent with hypothesis, not a marketing claim)

Pooling naive + grounded as a single "with-factbook" arm (because the rendering format is MIT-licensed and isn't the moat):

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

**Robustness against same-family contamination.** A reader can object that one of our three judges is the same family as one of the generators (Claude-judges-Claude). Re-running the consensus on **only GPT-4.1 + Gemini judges** (excluding Claude entirely) keeps the direction and magnitude of every delta within 0.06pts:

| Metric | full 3-judge | GPT+Gemini only |
|---|---:|---:|
| Quality Δ | +1.39 | +1.33 |
| Citation Δ | +0.52 | +0.50 |
| Coverage Δ | +0.47 | +0.39 |
| Contradiction Δ | −0.67 | −0.61 |

So same-family judging is not what's driving the lift.

### 2. The rendering format is not the moat

The strategic comparison above pools "naive markdown" and "structured per-vendor" because anyone can copy a rendering format — it's MIT-licensed. For completeness, here's the diagnostic split:

| Metric | naive markdown | structured renderer | Δ |
|---|---:|---:|---:|
| Quality | 4.22 | 4.00 | −0.22 |
| Contradictions | 0.00 | 0.00 | 0 |
| Coverage | 0.83 | 0.89 | +0.06 |
| Citation | 0.44 | 0.94 | +0.50 ⚠️ |

The citation jump is a renderer artifact: the naive renderer doesn't include factlet IDs (`f001`, `f002`, …) so models grounded with naive markdown literally cannot cite the IDs they were never shown. On every metric that is actually about quality of output (contradictions, coverage, harm) — naive ≈ grounded.

**This finding hurts the protocol's positioning more than it helps.** Publishing it is the credibility move. The protocol's value is in **what** the factbook contains and how it gets generated/maintained, not how it gets rendered into the prompt.

### 3. Where the factbook helps and where it doesn't

Per-task quality delta (no-factbook → with-factbook, averaged across 3 models):

| Task | qual without | qual with | Δ | Reading |
|---|---:|---:|---:|---|
| ml-pipeline-001 (S3 data loading) | 1.67 | 4.67 | **+3.00** | Model defaulted to direct S3 read; factbook redirected to dataset registry |
| frontend-001 (state management) | 2.00 | 4.67 | **+2.67** | Model reached for Redux; factbook said TanStack Query |
| payments-001 (90-day refund) | 1.67 | 3.83 | **+2.17** | Model auto-refunded; factbook required ops approval |
| frontend-002 (image component) | 4.33 | 4.67 | +0.33 | Model already knew next/Image; factbook just confirmed |
| ml-pipeline-002 (outside coverage) | 2.33 | 2.50 | +0.17 | Outside the factbook's coverage; ceiling effect |
| payments-002 (customer ID type) | 4.33 | 4.33 | 0 | Model already knew strings; factbook redundant |

**Pattern:** the factbook's value is proportional to how often your team's truth diverges from the public training corpus. On tasks where general knowledge already aligns with team policy, the factbook is neutral. On tasks where the model's prior conflicts with the team's documented decision (incidents, retired libraries, compliance rules), the factbook is decisive.

This is the substantive finding worth taking forward — the marketing line "factbook lifts every task" is wrong; the engineering line "factbook lifts the tasks that need lifting" is right.

## Inter-judge agreement

| Metric | Agreement |
|---|---:|
| contradiction | 0.98 |
| coverage | 0.95 |
| citation | 0.88 |
| risk | 0.85 |
| quality | 0.77 |

Quality at 0.77 is the weakest; we treat it as the lowest-confidence metric in the table.

## Limitations (the things that change at Tier 2)

1. **N=6 tasks.** Wilson 95% CI on a binary outcome at N=18 cells is roughly ±25pp. Direction-of-effect signals are visible; magnitudes are not pinned.
2. **Single-author task set.** The most important construct-validity issue. Tier 2 gates on ≥5 externally-authored tasks. Until then, every finding here is "this is what one person who knows the protocol thinks the protocol does."
3. **K=1 at temp=0.** No characterization of provider-side stochasticity. Anthropic, OpenAI, and Google all decline to guarantee bitwise determinism even at temp=0. A reader rerunning these tasks will get *similar* but not *identical* numbers.
4. **No vanilla-RAG comparator.** "With factbook" beats "no factbook," but neither arm tests against retrieval. Tier 2 adds it.
5. **No comparator against vendor memory features** (Anthropic Memory, OpenAI Memory). Tier 2 adds them.
6. **Factbooks are small** (5–8 factlets each). Real factbooks are 50–200. Tier 2 expands.
7. **Distractor injection not tested** (irrelevant factlets in the context to test attention). Tier 2 adds.

## What you can say externally based on this run

Defensible:
- "In a small (N=6 tasks) pre-registered scaffold run, supplying the model with team-specific truth in any reasonable format reduced harmful shipping recommendations and increased citation of team policy, across Claude, GPT, and Gemini. The improvement concentrates on tasks where the model's training prior conflicts with team-specific decisions; tasks where general knowledge already aligns saw no improvement. The rendering format (structured XML vs. flat markdown) did not materially change quality."

Not defensible until Tier 2:
- A single-number percentage headline
- "X% better than [comparator]" (no RAG/Memory comparators in this run)
- Per-vendor leaderboards
- Statistical significance claims

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

If you want to address the single-author limitation directly: pick a task in your domain, write the YAML following [`../tier1/task-schema.md`](../tier1/task-schema.md), open a PR. Externally-authored tasks are the highest-leverage contribution at this stage. See [`../README.md#contributing-tasks`](../README.md#contributing-tasks).
