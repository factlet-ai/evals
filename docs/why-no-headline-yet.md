# Why this repo doesn't publish a headline number yet

A small-N pre-registered run does not support an aggregate "X% → Y%" claim. This page documents the three methodology issues that gate any such claim and what Tier 2 will add to address them.

## Three issues an aggregate claim must address

1. **Sample size.** N=20 binary outcomes per condition gives a Wilson 95% CI of ~±20 percentage points. Any headline with a ≤20pp delta is inside the noise floor — a reviewer who reruns gets a different number.

2. **Same-family judge contamination.** When the judge model is from the same family as a generator (e.g., Claude judges Claude), self-preference is a known failure mode. An aggregate claim needs a multi-judge architecture with an explicit robustness check that excludes the same-family judge.

3. **Counterfactual.** "Factbook vs. nothing" is the easy comparison. A more informative comparison is "factbook vs. naive markdown paste" (does structure beat unstructured grounding?) and "factbook vs. retrieval-augmented baseline" (does authored truth beat retrieved chunks?). Tier 1 includes the naive-markdown arm; Tier 2 adds RAG.

## What this repo ships now

Tier 1: methodology, infrastructure, task set, raw run data, judge prompts, scoring rubric. Sufficient for anyone to reproduce, audit, or extend. Not sufficient to publish an aggregate claim.

## What Tier 2 will add

- N from current scaffold → 100+ tasks
- ≥5 externally-authored tasks
- Multi-judge architecture (GPT-4.1 primary, Claude/Gemini secondary) with per-metric inter-judge agreement reported
- Composite metric: `must_cite ✓ AND contradictions == 0 AND coverage_honesty ✓ AND quality ≥ 4`
- Bootstrap task-clustered 95% CIs
- Pre-registered minimum effect size (publish only if CI excludes zero AND point estimate ≥ 15pp)
- Vanilla-RAG comparator arm
- Vendor-memory comparators (Anthropic Memory, OpenAI Memory) when APIs are stable

## Running it yourself

```
git clone https://github.com/factlet-ai/evals
cd evals/runner && pip install -e .
# Add task YAML under ../tier1/tasks/<domain>/
python run.py --tasks ../tier1/tasks --factbooks ../tier1/factbooks --output ../results/$(date +%Y-%m-%d)
```

Per-judge per-metric scores land in `results/YYYY-MM-DD/scored.jsonl`. Aggregate however you want.
