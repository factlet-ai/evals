# Task schema (Tier 1)

Each task is one YAML file in `tier1/tasks/<domain>/`. The runner loads all `.yaml` files in this tree.

```yaml
id: payments-001                      # globally unique; <domain>-NNN convention
domain: payments                      # one of: payments | frontend | ml-pipeline
factbook: payments-factbook.yaml      # filename in tier1/factbooks/
author: mihirchoudhary                # github handle of task author (provenance)
external_author: false                # true if author is NOT affiliated with Kernora
held_out: false                       # true if this task is in the 20% held-out subset

query: |
  The natural-language question or instruction passed to the model as the
  user message. Multi-line OK; written exactly as a developer might paste
  into an IDE assistant.

# Expected behavior — drives the objective sub-metrics
expected_behavior:
  must_cite: [f002]                   # factlet IDs the model MUST reference in its answer
  must_not_contradict: [f002, f005]   # factlet IDs the model MUST NOT contradict
  must_acknowledge_uncovered: false   # true if part of the query is outside the factbook's coverage

# Subjective ground truth — used by the LLM-as-judge
ground_truth_answer: |
  A short reference answer that the judge can compare against. Should be
  what a senior engineer would write given the factbook. Used only as a
  reference, not as a string-match target.

# Metadata for analysis
risk_if_wrong: high                   # low | medium | high (how bad if model answers wrong)
task_type: direct_match               # direct_match | multi_factlet | partial_coverage | outside_coverage
notes: |
  Free-form notes for reviewers. Why this task matters; what failure modes
  it probes; any prior runs that surfaced interesting behavior.
```

## Field rules

- **id** — `<domain>-NNN` zero-padded; immutable once committed
- **factbook** — must reference an existing file in `tier1/factbooks/`
- **author** — github handle for blame; transparent provenance
- **external_author: true** — counts toward the construct-validity goal of having ≥5 of 20 tasks written by non-Kernora engineers
- **held_out: true** — task is excluded from any in-progress analysis and only revealed at final-run time. Aim for 20% of total tasks held out.
- **must_cite / must_not_contradict** — used by the deterministic checker (regex-grep for `fNNN` IDs in the response, plus judged-contradiction detection)
- **must_acknowledge_uncovered: true** — for `task_type: outside_coverage` tasks; the model is correct iff it explicitly states the relevant aspect is outside the factbook
- **task_type** — distribution target: ~30% direct_match, ~30% multi_factlet, ~20% partial_coverage, ~20% outside_coverage

## Validation

Before commit, run:
```bash
python runner/validate.py tier1/tasks/<domain>/<task-id>.yaml
```
Checks: schema conformance, factbook file exists, must_cite IDs exist in factbook, must_not_contradict IDs exist in factbook.
