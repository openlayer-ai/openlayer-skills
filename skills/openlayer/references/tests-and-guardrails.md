---
name: openlayer-tests-and-guardrails
description: Create Openlayer tests from the prebuilt catalog (thresholds, performance/integrity/consistency) and configure runtime guardrails. Use when choosing or defining tests/evals, or blocking unsafe outputs at runtime.
---

# Openlayer Tests & Guardrails

Tests evaluate data after the fact (dev commits or live traces). Guardrails enforce policy at runtime.

Docs:
- Tests overview + browsing: https://docs.openlayer.com/tests/overview.md and https://docs.openlayer.com/tests/browse.md
- Test catalog (one page per test): https://docs.openlayer.com/tests/catalog/<test>.md — discover all via https://docs.openlayer.com/llms.txt
- Guardrails: https://docs.openlayer.com/guardrails/overview.md

## Use the catalog — don't invent test configs

Openlayer ships 70+ prebuilt tests (accuracy, answer-correctness, faithfulness, hallucination, bias,
contains-PII, prompt-injection, column-drift, latency, cost, exact-match, BLEU, …). The reliable way
to configure a test is to **copy a working example**, not to guess the `subtype`/threshold shape:

1. **MCP (best):** `discover_openlayer_schema` to list task types + the test catalog, then
   `generate_test_config` to produce a valid test object from a catalog slug. See `references/mcp-setup.md`.
2. **Docs:** open the catalog page `https://docs.openlayer.com/tests/catalog/<test>.md` and copy its example.

## Anatomy of a test

A test (a "goal") has: `name`, `type` (`performance` | `integrity` | `consistency`), `subtype` (the
platform's test id), `mode` (`development` or `monitoring`), and `thresholds[]`. Each threshold:
`insightName`, `measurement`, `operator` (`is`, `>`, `>=`, `<`, `<=`), `value`, optional `insightParameters`.

- **Development** tests live in `tests.json` (see `references/development-setup.md`) or
  `projects.tests.create`; they also set `usesValidationDataset` / `usesTrainingDataset` / `usesMlModel`.
- **Monitoring** tests run on live traces and set `evaluationWindow` / `delayWindow` (hours).

Create programmatically via the SDK (`client.projects.tests.create(...)`) / REST / MCP — confirm the
exact payload from the docs or `generate_test_config`. Some tests (e.g. LLM-rubric) require specific
`insightParameters` (like the rubric text).

### Reference columns by their canonical `openlayer_*` names

When a test/threshold targets a column (e.g. a `column_name` insight parameter, or a
`subpopulationFilters` measurement), use the platform's **canonical column names, not the raw dataset
header**. The engine exposes:

- **`openlayer_output`** — the model output (this is what `outputColumnName` becomes; do NOT use the
  raw output header like `"output"`).
- `openlayer_latency`, `openlayer_num_of_tokens`, `openlayer_cost`, `openlayer_timestamp`, etc.
- Input variables and ground truth keep the names you declared (e.g. `input_data`, `ground_truth`).

A test that references a column the dataset doesn't expose is **silently SKIPPED** (not failed) with
`"The column '<name>' is not in the validation dataset."` — so a green "0 failing" summary can hide a
skipped test. **After a push, check per-test status, not just the pass/fail totals** — a `skipped`
test usually means a wrong `column_name` (use `openlayer_output`, not `output`).

## Tests vs guardrails

- **Test** = scored evaluation over data; surfaces pass/fail, trends, alerts. Use for quality/regression.
- **Guardrail** = runtime check in the request path that can block or modify an output before it
  returns. Use when you must *prevent* (not just observe) bad outputs. See the guardrails docs and the
  `openlayer.lib.guardrails` API; guardrails attach to traced functions.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Inventing a `subtype` or threshold shape | Test won't sync/evaluate | Copy from the catalog page or use `generate_test_config` |
| Wrong `type` for the metric | Test misclassified / unexpected behavior | Match `performance` vs `integrity` vs `consistency` to the catalog entry |
| Rubric/LLM tests missing `insightParameters` | Test can't run | Provide required params (e.g. the rubric) per the catalog page |
| Targeting the raw output header (`column_name: "output"`) | Test silently SKIPPED ("column not in dataset") | Use the canonical `openlayer_output` (and `openlayer_*` for latency/tokens/cost) |
| Trusting the "0 failing" summary | A skipped test isn't failing — totals hide it | Check per-test status after a push; investigate any `skipped` |
| Mismatched `operator`/`value` types | Threshold never triggers correctly | Use the operator+value the catalog example shows (`is` for categorical, comparison for numeric) |
| Building a guardrail when you only need observation | Unnecessary runtime risk/latency | Use a monitoring test instead; reserve guardrails for blocking |
| Assuming a guardrail blocks when it only logs | Bad outputs still returned | Configure the guardrail's action explicitly per the docs |
