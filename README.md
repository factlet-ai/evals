# Factlet Protocol — Evals

Open eval suite for the [Factlet Protocol](https://factlet.ai). MIT-licensed.

> **Status: Tier 1 — methodology + raw runs.** This release publishes the eval *infrastructure*, *task set*, *raw run data*, and *worked examples*. **It deliberately does not publish a headline aggregate number.** A defensible aggregate number ships in Tier 2 (~2-4 weeks) after expanding to N=100+ tasks with multi-judge agreement, externally-authored tasks, and bootstrap CIs. Why this sequencing: see [`docs/why-no-headline-yet.md`](docs/why-no-headline-yet.md).

## What this repo is

A reproducible benchmark harness that compares LLM behavior under three conditions:

1. **Baseline** — no factbook
2. **Naive grounding** — factbook content as flat markdown in system
3. **Factlet-grounded** — factbook rendered via per-vendor renderer (Factlet Protocol)

…across three frontier models (Claude Sonnet 4.6, GPT-4.1, Gemini 2.0 Flash) on hand-crafted tasks across three domains (payments, frontend, ML pipeline).

The strategic comparison is **with-factbook (any rendering) vs no-factbook** — does giving the model your team's truth in context measurably reduce harmful or off-policy output? The diagnostic comparison **#3 vs #2** also gets reported but isn't the moat: the rendering format is MIT-licensed and trivially copyable. The moat is auto-generating and maintaining the factbook from your codebase + git history.

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
export GOOGLE_API_KEY=AIza...   # GEMINI_API_KEY also accepted

# Validate task YAML
python validate.py --tasks ../tier1/tasks --factbooks ../tier1/factbooks

# Run all tasks × all conditions × all models
python run.py \
  --tasks ../tier1/tasks --factbooks ../tier1/factbooks \
  --output ../results/$(date +%Y-%m-%d)

# Score with 3 judges (per-metric)
RUN_DIR=../results/$(date +%Y-%m-%d)
python score.py \
  --raw $RUN_DIR/raw.jsonl \
  --tasks ../tier1/tasks --factbooks ../tier1/factbooks \
  --prompts ../tier1/judge-prompts \
  --output $RUN_DIR/scored.jsonl

# Aggregate to markdown reports (summary + per-task detail + agreement)
python aggregate.py \
  --scored $RUN_DIR/scored.jsonl \
  --output $RUN_DIR
```

Cost at the current 6-task scaffold: **~$2.50** (54 generation calls + 810 judge calls). Scales linearly with task count and judge count.

## Pre-registration

Tier 1's task set, judge prompts, scoring rubric, and analysis plan are pre-registered before any run. The seal recipe (using `git ls-tree` for filesystem-/locale-independent hashing) lives in [`tier1/PREREG.md`](tier1/PREREG.md). Any change requires a new pre-registration with reason.

## Results so far

A first run (N=6 tasks, single-author scaffold) is published for transparency at [`docs/RESULTS-N6-MAY-2026.md`](docs/RESULTS-N6-MAY-2026.md). **Do not extract a single-number headline from this run** — the doc is explicit about why N=6 + single-author can't support that. Per-task heterogeneity (where the factbook helps, where it doesn't) is the substantive finding worth reading.

Raw + scored data: [`results/v2/`](results/v2/).

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
- **Tier 3 (~3 months, alongside spec v0.2)**: conformance test suite, retrieval-quality benchmarks, calibration evals on the protocol's confidence signal (low-confidence-coverage warnings), continuous-eval infrastructure.

## License

MIT — see [LICENSE](LICENSE).
