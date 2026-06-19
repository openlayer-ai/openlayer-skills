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

## 2. Push / run with the CLI

```bash
openlayer metrics push -d my_metric     # register on the platform (-d/--directory, default "metrics")
openlayer metrics run  -d my_metric     # execute locally to test
openlayer metrics pull                  # fetch existing metrics into the working dir
```

The CLI reads `OPENLAYER_API_KEY` / `OPENLAYER_BASE_URL` from env (see `references/cli.md`), so push
runs headless. Registration calls `PUT /projects/{id}/metric-settings` with `{key, name, description,
lowerBound, upperBound, storageUri}` — the server **auto-detects** that it's custom (the `custom` field
is read-only and set server-side). Don't send `custom` yourself, or you'll get
`Property is read-only - 'metricSettings.0.custom'`.

> **Known CLI bug (verified):** current `openlayer metrics push` bundles + uploads fine but then
> **fails registration** with exactly that `metricSettings.0.custom` error, because it round-trips the
> read-only field. Until it's fixed, register via the **direct API** instead: `PUT /projects/{id}/metric-settings`
> with the body above and **no `custom`** (returns 200; the server sets `custom: true`). Remove a metric
> with `DELETE /projects/{id}/metric-settings?key=<key>`.

## 3. Use it in a test

Reference the registered metric key from a test threshold (a `metricThreshold`-style test with the
metric's key as the `measurement`). See `references/tests.md`; for the test workflow see
`references/development-setup.md`.

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
