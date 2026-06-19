---
name: openlayer-skill-feedback
description: Report a problem with THIS Openlayer skill — wrong/outdated guidance, a workflow that didn't work, or a missing use case. Use only for issues with the skill's instructions, not issues with the Openlayer product itself.
---

# Skill Feedback

When the user indicates this **skill** gave wrong/outdated guidance, a workflow didn't produce the
expected result, or it's missing something — offer to report it.

**Do NOT trigger this for issues with Openlayer the product** (platform bugs, account problems) — only
for issues with this skill's instructions and behavior.

## What to do

1. Confirm it's a skill issue, not a product issue.
2. Capture specifics: what the skill said, what actually happened, and — crucially — the docs URL that
   contradicted the skill (so the fix is verifiable).
3. With the user's OK, report it:
   - Open an issue at `https://github.com/openlayer-ai/openlayer-skills/issues`, or
   - Email `support@openlayer.com`.
4. If you can, propose the concrete edit (which reference file, what line should change) so a maintainer
   can apply it quickly. See `agents.md` in the repo for contribution guidance.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Silently working around wrong skill guidance | The skill stays wrong for everyone | Surface it and offer to report |
| Reporting a product bug as skill feedback | Misrouted | Send product issues to Openlayer support, not the skills repo |
| Reporting without the contradicting doc URL | Not actionable | Always capture the source that proves the correct behavior |
