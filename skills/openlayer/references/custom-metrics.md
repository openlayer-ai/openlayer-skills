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
├── run.py            # defines a Metric(BaseMetric) with compute_on_dataset()
├── requirements.txt  # must include openlayer (e.g. openlayer>=0.2.0a26)
└── config.json       # display name, description, lowerBound/upperBound, install/run commands, optional params
```

`run.py` implements `compute_on_dataset(self, dataset) -> MetricReturn` (returns a score, unit,
metadata, optional added columns). Compute fresh per call — don't stash mutable state on the instance.
Configurable parameters declared in `config.json` are read at runtime from an auto-generated
`params.json`, so behavior can change without editing code. Confirm the exact `BaseMetric` /
`MetricReturn` shapes from the docs.

## 2. Push / run with the CLI

```bash
openlayer metrics push -d my_metric     # register on the platform (-d/--directory, default "metrics")
openlayer metrics run  -d my_metric     # execute locally to test
openlayer metrics pull                  # fetch existing metrics into the working dir
```

The CLI reads `OPENLAYER_API_KEY` / `OPENLAYER_BASE_URL` from env (see `references/cli.md`), so push
runs headless.

## 3. Use it in a test

Reference the registered metric key from a test threshold (a `metricThreshold`-style test with the
metric's key as the `measurement`). See `references/tests.md`; for the test workflow see
`references/development-setup.md`.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| `requirements.txt` missing `openlayer` | Metric won't run on the platform | Pin `openlayer>=…` per the docs |
| No `lowerBound`/`upperBound` in `config.json` | Score range undefined | Set the bounds |
| Mutable state on the `Metric` instance | Nondeterministic scores | Compute fresh inside `compute_on_dataset` |
| Wrong `-d` directory | Pushes nothing / wrong metric | Point `-d` at the metric dir (default `metrics`) |
| Hardcoding tunables instead of `params.json` | Can't reconfigure without a re-push | Declare params in `config.json`, read from `params.json` |
| Referencing the metric in a test before pushing | Test can't find the metric | Push first, then author the test against its key |
