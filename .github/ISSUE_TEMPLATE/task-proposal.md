---
name: Task proposal
about: Propose a new task before writing the YAML
title: "Task proposal: <domain> — <one-line summary>"
labels: ["task-proposal"]
---

> Open this issue **before** writing the task YAML. The maintainer will reply within a week with go / discuss / no-fit. Saves you from writing a task that gets rejected on grounds the issue would have caught.

## Domain
<!-- payments / frontend / ml-pipeline / security / devops / data-engineering / other -->

## The conflict the task tests
<!--
In 2-3 sentences: what would the model's likely default answer be, and what
team-specific decision contradicts it? Tasks that don't have a clear conflict
between general LLM knowledge and team-specific truth tend to be no-ops.

Example: "Models default to using stripe.refunds.create directly. The team's
factbook says refunds older than 90 days require manual ops approval (set
after a compliance incident). The task asks the model to write refund code
for a 6-month-old charge — the model should refuse to auto-process."
-->

## The query you'd put in the task
<!--
Sketch the developer-prompt you'd use. Doesn't have to be polished YAML yet.
Real-shape "write this code" / "make this change" prompts are stronger than
"explain X."
-->

## Which factlets the task references
<!--
Either:
  - Existing factlet ids in tier1/factbooks/<domain>-factbook.yaml (preferred)
  - New factlets you'd add (sketch the statements; one factlet per bullet)
-->

## Risk if a model gets it wrong
<!-- low / medium / high; one sentence on what bad-answer-shipped looks like -->

## Your background
<!--
Brief: what you do, how long you've worked in this domain, any affiliation
with Kernora (none required, but disclose for the audit trail).
-->

## Anything else maintainer should know before greenlighting?
