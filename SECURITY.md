# Security policy

## Scope

This repo is an eval harness, not a production service. The realistic security concerns:

- A malicious task YAML or factbook YAML that tries to abuse the runner (path traversal in `factbook:` field, prompt injection inside model outputs, etc.)
- API-key leakage in run artifacts (model responses occasionally include placeholder keys; we redact known-shape patterns before publishing)
- Supply-chain concerns in `runner/` dependencies

If you find an issue in any of those areas, please **don't open a public issue**.

## Reporting

Email: choudharymihir@gmail.com with subject `[evals security]`.

Include: a description of the issue, repro steps, and affected commit SHA. We'll acknowledge within a week and aim to fix or document within two.

## What we'll do

- Acknowledge receipt
- Triage and confirm
- Fix in a branch; coordinate disclosure if needed
- Credit the reporter in the fix commit message (unless you ask us not to)

## Known-out-of-scope

- "The protocol could be tricked by adversarial factbooks" — yes, that's a research direction. Open an issue tagged `discussion` if you want to discuss.
- "Model responses can contain insecure code" — these are eval outputs, not deployable code. Don't deploy them.
- Bug bounties — we don't run one. Goodwill only.
