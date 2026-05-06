# Tier 1 runner

Async runner + multi-judge scorer + aggregator for the Factlet Protocol Tier 1 evals.

## Install

```bash
cd runner
pip install -e .
```

## Environment

Set the API keys for whichever providers you're running:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export GOOGLE_API_KEY=AIza...   # or GEMINI_API_KEY
```

## Workflow

```bash
# 1. Validate task YAML
python validate.py --tasks ../tier1/tasks --factbooks ../tier1/factbooks

# 2. Generate model responses (3 conditions × 3 models × N tasks)
python run.py \
  --tasks ../tier1/tasks \
  --factbooks ../tier1/factbooks \
  --output ../results/2026-05-DD-runA

# 3. Score with 3 judges (per-metric)
python score.py \
  --raw      ../results/2026-05-DD-runA/raw.jsonl \
  --tasks    ../tier1/tasks \
  --factbooks ../tier1/factbooks \
  --prompts  ../tier1/judge-prompts \
  --output   ../results/2026-05-DD-runA/scored.jsonl

# 4. Aggregate to markdown
python aggregate.py \
  --scored ../results/2026-05-DD-runA/scored.jsonl \
  --output ../results/2026-05-DD-runA
```

## What gets published

For Tier 1: methodology + raw runs ONLY. The aggregator emits an
`scored_summary.md` table and an `inter_judge_agreement.md` page so the
data is auditable, but **we are not promoting an aggregate headline** at
N=20 — see `../docs/RESULTS-N6-MAY-2026.md` (Limitations + Tier 2 publish-gate) for why.

## Re-running

The runner is deterministic at `temperature=0` and pinned model snapshots,
so re-running on the same task set should reproduce within model-API-side
variability (which is the headline reproducibility claim Tier 1 makes).
