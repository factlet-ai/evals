# Pre-registration — Tier 1

> **Status:** **DRAFT, not yet sealed.** Hashes in §7 record the current
> on-disk state for transparency, but no run has begun. Sealing happens
> when (a) the task set is at its final size for this tier, (b) the
> repo owner explicitly tags it via `git tag evals-tier1-prereg-vN`
> recording the hashes, and (c) the announcement of the seal is public.
> Treat anything in this file pre-tag as revisable; treat post-tag as
> binding (changes only via §6 amendment).

This document locks the Tier 1 design BEFORE any results are inspected. Any change to design, scoring, or analysis after this tag is committed must be amended in §6 with timestamp and reason. Doing post-hoc tweaks without amendment = pre-registration violation.

---

## 1. Design

- **Conditions (3):** `baseline` (no factbook), `naive` (factbook as flat markdown), `grounded` (per-vendor renderer per Factlet Protocol §8)
- **Models (3):** `claude-sonnet-4-6`, `gpt-4-1`, `gemini-2.0-flash` (snapshots pinned; bumping any snapshot is a §6 amendment)
- **Total per task:** 9 cells (3 conditions × 3 models)
- **Sampling:** `temperature=0`, K=1 per cell — measuring capability, not distribution
- **Tasks (N=20):** 8 payments, 8 frontend, 4 ml-pipeline (incl. 2 outside-coverage calibration tasks). Frozen at the tag commit.

## 2. Scoring

- **Judges (3):**
  - `gpt-4-1` — primary (cross-family vs the 2 secondary judges we run on the same data; primary because OpenAI judges are independently observed to be the harshest grader on grounding tasks)
  - `claude-sonnet-4-6` — secondary
  - `gemini-2.0-flash` — secondary
  - Per-metric judge calls (one judge call per (task, condition, judge, metric))
- **Metrics (5):**
  - `citation` — binary 0/1, did response cite must_cite factlet ids
  - `contradiction` — integer ≥0, count of must_not_contradict factlets the response contradicted
  - `coverage` — binary 0/1, did response acknowledge the factbook gap when must_acknowledge_uncovered=true (or NOT falsely punt when false)
  - `quality` — integer 1-5
  - `risk` — categorical {low, medium, high}
- **Consensus rule:** majority for binary/categorical, median for ordinal — applied across the 3 judges per metric per cell

## 3. What we will publish at Tier 1

- The methodology (this doc + judge prompts + task schema + runner code)
- The raw `raw.jsonl` and `scored.jsonl` run artifacts
- `PER_TASK_DETAIL.md` (per-judge breakdown for every cell)
- `inter_judge_agreement.md` (transparency on judge variance)
- `scored_summary.md` (table; clearly labeled "indicative, NOT a headline")
- A qualitative writeup with 3-4 chosen worked examples illustrating concrete failure modes that grounding addresses (or doesn't)

## 4. What we will NOT publish at Tier 1

- A single headline aggregate number (e.g. "X% improvement"). Sample size N=20 per condition is below the threshold for that — see `tier1/methodology.md` §"Sample-size analysis"
- Any cell-level comparison promoted as a marketing claim
- Any per-vendor leaderboard claim

These claims are deferred to **Tier 2**, when N reaches ≥80/condition with externally-authored tasks. Tier 2 design + scope lives at `../FACTLET-EVALS-BACKLOG.md`.

## 5. Stopping rules and analysis plan

- Run the full task × condition × model grid in a single batch — no peeking, no early stopping
- After the run, score with all 3 judges in a single batch
- After scoring, aggregate per the consensus rule above and emit the 3 markdown reports — that's the analysis. We do not iterate on rubric, prompts, or task selection in response to the numbers
- If a metric shows judge agreement <0.6, the metric is downgraded to "exploratory only" in the Tier 1 writeup and not used in the qualitative narrative
- If <80% of cells return parseable scores from at least 2/3 judges, the run is declared a methodology failure and the prompts are revised (with §6 amendment) before re-run

## 6. Amendments

(empty — to be appended with timestamp + reason for any post-tag change)

---

## 7. Hashes (current on-disk state, NOT YET SEALED)

Computed via `find <path> -type f | sort | xargs cat | shasum -a 256` (run from repo root, current commit).

- task set sha256:       `c22b77e4a68dec4890b22613e61aaef24527513c320946a29f56b935adcebc82`
- judge prompts sha256:  `39a2305460d960d05cd6a0c65df0fd67fa789b73e1e1a0dd224aa55138be77f6`
- runner code sha256:    `3f1d4a30353f2c6793800eb3a80c9dd28f48d61a66c3d0458c45e27c72c0f6c6`
- factbooks sha256:      `31535a1b10d34da4b9fb0baef5eaec6f67d0f6a8ff6593b09a4258770b65419b`

Current Tier 1 task count: **6** (target before seal: 20). When the task set is grown to its final size, regenerate these hashes and replace this section with the sealed values + a `## 8. Seal log` row recording the tag, date, and signer.
