---
name: openlayer-fix-loop
description: Debug and fix failing Openlayer tests with the MCP fix-loop — inspect failed rows, propose a fix, apply and re-push, and wait for results. Use when development or monitoring tests are failing and the user wants help resolving them.
---

# Openlayer MCP Fix-Loop

An agentic loop to resolve failing tests. **Requires the Openlayer MCP server** (`references/mcp-setup.md`).

## Development-mode loop (failing commit tests)

1. **Find the failing goal:** `list_commit_test_results(project_version_id)` → identify the failed
   goal and its `goal_id`.
2. **Inspect evidence:** `fetch_failed_rows_for_goal(goal_id, page, per_page)` — read the actual rows
   that failed, not just the metric. Understand *why* before changing anything.
3. **Propose a fix:** `propose_fix(goal_id, project_version_id)` for an AI-assisted suggestion, or
   reason from the failed rows yourself.
4. **Apply and re-push:** `apply_and_push(project_id, directory, message, file_edits)` — applies edits
   and pushes a new commit. Add regression coverage with `add_rows_to_dataset` when relevant.
5. **Verify:** `wait_for_commit_results(project_version_id, timeout, poll_interval)` and confirm the
   goal now passes. Loop if not.

## Monitoring-mode (live failures)

`diagnose_monitoring_failure(project_name_or_id, goal_name)` chains pipeline → tests → failed rows to
locate a live failure, then inspect rows and decide on a fix (often a prompt/code change or a guardrail).

## Discipline

- **Inspect rows before fixing.** A passing metric isn't the goal — a correct system is.
- **Keep a human gate on `apply_and_push`.** It mutates the user's repo and pushes a commit; confirm
  the edits with the user first unless they've said to proceed autonomously.
- **Don't overfit to the failing rows.** A fix that only patches the specific failures (e.g. hardcoding)
  is worse than none. Generalize, and add regression rows so the fix is protected.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Running the loop without MCP | Tools unavailable | Set up `openlayer-mcp` first |
| Fixing from the metric alone | Wrong root cause | `fetch_failed_rows_for_goal` and read the rows |
| `apply_and_push` without confirmation | Unwanted commits to the user's repo | Confirm edits before applying |
| Overfitting the prompt/code to failures | Brittle, regresses elsewhere | Generalize; add regression rows |
| Not re-verifying after the fix | "Fixed" but still failing | Always `wait_for_commit_results` and confirm pass |
| Ignoring `type` (integrity vs performance) | Misdiagnosis | A data-integrity failure needs a data fix, not a prompt tweak |
