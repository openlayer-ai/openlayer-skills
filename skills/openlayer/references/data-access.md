---
name: openlayer-data-access
description: Read or modify Openlayer data programmatically — projects, inference pipelines, commits, test results, rows. Use when querying or mutating the platform via MCP, the SDK, or raw REST. Note the CLI is NOT for data access.
---

# Openlayer Data Access (the "API" plane)

Pick the highest available tier. The CLI is **not** here — it is the dev/push workflow tool (`references/cli.md`).

(If the Openlayer MCP server happens to be connected, prefer its typed tools — covered in a separate skill.)

## Tier 1 — SDK (typed client)

Install latest (`references/sdk-upgrade.md`). Init: `Openlayer(api_key=...)` (Python, also
`AsyncOpenlayer`) or `new Openlayer({ apiKey })` (TS). Reads `OPENLAYER_API_KEY` /
`OPENLAYER_BASE_URL` from env if omitted. **Confirm method names from the docs/SDK** — don't guess.

Resource map (Python; TS mirrors with camelCase):

| Resource | What |
| --- | --- |
| `client.projects` | create / list / delete projects (`task_type`: llm-base, tabular-classification, tabular-regression, text-classification) |
| `client.projects.inference_pipelines` | create / list monitoring pipelines |
| `client.projects.commits` | list dev commits (versions) |
| `client.projects.tests` | create / update / list tests |
| `client.commits` / `client.commits.test_results` | retrieve a commit; list its test results |
| `client.inference_pipelines.rows` | list / update rows (e.g. add ground truth) |
| `client.inference_pipelines.data` | `.stream(...)` to publish rows — see `references/data-streaming.md` |
| `client.inference_pipelines.test_results` | list a pipeline's test results |
| `client.storage.presigned_url` | presigned URLs for dataset/file uploads |
| `client.workspaces` (`.api_keys`, `.invites`) | workspace admin |

## Tier 2 — Raw REST

Last resort when the SDK isn't set up. Base URL `https://api.openlayer.com/v1` (or your
self-hosted/local `OPENLAYER_BASE_URL`); bearer `OPENLAYER_API_KEY`. Find endpoints in the API
reference via https://docs.openlayer.com/llms.txt (REST API section).

## Choosing a tier

Writing app code that already imports the SDK? → SDK. A one-off shell query with no SDK installed? →
SDK install is still usually cleaner than raw REST; use REST only when you can't add a dependency.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Reaching for the CLI to read data | CLI is push/workflow, not a REST client | Use the SDK / REST |
| Guessing SDK method names | Wrong call, runtime error | Confirm from the SDK docs/reference |
| Raw REST when the SDK is available | More brittle, no types | Prefer the SDK |
| Wrong base URL on self-hosted/local | 401/404 | Set `OPENLAYER_BASE_URL` to the right host |
| Ignoring pagination on list endpoints | Missing data | Page through (`page` / `per_page`) until exhausted |
| New client per call | Slow / wasteful | Reuse one client instance |
