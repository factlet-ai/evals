# Factlet Protocol — Evals

Open eval suite for the [Factlet Protocol](https://factlet.ai). MIT-licensed.

> **Status: Tier 1 — methodology + raw runs.** This release publishes the eval *infrastructure*, *task set*, *raw run data*, and *worked examples*. **It deliberately does not publish a headline aggregate number.** A defensible aggregate number ships in Tier 2 (~2-4 weeks) after expanding to N=100+ tasks with multi-judge agreement, externally-authored tasks, and bootstrap CIs. Why this sequencing: see [`docs/why-no-headline-yet.md`](docs/why-no-headline-yet.md).

## What this repo is

A reproducible benchmark harness that compares LLM behavior under three conditions:

1. **Baseline** — no factbook
2. **Naive grounding** — factbook content as flat markdown in system
3. **Factlet-grounded** — factbook rendered via per-vendor renderer (Factlet Protocol)

…across three frontier models (Claude Sonnet 4.6, GPT-4.1, Gemini 2.0 Flash) on hand-crafted tasks across three domains (payments, frontend, ML pipeline).

The interesting comparison is **#3 vs #2** — does the protocol's structured grounding actually beat naive doc-paste? Skeptics ask this; this eval answers it.

## Repo layout

```
tier1/
  tasks/                  6 scaffold tasks (target before seal: 20)
    payments/      *.yaml — 2 tasks
    frontend/      *.yaml — 2 tasks
    ml-pipeline/   *.yaml — 2 tasks (incl. 1 outside-coverage calibration task)
  factbooks/       *.yaml — copies from factlet-ai/registry
  judge-prompts/   *.md   — per-metric LLM-as-judge prompts
  task-schema.md         — task YAML schema reference
  methodology.md         — design rationale, sample-size analysis, limits
  PREREG.md              — pre-registration template + SHA-256 of locked artifacts
runner/
  run.py                 — runs tasks × conditions × models
  score.py               — multi-judge scorer (GPT-4.1 / Claude / Gemini)
  aggregate.py           — scored.jsonl → markdown reports
  validate.py            — task YAML schema validator
  pyproject.toml
docs/
  why-no-headline-yet.md — public-facing explanation of Tier 1 vs Tier 2 staging
results/                 — timestamped raw runs + reports (gitignored once they exist)
```

## Quick start

```bash
cd runner/
pip install -e .

# Set API keys (BYOK — no provider lock-in)
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export GOOGLE_API_KEY=AIza...

# Validate task YAML
python validate.py --tasks ../tier1/tasks --factbooks ../tier1/factbooks

# Run all tasks × all conditions × all models
python run.py \
  --tasks ../tier1/tasks --factbooks ../tier1/factbooks \
  --output ../results/$(date +%Y-%m-%d)

# Score with 3 judges (per-metric)
python score.py \
  --raw ../results/2026-05-DD/raw.jsonl \
  --tasks ../tier1/tasks --factbooks ../tier1/factbooks \
  --prompts ../tier1/judge-prompts \
  --output ../results/2026-05-DD/scored.jsonl

# Aggregate to markdown reports (summary + per-task detail + agreement)
python aggregate.py \
  --scored ../results/2026-05-DD/scored.jsonl \
  --output ../results/2026-05-DD
```

Estimated cost per full cycle: **~$10** (360 generation calls × 3 models + 1080 judge calls × 3 judges).

## Pre-registration

Tier 1's task set, judge prompts, scoring rubric, and analysis plan are pre-registered before any run. Hashes of all locked artifacts live in [`tier1/PREREG.md`](tier1/PREREG.md). Any change requires a new pre-registration with reason.

## Conditions and methodology

See [`tier1/methodology.md`](tier1/methodology.md) for the full design rationale, sample-size analysis, judge architecture, and known limitations.

## Contributing tasks

Especially encouraged: **tasks authored by people who are not the Factlet Protocol author.** Construct validity demands external task authorship.

To contribute a task:

1. Pick a domain (payments / frontend / ml-pipeline) — or propose a new one in an issue first.
2. Read the relevant factbook in `tier1/factbooks/`.
3. Write a YAML task following the schema in [`tier1/task-schema.md`](tier1/task-schema.md).
4. Open a PR. Include in the PR body: who you are, your engineering background, whether you have any affiliation with Kernora.

## Status of Tier 2 / Tier 3

See `docs/FACTLET-EVALS-BACKLOG.md` in the [main Kernora project](https://kernora.ai) for what's coming. Highlights:

- **Tier 2 (~2-4 weeks)**: N=100+ tasks, externally-authored, bootstrap CIs, multi-judge consensus, vanilla-RAG comparison, **headline aggregate number published**.
- **Tier 3 (~3 months, alongside spec v0.2)**: conformance test suite, retrieval-quality benchmarks, FactSignal calibration evals, continuous-eval infrastructure.

## License

MIT — see [LICENSE](LICENSE).
