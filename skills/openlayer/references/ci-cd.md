---
name: openlayer-ci-cd
description: Gate CI/CD on Openlayer evaluation results — run an offline commit on each PR and fail the build when tests fail. Use when setting up pre-merge eval gates (GitHub Actions or other CI).
---

# Openlayer CI/CD Eval Gates

Block merges when a model/app version fails its Openlayer tests. This builds on development mode
(`references/development-setup.md`).

Docs: https://docs.openlayer.com/guides/gh-actions.md and https://docs.openlayer.com/guides/cli-push.md

## Checklist

- [ ] The repo has a valid `openlayer.json` + `tests.json` and `openlayer validate` passes locally.
- [ ] Decide the trigger (PR, push to a branch, manual dispatch) with the user.
- [ ] Install the CLI in the job (cache it where possible).
- [ ] Push and **wait** so results gate the job:
      `openlayer push -m "CI: $GIT_SHA" -w` — the exit code reflects test pass/fail; let a non-zero
      exit fail the build. (Agentic CI alternative: MCP `push_commit` + `wait_for_commit_results`.)
- [ ] Store `OPENLAYER_API_KEY` as a CI secret; never echo it. Add any provider keys the model needs
      (OpenAI/Anthropic/etc.) as secrets too.
- [ ] Verify by opening a real PR and watching the check.

## Notes

- Without `-w`, the job finishes before evaluation completes and the gate is meaningless.
- Forked-PR builds can't read secrets (GitHub) — use a trusted trigger (internal PR, branch push, or
  `workflow_dispatch`) or document the limitation.
- Confirm the exact recommended Action/commands from the gh-actions doc — Openlayer may provide a
  prebuilt GitHub Action; prefer it over hand-rolling when available.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| `push` without `-w` | Build passes before results exist | Use `-w` (or MCP `wait_for_commit_results`) |
| Not failing on failed tests | Gate is cosmetic | Propagate the non-zero exit / check results and fail |
| API key echoed in logs | Leak | Use CI secrets; never print the key |
| Missing provider secrets (full model) | Output generation fails in CI | Add OpenAI/Anthropic/etc. keys as secrets |
| Forked PR can't access secrets | Check fails to run | Use a trusted trigger or document it |
| Re-pushing identical commits | Wasted runs | Push only on relevant changes |
