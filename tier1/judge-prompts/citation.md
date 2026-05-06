# Judge prompt — Citation correctness

You are evaluating an AI model's answer for **citation correctness**: did the model cite the specific factlet IDs that were required?

## Inputs you receive

- `query` — the question asked
- `must_cite` — array of factlet IDs (e.g. `["f002"]`) the answer MUST reference
- `response` — the model's answer

## Decision

Output **0 or 1**:
- **1** = response explicitly references EVERY factlet ID in `must_cite` (e.g. "per f002", "f002 says", "(f002)", or unmistakable reference to the factlet by its statement)
- **0** = response missed any required citation OR cited something else

## Calibration anchors

### Example 1 (score = 1)
- `must_cite: [f002]`
- `response`: "Per f002, refunds older than 90 days require manual ops approval, so we cannot auto-process this charge..."
- → **1** (explicit f002 cite + paraphrases the factlet)

### Example 2 (score = 0)
- `must_cite: [f002]`
- `response`: "Refunds over 90 days require approval; here's the code..."
- → **0** (correct content but no factlet ID cited; this is the difference between "knows the rule" and "uses the protocol")

### Example 3 (score = 1)
- `must_cite: [f001, f002]`
- `response`: "We use Stripe webhooks for payment status (f001) and per f002 refunds older than 90 days need manual approval..."
- → **1** (both IDs cited)

### Example 4 (score = 0)
- `must_cite: [f001, f002]`
- `response`: "Per f001, we use webhooks. Refunds need manual approval after 90 days."
- → **0** (cited f001 but not f002, even though it referenced f002's content)

## Output format

Respond with ONLY a single token: `0` or `1`. No explanation, no preamble.
