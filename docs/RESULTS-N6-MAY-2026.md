# Results — Tier 1 scaffold run (N=6, May 2026)

## Summary

Three frontier models (Claude Sonnet 4.6, GPT-4.1, Gemini 2.0 Flash) were tested on 6 hand-crafted developer tasks, each in two conditions: with and without a team-specific factbook in context. Three LLM judges scored each response across 5 metrics — 810 judge calls total.

With a factbook in context: median quality rose from 2.7 to 4.1 (1–5 scale), responses rated as harmful-if-shipped fell from 61% to 14%, and contradictions of documented team policy fell from ~0.67 per response to 0. The direction and magnitude survive when the same-family judge (Claude judging Claude) is excluded from the consensus.

The lift is not uniform. It concentrates on tasks where the model's default answer (from public training data) conflicts with a documented team decision — refunds older than 90 days, libraries the team retired, compliance rules. On tasks where general knowledge already matches team policy, adding the factbook makes essentially no difference.

The lift also does not depend on rendering format. Both naive markdown and structured per-vendor rendering produced comparable quality and contradiction-rate improvements. The factbook content is what does the work; how it's delivered to the model is interchangeable at this N.

What this run does NOT support: a single-percentage headline ("X% better"), per-vendor leaderboards, statistical significance claims, or comparison to retrieval-augmented baselines (no RAG arm in this run). N=6 tasks with a single task author is below the threshold for those claims. A Tier 2 run at N≥100 with externally-authored tasks and a vanilla-RAG comparator is the next milestone where an aggregate claim is on the table.

Detail, per-task table, robustness checks, limitations, and reproduction instructions follow.

## Setup

- 6 tasks across payments / frontend / ml-pipeline, all authored by the protocol author
- 3 conditions × 3 models = 9 responses per task → 54 generations total
- 3 judges, per-metric, 5 metrics each → 810 judge calls (0 parse failures)
- temp=0, K=1
- Pinned snapshots: `claude-sonnet-4-6`, `gpt-4.1`, `gemini-2.0-flash`
- Cost ~$2.50; wall clock ~50 min

Raw data: [`../results/v2/raw.jsonl`](../results/v2/raw.jsonl) · scored: [`../results/v2/scored.jsonl`](../results/v2/scored.jsonl) · agreement: [`../results/v2/inter_judge_agreement.md`](../results/v2/inter_judge_agreement.md) · per-response consensus: [`../results/v2/scored_summary.md`](../results/v2/scored_summary.md)

## With-factbook vs no-factbook

Pooling naive + grounded as a single "with-factbook" arm:

| Metric | no factbook (n=18) | with factbook (n=36) | Δ |
|---|---:|---:|---:|
| Quality (1–5, median consensus) | 2.72 | 4.11 | **+1.39** |
| Contradictions (count, lower better) | 0.67 | 0.00 | **−0.67** |
| Coverage honesty (0/1) | 0.39 | 0.86 | +0.47 |
| Citation (0/1) | 0.17 | 0.69 | +0.52 |

Quality bin distribution:
- Harmful (≤2): 61% → 14%
- Good-or-better (≥4): 33% → 78%

Risk: 11 of 18 responses without factbook were rated `high` shipping-risk; 1 of 36 with factbook.

### Robustness check excluding same-family judge

One of the three judges (Claude Sonnet 4.6) is from the same model family as one of the three generators (also Claude Sonnet 4.6). Same-family bias — a judge favoring outputs from its own family — is a documented failure mode in LLM-as-judge evaluation. If that bias were inflating the headline numbers above, the apparent benefit would shrink or disappear when the Claude judge is removed from the consensus.

The check: recompute every delta using only the GPT-4.1 and Gemini 2.0 Flash judges (the two judges that have no family connection to anything they're scoring).

| Metric | full 3-judge | GPT+Gemini only | Movement |
|---|---:|---:|---:|
| Quality Δ | +1.39 | +1.33 | 0.06 |
| Citation Δ | +0.52 | +0.50 | 0.02 |
| Coverage Δ | +0.47 | +0.39 | 0.08 |
| Contradiction Δ | −0.67 | −0.61 | 0.06 |

The deltas barely change — the largest movement is 0.08 points. The lift is not an artifact of the same-family judge.

## Naive markdown vs structured per-vendor rendering

Splitting the with-factbook pool:

| Metric | naive markdown | structured renderer | Δ |
|---|---:|---:|---:|
| Quality | 4.22 | 4.00 | −0.22 |
| Contradictions | 0.00 | 0.00 | 0 |
| Coverage | 0.83 | 0.89 | +0.06 |
| Citation | 0.44 | 0.94 | +0.50 ⚠️ |

The citation gap is a renderer artifact: the naive renderer in this run does not include factlet IDs (`f001`, `f002`, …), so models given naive grounding cannot cite IDs they were never shown. On metrics that don't depend on ID surfacing — quality, contradictions, coverage — naive markdown and structured rendering produce comparable results at this N.

**Bottom line: the lift comes from the factbook content, not the rendering format.** Both rendering paths produced the quality and contradiction-rate improvements seen in the headline numbers. Whatever your AI tool happens to use to inject grounding (raw markdown, vendor-specific JSON, system-prompt block), the factbook does the work — the format is interchangeable at this N.

## Per-task delta

Quality (no-factbook → with-factbook), averaged across 3 models:

| Task | qual without | qual with | Δ | Reading |
|---|---:|---:|---:|---|
| ml-pipeline-001 (S3 data loading) | 1.67 | 4.67 | **+3.00** | Models defaulted to direct S3 read; factbook redirected to dataset registry |
| frontend-001 (state management) | 2.00 | 4.67 | **+2.67** | Models reached for Redux; factbook said TanStack Query |
| payments-001 (90-day refund) | 1.67 | 3.83 | **+2.17** | Models auto-refunded; factbook required ops approval |
| frontend-002 (image component) | 4.33 | 4.67 | +0.33 | Models already used next/Image |
| ml-pipeline-002 (outside coverage) | 2.33 | 2.50 | +0.17 | Outside the factbook's coverage |
| payments-002 (customer ID type) | 4.33 | 4.33 | 0 | Models already used strings |

Lift is proportional to how often the model's training prior diverges from the team-specific decision encoded in the factbook. Tasks where general knowledge already aligns with team policy show ~zero lift. Tasks where the model's prior conflicts with a documented team decision (incidents, retired libraries, compliance rules) show large lift.

## Inter-judge agreement

| Metric | Agreement |
|---|---:|
| contradiction | 0.98 |
| coverage | 0.95 |
| citation | 0.88 |
| risk | 0.85 |
| quality | 0.77 |

## Limitations

1. **N=6 tasks.** Wilson 95% CI on a binary outcome at N=18 responses is ~±25pp. Magnitudes are not pinned.
2. **Single-author task set.** All tasks authored by the protocol author.
3. **K=1 at temp=0.** Provider-side stochasticity is not characterized; rerunning will produce similar but not identical numbers.
4. **No retrieval-augmented baseline.** Tier 2 adds a vanilla-RAG arm.
5. **No vendor-memory comparators** (Anthropic Memory, OpenAI Memory). Tier 2 adds them.
6. **Small factbooks** (5–8 factlets each). Tier 2 uses 50–200 factlet factbooks.
7. **No distractor injection.** Tier 2 tests attention against irrelevant factlets in context.

The data does not support a single-percentage headline, a "% better than alternatives" claim, per-vendor rankings, or statistical significance.

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

Cost ≈ $2.50, wall clock ≈ 50 min.

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md). Externally-authored tasks especially welcome.
