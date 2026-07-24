---
name: openlayer
description: >-
  Use when integrating, instrumenting, evaluating, or testing an app with Openlayer — the AI
  evaluation and observability platform. Covers BOTH modes: (1) MONITORING/live — add tracing to
  LLM or agent code with the openlayer Python or TypeScript SDK (@trace, trace_openai /
  trace_anthropic / trace_litellm / trace_bedrock and the LangChain callback), publish inference
  rows, enrich traces with user/session context, metadata, and guardrails; and (2) DEVELOPMENT/offline
  — author openlayer.json + tests.json, push commits with the Openlayer CLI or MCP, gate CI/CD, and
  run the fix-loop on failing rows. Also covers creating tests (the prebuilt catalog, thresholds),
  inference pipelines, and programmatic data access. Trigger when the user mentions Openlayer,
  OPENLAYER_API_KEY, OPENLAYER_INFERENCE_PIPELINE_ID, openlayer.json, tests.json, an inference pipeline,
  "openlayer push", openlayer-mcp, trace_openai / trace_anthropic, Openlayer guardrails, or LLM evals.
license: Apache-2.0
allowed-tools:
  - WebFetch(domain:docs.openlayer.com)
  - WebFetch(domain:openlayer.com)
  - Bash(openlayer whoami*)
  - Bash(openlayer projects*)
  - Bash(openlayer inspect*)
  - Bash(openlayer validate*)
  - Bash(curl *docs.openlayer.com/*)
---

# Openlayer

This skill helps you integrate apps with Openlayer correctly and fast — instrumenting code for live
monitoring, setting up offline evals, creating tests and guardrails, gating CI/CD, and accessing data.

## Core Principles

Follow these for ALL Openlayer work:

1. **Docs-first.** NEVER implement from memory — the SDKs, CLI, MCP, and test catalog change often.
   Resolve the current API from the docs before writing code. See `references/docs-access.md`.
2. **Use the latest versions.** Install/upgrade `openlayer` (PyPI) / `openlayer` (npm) to latest; don't
   downgrade to match an old snippet. See `references/sdk-upgrade.md`.
3. **Identify the mode FIRST** — this is the primary routing decision:
   - **Monitoring (live):** the user is shipping real traffic and wants traces/observability and
     continuous tests on production data → `references/monitoring-instrumentation.md`.
   - **Development (offline):** the user wants to evaluate a model/app version against datasets before
     shipping, with results gating a commit/PR → `references/development-setup.md`.
   - Unsure? Ask one question: "Do you want to evaluate live production traffic, or test a version
     offline before shipping?" Many teams eventually use both.
4. **Minimal footprint.** Wrap existing clients and decorate existing functions — don't rewrite app logic.
5. **Never hardcode keys.** Use env vars: `OPENLAYER_API_KEY`, `OPENLAYER_BASE_URL` (self-hosted/local
   only), `OPENLAYER_INFERENCE_PIPELINE_ID`, `OPENLAYER_DISABLE_PUBLISH`. Don't ask the user to paste
   keys into chat — have them set the env var or a `.env`. Keys: Workspace settings → API keys.

## Data access (the "API" plane)

When you need to read or modify Openlayer data programmatically, use this tiered fallback. Details and
the SDK resource map are in `references/data-access.md`.

1. **SDK (default).** Use the typed client: `Openlayer(api_key=...)` (Python) or `new Openlayer({ apiKey })` (TS).
2. **Raw REST** via the OpenAPI as a last resort.

(If the Openlayer MCP server happens to be connected, prefer its tools — covered in a separate skill.)

> The Openlayer **CLI is NOT the data-access tool** — it is the development/push workflow tool
> (`openlayer push`, `validate`, `export`, …). See `references/cli.md`.

## Documentation access

Openlayer docs at `docs.openlayer.com` are agent-friendly:

- **Index:** fetch `https://docs.openlayer.com/llms.txt` — every page listed as `[title](url.md): description`.
- **Read a page as markdown:** append `.md` to any docs URL (e.g. `https://docs.openlayer.com/monitoring/instrument.md`).
- **Search:** the `search_openlayer_docs` MCP tool, and a hosted docs MCP at `docs.openlayer.com/mcp`.

Preference order: search (when topic is fuzzy) → `llms.txt` lookup → fetch the specific `.md`. See
`references/docs-access.md`.

## Use case specific references

| If the user wants to…                                   | Read                                      |
| ------------------------------------------------------- | ----------------------------------------- |
| Add live tracing / observability to code               | `references/monitoring-instrumentation.md` |
| Monitor or evaluate a traditional / tabular ML model (scikit-learn, XGBoost, regression/classification) | `references/traditional-ml.md` |
| Set up offline evals (`openlayer.json` / `tests.json`)  | `references/development-setup.md`          |
| Create or choose tests / thresholds                     | `references/tests.md`                      |
| Add runtime guardrails (block/redact PII, injection)    | `references/guardrails.md`                 |
| Author a custom metric                                  | `references/custom-metrics.md`             |
| Set up compliance frameworks / governance               | `references/governance.md`                 |
| Route LLM calls through the Openlayer Gateway           | `references/gateway.md`                    |
| Subscribe to platform events via webhooks               | `references/webhooks.md`                   |
| Publish or stream inference rows directly               | `references/data-streaming.md`             |
| Gate CI/CD on eval results                              | `references/ci-cd.md`                      |
| Query data programmatically                             | `references/data-access.md`                |
| Install/use the Openlayer CLI                           | `references/cli.md`                        |
| Find or fetch docs                                      | `references/docs-access.md`                |
| Install or upgrade the SDK                              | `references/sdk-upgrade.md`                |
