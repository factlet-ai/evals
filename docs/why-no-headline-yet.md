# Why this repo doesn't publish a headline number yet

(And why that's deliberate — not laziness.)

## The question

When the Factlet Protocol was first proposed, the most predictable question was: *"Does this actually work compared to alternatives? Show numbers."*

The fastest path to a headline number would have been: hand-craft 20 tasks, run baseline-vs-grounded across 3 models, compute "Wrong-answer rate dropped from X% to Y%," publish.

That path was rejected on methodology grounds.

## Three blockers to a headline at N=20 or smaller

A pre-implementation Principal Engineer review surfaced three issues that any responsible eval must address before publishing an aggregate claim:

1. **Sample size.** N=20 binary outcomes per condition → Wilson 95% CI is ~±20 percentage points. Any "X% → Y%" headline with a ≤20pp delta is inside the noise floor. A reviewer who reruns gets a different number; the result is unreproducible by design.

2. **Same-family judge contamination.** When the judge model is from the same family as a generator (e.g., Claude judges Claude), a sophisticated reader assumes self-preference. Defensible aggregate claims require a multi-judge architecture and an explicit robustness check that excludes the same-family judge.

3. **Counterfactual choice.** "Baseline = no factbook" is the easy comparison. A more demanding comparison is "factbook vs. naive markdown paste" (does structure beat unstructured grounding?) and "factbook vs. retrieval-augmented baseline" (does authored truth beat retrieved chunks?). Tier 1 includes the naive-markdown arm; Tier 2 adds RAG.

A headline number that doesn't address these three is more misleading than no headline.

## What this repo ships instead

**Tier 1 is the methodology, infrastructure, task set, and raw run data.** A Tier 2 follow-up — N≥100, externally-authored tasks, vanilla-RAG comparator, bootstrap CIs, pre-registered minimum effect size — will be the next milestone where an aggregate claim is on the table.

This sequencing follows the pattern of other open spec + reference-implementation projects: ship the spec and SDK first, then publish rigorous benchmarking as a separate evidentiary wave.

## What Tier 2 will add

- N grows from current scaffold → 100+ tasks
- ≥5 externally-authored tasks (construct validity gate)
- Multi-judge architecture (GPT-4.1 primary, Claude/Gemini secondary) with inter-judge agreement reported per metric
- Composite objective-heavy headline metric: `must_cite ✓ AND contradictions == 0 AND coverage_honesty ✓ AND quality ≥ 4`
- Bootstrap task-clustered 95% confidence intervals
- Pre-registered minimum effect size (only publish if CI excludes zero AND point estimate ≥ 15pp)
- Vanilla-RAG comparison arm
- Vendor-memory comparators (Anthropic Memory, OpenAI Memory) when API stable

## What you can do now

If you want to test the protocol on your own queries:

1. Clone this repo
2. Set API keys (Anthropic / OpenAI / Google)
3. Add a task YAML under `tier1/tasks/<domain>/`
4. Run `python runner/run.py` — see your own results

The infrastructure is real; it's the aggregate claim that's deferred.

## Reading the open data

`results/YYYY-MM-DD/scored.jsonl` has every individual run with its per-judge per-metric scores. Anyone can compute their own aggregates and draw their own inferences from the raw data.
