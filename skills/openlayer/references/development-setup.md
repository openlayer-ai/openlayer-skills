---
name: openlayer-development
description: Set up Openlayer offline (development-mode) evaluation — author openlayer.json + tests.json + datasets and push a commit. Use when evaluating a model/app version against datasets before shipping, or wiring Openlayer into a pre-merge workflow.
---

# Openlayer Development — Offline Evaluation Setup

Development mode evaluates a *version* of your system against datasets before you ship it. You author
config files, push a commit, and Openlayer runs your model over the datasets, computes insights, and
evaluates your tests — gating the commit.

**Fetch current schemas and examples from the docs before writing config:**
- Workflow + push: https://docs.openlayer.com/development/overview.md and https://docs.openlayer.com/guides/cli-push.md
- `openlayer.json`: https://docs.openlayer.com/development/openlayer-json.md
- `tests.json`: https://docs.openlayer.com/development/tests-json.md
- Output generation (shell vs full model): https://docs.openlayer.com/development/configuring-output-generation.md

## Workflow

### 1. Pick the task type

One of `llm-base`, `tabular-classification`, `tabular-regression`, `text-classification`. This drives
which fields the config and datasets need.

### 2. Author `openlayer.json`

Five sections: `taskType` (required), `model` (required), `datasets` (required), `testsPath`
(optional, points at `tests.json`), `metrics` (optional). Key choices:
- `model.modelType`: `"shell"` (you provide precomputed outputs in the dataset — simplest, no runtime)
  or `"full"` (Openlayer runs your code: `runtime`, `installCommand`, `batchCommand` with `{{ path }}`
  and `{{ name }}` placeholders, `outputDirectory`).
- `datasets[]`: each needs `name`, `label` (`"validation"` or `"training"`), `path`, optional
  `groundTruthColumnName`. Task-specific: `llm-base` → `inputVariableNames`; classification →
  `classNames`; tabular → `featureNames`. **Dataset column names must match what the config declares.**

### 3. Author `tests.json`

An array of Test objects. Each: `name`, `type` (`integrity` | `consistency` | `performance`),
`subtype` (the platform's test id), `mode: "development"`, `thresholds[]`, and `syncId` (a UUID).
Development-mode tests also set `usesValidationDataset` / `usesTrainingDataset` / `usesMlModel`.
Threshold fields: `insightName`, `measurement`, `operator` (`is`, `>`, `>=`, `<`, `<=`), `value`,
optional `insightParameters`.

**Do not invent `subtype`/threshold shapes.** Copy a working example from the relevant test catalog
page (`https://docs.openlayer.com/tests/catalog/<test>.md`) or generate one with the MCP tool
`generate_test_config`. See `references/tests-and-guardrails.md`.

When a test targets the model output, reference it as **`openlayer_output`** (the canonical name), not
the raw `outputColumnName` value — a wrong column name makes the test silently **SKIPPED**, not failed.
After the push, check per-test status, not just pass/fail totals. See `references/tests-and-guardrails.md`.

### 4. Validate, then push

```bash
openlayer validate           # check openlayer.json + tests.json before pushing

# Non-interactive (agents/CI) — preferred. No `login`/`link` needed; the CLI reads env vars:
export OPENLAYER_API_KEY=...
export OPENLAYER_PROJECT_ID=...      # target project id (replaces interactive `openlayer link`)
export OPENLAYER_BASE_URL=...        # self-hosted/local only
openlayer push -m "message" -w       # -w waits for results; add -t to tail logs
```

`openlayer login` and `openlayer link` are interactive (TTY-only) and will hang an agent — skip them
and set `OPENLAYER_PROJECT_ID`. If you see `project id not found. Run 'openlayer link'`, set that env
var instead of running `link`. See `references/cli.md`.

Or via MCP when connected: `push_commit` then `wait_for_commit_results`. After push, Openlayer runs
the model, generates insights, evaluates tests, and reports pass/fail (commit logs in the app, Git,
or REST `commits.test_results`). See `references/cli.md` and `references/data-access.md`.

### 5. On failures

Inspect failing rows and iterate — `references/mcp-fix-loop.md` covers the agentic
`fetch_failed_rows_for_goal → propose_fix → apply_and_push → wait_for_commit_results` loop.

## Development vs Monitoring (don't mix them up)

| | Development (this file) | Monitoring (`monitoring-instrumentation.md`) |
| --- | --- | --- |
| Goal | Evaluate a version offline before shipping | Observe live production traffic |
| Inputs | `openlayer.json` + `tests.json` + datasets | Traces from instrumented code |
| Mechanism | `openlayer push` (commit) | SDK tracing → inference pipeline |
| Test `mode` | `development` | `monitoring` |

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Confusing dev push with monitoring publish | Wrong plane entirely | Dev = `openlayer push` commits; monitoring = SDK traces to a pipeline |
| Wrong or omitted `taskType` | Validation/run fails | Set one of the four task types; match dataset fields to it |
| Inventing `subtype` / threshold shape | Test won't sync or evaluate | Copy from the test catalog page or use MCP `generate_test_config` |
| Dataset column names don't match config | Rows fail / outputs unmapped | Align `inputVariableNames` / `featureNames` / `groundTruthColumnName` with the file |
| Pushing without `-w` in automation | Job "passes" before results exist | Use `-w` (or MCP `wait_for_commit_results`) and fail on failed tests |
| Skipping `openlayer validate` | Push fails late with a cryptic error | Always `validate` first |
| Secrets committed in `openlayer.json` | Leak | Keep keys in env vars, not the config |
| `modelType: "full"` with no/ wrong `batchCommand` | Output generation fails | Use `{{ path }}`/`{{ name }}` placeholders, or use `"shell"` with precomputed outputs |
