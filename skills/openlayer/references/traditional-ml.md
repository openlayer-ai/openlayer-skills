---
name: openlayer-traditional-ml
description: Monitor or evaluate a traditional / tabular ML model (scikit-learn, XGBoost, LightGBM — regression or classification) with Openlayer. Use INSTEAD of the tracing/@trace path when there is no LLM call to wrap. Covers monitoring (stream vs batch publish with typed tabular configs) and offline dev (run_batch_from_df).
---

# Openlayer for Traditional / Tabular ML

For classic ML (scikit-learn, XGBoost, LightGBM, …) there is **no LLM call to wrap**, so the
`@trace` decorator and provider wrappers (`trace_openai`, …) are the **wrong tool**. Publish the
model's predictions directly instead. This applies to `tabular-classification`, `tabular-regression`,
and `text-classification` projects. The project's **task type** picks the typed config class in both
modes.

## Monitoring (live) — publish predictions to an inference pipeline

**First decide: stream or batch.** Ask the user which fits their system:

- **Stream** — publish predictions as they happen (online serving, per-request). One or a few rows at
  a time via `client.inference_pipelines.data.stream(inference_pipeline_id=..., config=<typed>, rows=[...])`.
- **Batch** — publish periodically in bulk (a nightly/hourly scoring job, a backfill). A whole
  DataFrame at once via `openlayer.lib.data.upload_batch_inferences(client, inference_pipeline_id=..., config=<typed>, dataset_df=...)`.

Both take the **same typed config** describing how your columns map to Openlayer's semantics
(`openlayer.types.inference_pipelines.data_stream_params`):

- `ConfigTabularClassificationData`: `class_names`, `feature_names`, `categorical_feature_names` (send
  all three together — see Common Mistakes), `predictions_column_name`, `prediction_scores_column_name`
  (per-class **lists**), `label_column_name` (ground truth — NOT `ground_truth_column_name`).
- `ConfigTabularRegressionData`: `feature_names`, `predictions_column_name`, `target_column_name`.

Row dict keys (stream) / DataFrame columns (batch) must match the `*_column_name` values in the config.

If ground truth (the true label/target) arrives later, set `inference_id_column_name` in the config
and provide a stable id per row, then patch labels in with
`openlayer.lib.data.update_batch_inferences(...)`. See `references/data-streaming.md` for the shared
stream/config mechanics and `references/monitoring-instrumentation.md` for why `@trace` does not apply
here.

Docs: SDK stream + batch walkthrough at
https://docs.openlayer.com/monitoring/publishing-tabular-predictions.md; ground-truth updates at
https://docs.openlayer.com/monitoring/updating-data.md.

## Development (offline) — let Openlayer run your tabular model

Use a **`full`** model in `openlayer.json` (see `references/development-setup.md` for the full config
shape and the tabular gotchas). The `batchCommand` runs a Python script — by convention
`openlayer_run.py` — that Openlayer invokes over each dataset. That script must:

1. Define a class subclassing `OpenlayerModel` (`from openlayer.lib.core.base_model import OpenlayerModel, RunReturn`).
2. Implement **`run_batch_from_df(self, df) -> (df, config)`** — score the whole DataFrame, add a
   predictions column, and return the df plus a config dict (`predictionsColumnName`, `featureNames`,
   `categoricalFeatureNames`, and `classNames` for classification). Do **not** implement the per-row
   `run` method for tabular models — leave it raising `NotImplementedError`.
3. End with `if __name__ == "__main__": MyModel().run_from_cli()`. `run_from_cli()` reads
   `--dataset-path` and `--output-dir` — **you must pass both yourself in `batchCommand`; Openlayer
   does not append them.** Use exactly:
   `python model/openlayer_run.py --dataset-path {{ path }} --output-dir {{ outputDirectory }}/{{ name }}`

Copy the canonical example rather than writing from scratch:
https://github.com/openlayer-ai/templates/blob/main/python/tabular-regression/scikit-learn/diabetes-predictor/app/model/openlayer_run.py
(and the classification sibling under `python/tabular-classification/`). Docs:
https://docs.openlayer.com/development/configuring-output-generation.md.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Reaching for `@trace` / `trace_openai` on a tabular model | Nothing to wrap; no rows publish | Publish predictions directly — stream or batch (above) |
| Implementing per-row `run` for a dev-mode tabular model | Openlayer expects batch scoring | Implement `run_batch_from_df(df)`; leave `run` as `NotImplementedError` |
| `batchCommand` missing `--output-dir` (or adding flags `run_from_cli` doesn't accept) | Server run fails (`output_dir=None`, or `unrecognized arguments`) | Pass exactly `--dataset-path {{ path }} --output-dir {{ outputDirectory }}/{{ name }}` — nothing else |
| Wrong / omitted typed config class | Stream/upload validation error | Match the config class to the project task type (`ConfigTabular*`) |
| Omitting `categorical_feature_names` for tabular-classification | 400 `not valid under any of the given schemas` (SDK marks it optional; server requires it) | Always send `class_names` + `feature_names` + `categorical_feature_names` (use `[]` if none) |
| Row keys / DataFrame columns don't match config | Columns unmapped or dropped | Make keys/columns exactly equal the `*_column_name` values |
| Using `ground_truth_column_name` for tabular | Rejected / label unmapped | Use `label_column_name` (classification) / `target_column_name` (regression) |
| No `inference_id` when ground truth comes later | Can't correlate the update | Set `inference_id_column_name` + stable ids; patch with `update_batch_inferences` |
| Guessing config field names from memory | Runtime error | Confirm current fields from the docs/SDK |
