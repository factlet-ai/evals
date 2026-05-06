<!-- For task contributions: link the issue from your task proposal. -->

## Summary
<!-- one or two sentences on what this PR does -->

## Type
<!-- check one -->
- [ ] New task (link the proposal issue: closes #___)
- [ ] Factbook update (new factlet or amendment)
- [ ] Runner code change
- [ ] Docs / methodology
- [ ] Other:

## For task contributions

- [ ] `external_author: true` set in the task YAML
- [ ] `author` field populated with my GitHub handle
- [ ] `python validate.py --tasks ../tier1/tasks --factbooks ../tier1/factbooks` passes locally
- [ ] Optionally — I ran the eval against this task to confirm the failure pattern (paste the relevant row of `scored_summary.md` if so)

### Conflict the task tests
<!--
1-2 sentences: what would the model's likely default answer be, and what
team-specific decision contradicts it? (Same as the issue, restated for the
PR record.)
-->

### Author background
<!--
Brief: what you do, domain experience, any affiliation with Kernora.
This goes into the audit trail; we'd rather over-disclose than under.
-->

## For runner / docs changes

- [ ] No new dependencies, OR new dependency justified in the description
- [ ] If touching scoring or judge prompts: pre-registration implications noted

## Anything reviewer should know
