# Why this repo doesn't publish a headline number yet

(And why that's deliberate — not laziness.)

## The skeptic question

When the Factlet Protocol launched, the most predictable skeptic question was: *"Show me numbers. Does this actually work compared to alternatives?"*

The fastest path to a headline number would have been: hand-craft 20 tasks, run baseline-vs-grounded across 3 models, compute "Wrong-answer rate dropped from X% to Y%," publish.

We chose not to.

## Why publishing a headline at N=20 would have been worse than not publishing

A pre-implementation Principal Engineer review surfaced three blockers:

1. **Sample-size honesty.** N=20 binary outcomes per condition → Wilson 95% CI is ~±20 percentage points. Any "X% → Y%" headline with a ≤20pp delta is inside the noise floor. Reviewers who rerun get a different number; reproducibility claim breaks; credibility taken.

2. **Same-family judge contamination.** If Claude judges Claude's outputs (and the grounded version uses Claude-tuned XML), the first sophisticated reader assumes self-preference. Mitigation requires multi-judge architecture — non-trivial to build right.

3. **Wrong baseline.** "Baseline = no factbook" is the wrong counterfactual. The real comparison a skeptical engineer wants is: "does the protocol beat me pasting my docs into the system prompt?" That requires a third arm (naive grounding) — not in original scope.

A bad headline number costs more credibility than no headline number.

## What we shipped instead

**Tier 1 is the methodology, infrastructure, task set, and raw run data. Tier 2 publishes the headline number ~2-4 weeks later.**

This is the same pattern MCP used: spec first, reference SDK, then evals + benchmarks 2-3 weeks later as a follow-up "rigorous data" wave. Sequenced credibility instead of one-shot risk.

## What Tier 2 will fix

- N grows from 20 → 100+ tasks
- ≥5 externally-authored tasks (construct validity)
- Multi-judge architecture (GPT-4.1 primary, Claude/Gemini secondary), inter-judge agreement reported
- Composite objective-heavy headline metric: `must_cite ✓ AND contradictions == 0 AND coverage_honesty ✓ AND quality ≥ 4`
- Bootstrap task-clustered 95% CIs
- Pre-registered minimum effect size (only publish if CI excludes zero AND point estimate ≥ 15pp)
- Naive-grounding baseline arm in Tier 1 (already)
- Vanilla-RAG comparison added in Tier 2

## What you can do now

If you want to test the protocol on your own queries:

1. Clone this repo
2. Set API keys (Anthropic / OpenAI / Google)
3. Add your own task YAML in `tier1/tasks/<domain>/`
4. Run `python runner/run.py` — see your own results

The infrastructure is real; it's the headline that's deferred.

## Reading the open data

`results/YYYY-MM-DD/scored.jsonl` has every individual run with its sub-metric scores. You can compute your own aggregates, draw your own inferences. We publish the data; you draw the conclusions.

## Honest framing for re-distributors

If you're writing about this work, the right framing is:

> "Tier 1 of the open Factlet Protocol evals shipped: methodology, 3 conditions × 3 models × 3 judges, hand-crafted scaffold tasks, full pre-registered design. The repo intentionally defers an aggregate headline number until Tier 2 when N grows to 100+ with externally-authored tasks and bootstrap CIs."

Not:
> "Factlet Protocol evals show grounded answers reduce X by Y%."

We don't make that claim yet. Don't put it in our mouths.
