---
name: openlayer-tests
description: Create and configure Openlayer tests from the prebuilt catalog (80+) — thresholds, LLM-as-a-judge rubric, SQL-query, statistical, RAG, data-quality, and custom-metric tests. Use when choosing or authoring tests/evals in development or monitoring mode.
---

# Openlayer Tests

Tests ("goals") evaluate your data and pass/fail against thresholds — in development (on a commit) or
monitoring (on live traces). Openlayer ships 80+ prebuilt tests; **don't invent test configs — copy a
working shape from the catalog.**

Docs:
- Overview + browsing: https://docs.openlayer.com/tests/overview.md , https://docs.openlayer.com/tests/browse.md
- Catalog (one page per test, with a copy-paste config): https://docs.openlayer.com/tests/catalog/<test>.md — discover all via https://docs.openlayer.com/llms.txt
- Custom metrics: see `references/custom-metrics.md`

## Anatomy of a test

`name`, `type` (`performance` | `integrity` | `consistency`), `subtype` (the platform test id), `mode`
(`development` | `monitoring`), and `thresholds[]`. Each threshold: `insightName`, `measurement`,
`operator` (`is`, `>`, `>=`, `<`, `<=`), `value`, optional `insightParameters`.

- **Development** tests live in `tests.json` (see `references/development-setup.md`) or
  `projects.tests.create`; also set `usesValidationDataset` / `usesTrainingDataset` / `usesMlModel`.
- **Monitoring** tests run on live traces; set `evaluationWindow` / `delayWindow` (hours).

### Reference columns by their canonical `openlayer_*` names

When a threshold targets a column (`column_name` insight param, or a `subpopulationFilters`
measurement), use the platform's canonical names — model output is **`openlayer_output`** (NOT the raw
`outputColumnName`), plus `openlayer_latency` / `openlayer_num_of_tokens` / `openlayer_cost`. A wrong
name makes the test silently **SKIPPED** ("column not in dataset"), which a "0 failing" summary hides.
**After a push, check per-test status, not just totals.**

### Gotchas the catalog pages don't tell you (verified)

- **`insightParameters` is never `null`.** The catalog prints `"insightParameters": null` for some tests,
  but the API rejects null ("Field may not be null"). When a test takes params, use an array of
  `{name, value}`. When it takes none, **omit the key entirely** — for many subtypes (`hasPromptInjectionCount`,
  `metricThreshold`, and the no-param drift/profile tests `labelDrift`/`driftedFeatureCount`/
  `classImbalanceRatio`/`correlatedFeatureCount`) even `[]` is rejected ("Unknown field").
- **Catalog values can be wrong/stale — they fail at sync.** Seen: `columnDrift` `test_type` must be
  title-case **`"K-S Test"`** (catalog shows `"K-S test"`); `classImbalanceRatio` `operator` must be
  `<` or `<=` (catalog shows `>`). Cross-check the operator/enum the backend accepts, not just the catalog text.
- **Ground-truth metrics need a tabular task type.** accuracy/precision/recall/f1/falsePositiveRate/rocAuc
  (classification) and mae/mse/rmse/r2 (regression) are `metricThreshold` (`usesMlModel: true`) and require
  the dataset's `labelColumnName`/`targetColumnName` + predictions. Drift/profile tests
  (`columnDrift`, `correlatedFeatureCount`, `classImbalanceRatio`) need a **training** dataset
  (`usesTrainingDataset: true`). Prefer **explicit `columnDrift`** (with a `test_type`) — auto-method drift
  (`labelDrift`/`driftedFeatureCount`) may silently SKIP on some backends.
- **`type` drives `usesMlModel`.** `performance` tests require `usesMlModel: true` (even on a shell model);
  `integrity` / `consistency` tests use `usesMlModel: false`. A performance test with `false` is rejected
  ("Performance goals must use ML models...").
- **Not every catalog test supports every task type.** Many are tabular-only (`emptyFeature`,
  `dtypeValidation`, `featuresMissingValues`) or are rejected for `llm-base` despite the catalog listing
  it. The backend rejects an unsupported subtype×task at sync.
- **A single bad test fails the WHOLE push at sync** (Total Tests = 0) — you only get per-test status once
  sync passes. So fix sync-time rejections first, *then* read per-test pass/fail/skip.

## Catalog at a glance

LLM quality (faithfulness, hallucination, coherence, toxicity, bias, answer correctness/relevancy,
groundedness) · RAG (context recall/relevancy/utilization) · data quality (null/duplicate/dtype,
column & feature drift) · statistical (F1, precision/recall, accuracy, AUC, MAE, RMSE) · session-level
(cost, latency, tokens, goal/role/guideline adherence) · and the three below.

## Three common subtypes (copy these shapes; confirm from the catalog page)

**Metric threshold** (`metricThreshold`, `insightName: "metrics"`) — `measurement` is the metric key
(e.g. `answerRelevancy`, `conciseness`); operator + numeric `value`.

**LLM-as-a-judge** — https://docs.openlayer.com/tests/catalog/l-l-m-rubric-threshold.md
`subtype: "llmRubricThresholdV2"`, `insightName: "llmRubricV2"`, `measurement: "criteria0MeanScore"`,
with an `insightParameters` `criteria_list` of `{name, criteria, scoring}`. It's a **`performance`** test
→ set **`usesMlModel: true`** (the catalog example shows `false`, which the backend rejects). For a
reliable judge, keep criteria binary/specific and validate against a labeled set before trusting verdicts.

**SQL query** — https://docs.openlayer.com/tests/catalog/sql-query.md
`subtype: "sqlQuery"`, `insightName: "sqlQuery"`, `measurement: "result"`; `insightParameters` `query`
must reference the dataset as **`df`** and return a single number, e.g. `SELECT COUNT(*) FROM df`.

**Contains-PII** — `subtype: "containsPii"`, `measurement: "containsPIIRowCount"`. Requires **both**
`insightParameters` (exactly 2): `pii_type` (a list, e.g. `["EMAIL_ADDRESS","PHONE_NUMBER"]`) **and**
`column_name` (e.g. `openlayer_output`). Supplying only one fails sync with "Length must be 2".

### LLM-quality / RAGAS metrics (verified)

The LLM/RAG quality metrics are all **`metricThreshold`** (`type: performance`, `usesMlModel: true`,
`insightName: "metrics"`) with `measurement` set to one of the **only valid keys**:
`faithfulness, answerCorrectness, answerRelevancy, contextRecall, contextRelevancy, contextUtilization,
hallucination, coherence, conciseness, correctness, harmfulness, maliciousness`. Example:

```json
{ "name": "Faithful to context", "type": "performance", "subtype": "metricThreshold",
  "mode": "development", "usesValidationDataset": true, "usesMlModel": true, "syncId": "<uuid>",
  "thresholds": [{ "insightName": "metrics", "measurement": "faithfulness", "operator": ">", "value": 0.9 }] }
```

- **Bias** is a separate subtype: `llmBiasThreshold` (`insightName: "llmBias"`, `measurement: "biasMeanScore"`).
- **`toxicity` and `groundedness` are NOT valid `metricThreshold` measurements** — catalog pages exist but
  there's no such goal; using them fails the whole push at sync. Check those via an `llmRubricThresholdV2`
  criterion instead.
- **RAG metrics need column mappings** the public `openlayer.json` doc omits: set `contextColumnName`
  (and `questionColumnName`) on the dataset, or context-dependent metrics (faithfulness, hallucination,
  contextRecall/Relevancy/Utilization) can't compute. These judges read the configured output
  automatically — no `openlayer_output` column param needed.

Discover valid configs programmatically with the MCP `generate_test_config` tool when the Openlayer
MCP is connected (covered in a separate skill).

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Inventing a `subtype`/threshold shape | Won't sync or evaluate | Copy from the catalog page (`tests/catalog/<test>.md`) |
| Targeting raw `output` instead of `openlayer_output` | Test silently SKIPPED | Use canonical `openlayer_*` column names |
| Trusting "0 failing" totals | A skipped test isn't failing | Check per-test status after a push |
| Wrong `type` for the metric | Misclassified test | Match `performance`/`integrity`/`consistency` to the catalog entry |
| SQL test not selecting from `df` / returning many values | Test errors | Query `FROM df`, return one number |
| Rubric test missing `criteria_list` params | Judge can't run | Provide the criteria per the catalog page |
