# Contributing

Thanks for wanting to contribute. The single highest-leverage contribution to this repo is **a task authored by someone other than the protocol author**. Construct validity of the eval depends on this. We need it more than we need code.

## What we want

**Tasks that test cases where the model's training prior is likely to conflict with a documented team-specific decision.** This is the empirical pattern that matters: tasks where general LLM knowledge already aligns with what the team would do produce no signal (the model gets it right with or without the factbook). Tasks where the team has retired a library, set a non-default policy, or recorded an incident that informs current practice produce real signal.

**Domains we especially want.** Right now we have payments / frontend / ml-pipeline. We're actively asking for:
- **security** — auth flows, secret handling, IAM policy, OWASP-class issues with team-specific guardrails
- **devops / infrastructure** — Terraform / Kubernetes / CI policies; team-specific deploy rules; incident-driven constraints
- **data engineering** — schema decisions, pipeline conventions, registry / lineage discipline
- Other domains welcome — open an issue first if you're unsure whether your task fits.

## What makes a good task

Acceptance criteria the maintainer applies on review:

1. **Real conflict.** The task tests a case where the model's likely default answer (from public training data) would violate something in the factbook. If general knowledge already matches the factbook, the task is a no-op and gets rejected.
2. **Verifiable.** `expected_behavior.must_cite` / `must_not_contradict` ids actually exist in the referenced factbook, and the `ground_truth_answer` is checkable by a senior engineer in the domain.
3. **Concrete query.** A real-shape developer prompt, not "explain the policy." Tasks that ask the model to *write code* / *make a change* are stronger than tasks that ask it to recite knowledge.
4. **Non-trivial.** A factbook the model could trivially deduce from the query (e.g. naming a library that the query already mentions) doesn't test grounding — it tests reading.
5. **Single contested point per task.** Multi-factlet tasks are fine but each task should have a clear primary failure mode. Stuffing 5 unrelated rules into one query makes the result hard to interpret.
6. **Outside-coverage tasks welcome.** Tasks where `must_acknowledge_uncovered: true` (the factbook deliberately doesn't address part of the query) are valuable — they test calibration honesty.

## How to contribute a task

1. **Open an issue first** using the [Task proposal](.github/ISSUE_TEMPLATE/task-proposal.md) template. Describe the conflict the task tests in 2–3 sentences. This saves you from writing a YAML that gets rejected. The maintainer will reply with go / discuss / no-fit within a week.
2. **Once green-lit**, fork, write the task YAML following [`tier1/task-schema.md`](tier1/task-schema.md), and add it to the appropriate domain folder under `tier1/tasks/`. Set `external_author: true` and put your handle in `author`.
3. **If your task references a factlet that doesn't exist in any current factbook**, open a PR to `tier1/factbooks/<domain>-factbook.yaml` first (or alongside) — but prefer using existing factlets when you can.
4. **Run the validator locally**: `cd runner && pip install -e . && python validate.py --tasks ../tier1/tasks --factbooks ../tier1/factbooks`. The PR will be rejected if it doesn't pass.
5. **Optional — run the eval against your task** to see how the 3 models handle it before submitting (~$0.05 cost). Useful for sanity-checking that the task actually produces the failure pattern you expected.
6. **Open a PR** using the PR template. Disclose your engineering background and any affiliation with Kernora.

## What we won't accept

- Tasks copy-pasted from public benchmarks (HumanEval, SWE-bench, etc.) — they're already in training data.
- Tasks that test general knowledge ("what does HTTP 429 mean?") — wrong eval.
- Tasks where the "correct" answer is contestable among senior engineers — we want documented team decisions, not opinion.
- Marketing-flavored tasks designed to make the protocol look good — we'll pick up that signal in the review and it will hurt your contribution credibility, not help.
- Tasks with prompt-injection content or attempts to test injection — interesting research direction, but out of scope for Tier 1.

## Maintainer triage

PRs are reviewed on a roughly weekly cadence by [@mihirchoudhary](https://github.com/mihirchoudhary). The triage rubric:

- **Reject** if the task fails any of the "good task" criteria above, or if it's a duplicate of an existing failure mode (we want diverse failure modes, not coverage of the same one).
- **Request changes** if it's salvageable — usually because `expected_behavior` doesn't match the prose query, or the ground-truth answer needs sharpening.
- **Accept** if it adds a new failure mode in a domain we want, the contributor's affiliation is disclosed, and the YAML validates.

We aim to merge ≥5 externally-authored tasks before re-running the eval and publishing an updated results doc. After that gate, the cadence becomes monthly merges + quarterly re-runs.

## Code contributions

The runner code (`runner/`) is small and not the primary thing we need help on. If you do want to contribute there:

- Open an issue first describing the change — mechanical PRs that add features without prior discussion will be closed.
- Tests welcome (we don't have many).
- Performance and async-runner improvements actively welcome (current runner is serial; Tier 2's larger N will hurt without it).

## Thanks

Especially to engineers contributing tasks from domains we haven't covered yet. The eval is more honest with your perspective in it than without.
