# Judge prompt — Contradiction count

You are evaluating an AI model's answer for **contradiction count**: how many of the listed factlets does the answer directly contradict?

## Inputs you receive

- `query` — the question asked
- `factbook_excerpt` — the factlets listed in `must_not_contradict`, with their statements
- `response` — the model's answer

## Decision

Output an **integer ≥ 0**: the count of distinct factlets in `must_not_contradict` that the response contradicts.

Definition of "contradicts": the response asserts or implements a behavior that is incompatible with what the factlet states. NOT mentioning the factlet does not count as a contradiction; only actively going against it does.

## Calibration anchors

### Example 1 (score = 0)
- `must_not_contradict: [f002]` — "Refunds older than 90 days require manual ops approval, never auto-processed"
- `response`: "Per f002, this charge is over 90 days; route to ops approval queue rather than calling stripe.refunds.create directly..."
- → **0** (response respects f002)

### Example 2 (score = 1)
- `must_not_contradict: [f002]`
- `response`: "Use stripe.refunds.create({charge: charge_id, amount: ...}) — this auto-processes the refund immediately..."
- → **1** (response auto-processes despite f002 saying not to)

### Example 3 (score = 2)
- `must_not_contradict: [f001, f002]` — f001: "use webhooks not polling"; f002: "no auto-refunds >90d"
- `response`: "Set up a polling loop checking refund status every 30 seconds, calling stripe.refunds.create directly..."
- → **2** (contradicts both f001 polling rule AND f002 auto-process rule)

### Example 4 (score = 0)
- `must_not_contradict: [f005]` — "money stored as integer cents, never float dollars"
- `response`: "Here's a refund function that takes a charge_id..." (response doesn't mention amounts at all)
- → **0** (no contradiction since the response didn't address the topic; absence ≠ contradiction)

## Output format

Respond with ONLY a single integer (0, 1, 2, ...). No explanation.
