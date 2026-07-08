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
metrics/                    # the dir you pass to `-d` (default is `metrics/`)
└── wordCountUnderLimit/     # ONE subdir per metric, named EXACTLY the metric key
    ├── run.py               # Metric(metrics.BaseMetric) with compute_on_dataset(); ends with Metric().run()
    ├── requirements.txt     # must include openlayer
    └── config.json          # installCommand, runCommand, name, description, lowerBound, upperBound (+ optional parameterDefinitions[])
```

`-d` points at the **parent** directory; each metric is a **subdirectory** of it. Pointing `-d` straight
at a leaf metric dir (the one holding `run.py`) makes the CLI report "0 metrics" and push nothing.

**Copy this complete `run.py` shape — do NOT copy the run.py from the docs page.** The docs example reads
the model output via `data[config["outputColumnName"]]` / `dataset.config[...]`; that key is **absent at
server evaluation**, so the metric raises a `KeyError` and the test **errors instead of evaluating**. The
model output is always the canonical column `dataset.df["openlayer_output"]` (see `references/tests.md` for
the other `openlayer_*` names). Only cross-check the `BaseMetric` / `MetricReturn` *class API* against the docs.

```python
from openlayer.lib.core import metrics

class Metric(metrics.BaseMetric):
    def compute_on_dataset(self, dataset: metrics.Dataset) -> metrics.MetricReturn:
        # dataset.df is a pandas DataFrame; compute fresh (no mutable instance state).
        # Model output = the canonical column `dataset.df["openlayer_output"]` (NOT config["outputColumnName"]).
        df = dataset.df
        under_limit = df["openlayer_output"].astype(str).str.split().str.len() <= 50
        return metrics.MetricReturn(value=float(under_limit.mean()), unit=None, meta=None, added_cols=set())

if __name__ == "__main__":   # REQUIRED — the CLI invokes the metric this way
    Metric().run()
```

Note the field names: `MetricReturn(value=, unit=, meta=, added_cols=)` (it's `value`/`meta`, not
`score`/`metadata`). Optional configurable parameters declared in `config.json` are read at runtime
from an auto-generated `params.json`, so behavior changes without editing code.

## 2. Test locally, then push

```bash
openlayer metrics push               # register the metric; `-d` defaults to `metrics/` (the parent dir, not the leaf)
openlayer metrics run -d metrics     # optional local run — needs deps installed and may not work for a
                                     # shell-only setup, so rely on the pushed commit's goal status instead
```

`push` reads `OPENLAYER_API_KEY` / `OPENLAYER_BASE_URL` / `OPENLAYER_PROJECT_ID` from env (see
`references/cli.md`). `openlayer metrics pull` fetches existing metrics into the working dir, and
`openlayer metrics delete <key>` removes one.

**Name the metric directory exactly the metric `key`** (e.g. key `wordCountUnderLimit` → dir
`wordCountUnderLimit/`). At evaluation the platform extracts the bundle and looks for `<key>/run.py`; a
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
| Pointing `-d` at the leaf metric dir | CLI reports "0 metrics", pushes nothing | `-d` is the PARENT dir; put the metric in a `<key>/` subdir (default `-d metrics`) |
| Reading output via `outputColumnName` / `dataset.config` in `run.py` | KeyError → the test errors instead of evaluating | Read `dataset.df["openlayer_output"]` (canonical output column) |
| Hardcoding tunables instead of `params.json` | Can't reconfigure without a re-push | Declare params in `config.json`, read from `params.json` |
| Referencing the metric in a test before pushing | Test can't find the metric | Push first, then author the test against its key |
