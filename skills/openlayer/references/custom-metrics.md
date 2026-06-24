---
name: openlayer-custom-metrics
description: Author a custom Openlayer metric in Python, push it with the openlayer metrics CLI, and use it in a test. Use when the prebuilt test catalog lacks the metric you need and you want a bespoke score computed over a dataset.
---

# Openlayer Custom Metrics

When the catalog doesn't have the score you need, author a custom metric in Python and push it; then a
test can threshold on it.

Docs: https://docs.openlayer.com/tests/custom-metrics.md and the CLI command https://docs.openlayer.com/api-reference/cli/commands/metrics.md

## 1. Author (one directory per metric)

```
my_metric/
├── run.py            # Metric(metrics.BaseMetric) with compute_on_dataset(); ends with Metric().run()
├── requirements.txt  # must include openlayer
└── config.json       # installCommand, runCommand, name, description, lowerBound, upperBound (+ optional params)
```

`run.py` (shape — confirm against the docs):

```python
from openlayer.lib.core import metrics

class Metric(metrics.BaseMetric):
    def compute_on_dataset(self, dataset: metrics.Dataset) -> metrics.MetricReturn:
        # dataset.df is a pandas DataFrame; compute fresh (no mutable instance state)
        return metrics.MetricReturn(value=..., unit=None, meta=None, added_cols=set())

if __name__ == "__main__":   # REQUIRED — the CLI invokes the metric this way
    Metric().run()
```

Note the field names: `MetricReturn(value=, unit=, meta=, added_cols=)` (it's `value`/`meta`, not
`score`/`metadata`). Optional configurable parameters declared in `config.json` are read at runtime
from an auto-generated `params.json`, so behavior changes without editing code.

## 2. Test locally, then push

```bash
openlayer metrics run  -d my_metric     # execute locally to sanity-check the score
openlayer metrics push -d my_metric     # bundle, upload, and register the metric
```

`push` reads `OPENLAYER_API_KEY` / `OPENLAYER_BASE_URL` / `OPENLAYER_PROJECT_ID` from env (see
`references/cli.md`). `openlayer metrics pull` fetches existing metrics into the working dir, and
`openlayer metrics delete <key>` removes one.

**Name the metric directory exactly the metric `key`** (e.g. key `shortAnswerRate` → dir
`shortAnswerRate/`). At evaluation the platform extracts the bundle and looks for `<key>/run.py`; a
mismatched dir name makes the test error with `missing insights: ['customMetric']`.

## 3. Use it in a test

A custom metric is **not** a `metricThreshold`. It has its own subtype **`customMetricThreshold`** with a
fixed `insightName: "customMetric"` and a literal `measurement: "value"` — the metric **key goes in
`insightParameters`** as `{"name": "key", "value": "<metricKey>"}` (NOT as the `measurement`), alongside
any of the metric's own parameters. It's a `performance` test (`usesMlModel: true`). Example:

```json
{ "name": "Most answers are concise", "type": "performance", "subtype": "customMetricThreshold",
  "mode": "development", "usesValidationDataset": true, "usesTrainingDataset": false, "usesMlModel": true,
  "syncId": "<uuid>",
  "thresholds": [{ "insightName": "customMetric", "measurement": "value", "operator": ">=", "value": 0.75,
    "insightParameters": [
      { "name": "key", "value": "wordCountUnderLimit" },
      { "name": "max_words", "value": 50 } ] }] }
```

Push the commit (see `references/development-setup.md`); the metric runs over the dataset and the test
thresholds on its returned `value`.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| `requirements.txt` missing `openlayer` | Metric won't run on the platform | Include `openlayer` |
| Omitting `if __name__ == "__main__": Metric().run()` | CLI can't execute the metric | Keep the `__main__` block that calls `Metric().run()` |
| Returning `score=`/`metadata=` to `MetricReturn` | Wrong field names | Use `value=` and `meta=` |
| No `lowerBound`/`upperBound` in `config.json` | Score range undefined | Set the bounds |
| Mutable state on the `Metric` instance | Nondeterministic scores | Compute fresh inside `compute_on_dataset` |
| Wrong `-d` directory | Pushes nothing / wrong metric | Point `-d` at the metric dir (default `metrics`) |
| Hardcoding tunables instead of `params.json` | Can't reconfigure without a re-push | Declare params in `config.json`, read from `params.json` |
| Referencing the metric in a test before pushing | Test can't find the metric | Push first, then author the test against its key |
