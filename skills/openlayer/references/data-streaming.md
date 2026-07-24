---
name: openlayer-data-streaming
description: Publish/stream inference rows to an Openlayer inference pipeline with the per-task-type config object (ConfigLlmData and friends). Use when sending production data directly instead of (or alongside) SDK tracing.
---

# Openlayer Data Streaming (publishing rows)

Use this when you want to push inference data directly to a pipeline rather than via `@trace`
auto-publish — batch jobs, non-Python services, or backfills.

Docs: stream/upload examples are in the SDK `examples/` and the monitoring docs — discover via
https://docs.openlayer.com/llms.txt (monitoring + REST API → monitoring). Confirm the current config
fields from the docs before coding.

## How it works

`client.inference_pipelines.data.stream(inference_pipeline_id=..., config=<task-config>, rows=[...])`.
The **config** describes how your row columns map to Openlayer's semantics; the **rows** are dicts
whose keys must match the names declared in the config.

For `llm-base`, the config (e.g. `ConfigLlmData`) maps columns:
- Required: `output_column_name`, `input_variable_names` (list).
- Optional: `cost_column_name`, `num_of_token_column_name`, `latency_column_name`,
  `timestamp_column_name`, `ground_truth_column_name`, `context_column_name`, `question_column_name`,
  `user_id_column_name`, `session_id_column_name`, `inference_id_column_name`, plus `metadata`.

Other task types have their own config classes. Match the config class to the project's task type.
For **traditional / tabular ML** (the `ConfigTabular*` classes, their required fields, and the batch
`upload_batch_inferences` alternative), see `references/traditional-ml.md`.

Include an `inference_id` per row if you'll later add ground truth or update the row
(`client.inference_pipelines.rows.update(...)`).

## Stream vs trace — don't double-publish

If the app is already instrumented with `@trace` / a wrapper (`references/monitoring-instrumentation.md`),
those traces already publish to the pipeline. Streaming the same data again creates duplicates. Use
streaming *instead of* tracing for that path, not in addition.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Row keys don't match config column names | Columns unmapped / dropped | Make row dict keys exactly match the `*_column_name` values |
| Wrong config class for the task type | Validation error | Use the config matching the project `task_type` |
| Streaming data that tracing already publishes | Duplicate rows | Pick one path per request flow |
| No `inference_id` | Can't correlate later ground-truth updates | Set `inference_id_column_name` and provide stable ids |
| Wrong timestamp unit/format | Rows mis-ordered or rejected | Use the unit the docs specify |
| Row values are numpy scalars (from a pandas row) | Server dtype validation 400 (e.g. "must be int32/int64") | Cast to native Python types (`int(...)`, `.item()`) before streaming |
| Guessing config field names | Runtime error | Confirm fields from the current docs/SDK |
