---
name: openlayer-monitoring
description: Instrument an app with Openlayer tracing for live monitoring. Use when adding observability to LLM/agent code, wrapping an LLM client, or auditing existing Openlayer instrumentation.
---

# Openlayer Monitoring — Instrumentation

Add tracing to a live app so each request becomes a trace (inputs, outputs, intermediate steps,
tokens, cost, latency) that Openlayer runs tests and alerts on.

**Always fetch current code from the docs** — providers and helpers change. Start here:
- Quickstart: https://docs.openlayer.com/monitoring/instrument.md
- Other integrations (LangChain callback, LiteLLM, Bedrock, Gemini, ADK, etc.): https://docs.openlayer.com/monitoring/alternative-integrations.md
- TypeScript: look up the TS SDK section from https://docs.openlayer.com/llms.txt

## Workflow

### 1. Assess current state

- Is `openlayer` installed? (`pip show openlayer` / check `package.json`.)
- Which LLM provider/framework is used? Grep the code for `openai`, `anthropic`, `litellm`,
  `langchain`/`langgraph`, `bedrock`/`boto3`, `mistral`, `groq`, `gemini`/`google.generativeai`,
  `portkey`, `oci`. The right wrapper depends on this.
- Is there existing Openlayer instrumentation to audit instead of adding fresh?

**Prefer the matching integration over manual spans** — wrappers capture model name, tokens, and cost
automatically. Use `@trace()` only for your own (non-LLM) functions.

### 2. Set up credentials and a target pipeline

Traces publish to an **inference pipeline**. Both env vars are required — without the pipeline id,
traces are created but never published:

```bash
export OPENLAYER_API_KEY=...
export OPENLAYER_INFERENCE_PIPELINE_ID=...   # required to publish
# self-hosted / local backend only:
export OPENLAYER_BASE_URL=https://api.openlayer.com/v1
```

Get a pipeline id: create a project + inference pipeline in the app, or via MCP
(`create_project` → `create_inference_pipeline`) / SDK. See `references/data-access.md`.

### 3. Instrument (minimal footprint)

The pattern (Python): wrap the LLM client with the matching tracer, decorate the functions that make
up a request with `@trace()` (or `@trace_async()` for async). Available wrappers include
`trace_openai`, `trace_async_openai`, `trace_anthropic`, `trace_litellm`, `trace_bedrock`,
`trace_mistral`, `trace_groq`, `trace_gemini`, `trace_google_adk`, `trace_portkey`, `trace_oci_genai`,
plus a LangChain callback handler. Confirm the exact import and call from the docs above — do not
guess provider-specific signatures.

For frameworks without a wrapper, decorate your own functions with `@trace()`; nested decorated calls
become child steps automatically.

### 4. Run once, then verify a trace lands BEFORE adding more

Execute one real request, then confirm the trace appears (Data page in the app, or
`client.inference_pipelines.rows.list(...)` / MCP `list_inference_pipelines`). Do not add ten spans
before confirming the first one publishes — most failures are "configured but nothing arrives."

### 5. Enrich (only what's relevant — infer from code, ask when unclear)

| If the code has…                          | Add                          | Docs |
| ----------------------------------------- | ---------------------------- | ---- |
| Conversation history / chat endpoints     | user/session context         | https://docs.openlayer.com/monitoring/sessions-and-users.md |
| Retrieval / RAG                           | context (+ question)         | https://docs.openlayer.com/monitoring/context.md |
| Useful request attributes                 | metadata, promoted columns   | https://docs.openlayer.com/monitoring/metadata.md |
| Ground truth arriving later               | update rows after the fact   | https://docs.openlayer.com/monitoring/updating-data.md |

Use `update_current_trace` / `set_user_session_context` from `openlayer.lib` for context. For local
dev without publishing, set `OPENLAYER_DISABLE_PUBLISH=true`. Offline buffering is available for
unreliable networks (see the tracing docs).

### 6. Point the user to next steps

Tests run on the live traces — to add quality checks, go to `references/tests-and-guardrails.md`.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| `OPENLAYER_INFERENCE_PIPELINE_ID` not set | Traces created but never published — nothing appears | Set the pipeline id env var (or pass `inference_pipeline_id` to `@trace`/`configure`) |
| Wrapping the wrong client instance | The calls that run aren't traced | Wrap the exact client object your request path uses |
| `@trace` on a function that also uses a wrapped client, expecting one to replace the other | Double-counted or confusing spans | Wrapper traces the LLM call; `@trace` traces your function — use both intentionally, not redundantly |
| Hardcoding the API key in code | Leak / fails in CI | Use `OPENLAYER_API_KEY` env var; never paste keys into chat |
| Using sync `trace_openai` on an `AsyncOpenAI` client (or vice-versa) | Calls not traced / errors | Match async: `trace_async_openai` with `AsyncOpenAI` and `@trace_async()` |
| Adding lots of instrumentation before verifying | Hard to debug why nothing lands | Verify one trace publishes first, then enrich |
| Guessing provider wrapper names/signatures from memory | Wrong import, runtime error | Fetch the current snippet from the instrument / alternative-integrations docs |
| Assuming TS auto-publishes without the pipeline env var | Silent no-op | TS publishes only when `OPENLAYER_INFERENCE_PIPELINE_ID` is set; `OPENLAYER_DISABLE_PUBLISH=true` disables |
