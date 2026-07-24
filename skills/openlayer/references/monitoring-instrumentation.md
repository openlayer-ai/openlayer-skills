---
name: openlayer-monitoring
description: Instrument an app with Openlayer tracing for live monitoring. Use when adding observability to LLM/agent code, wrapping an LLM client, or auditing existing Openlayer instrumentation.
---

# Openlayer Monitoring — Instrumentation

Add tracing to a live app so each request becomes a trace (inputs, outputs, intermediate steps,
tokens, cost, latency) that Openlayer runs tests and alerts on.

> **Traditional / tabular ML** (scikit-learn, XGBoost — no LLM call to wrap)? `@trace` is the wrong
> tool. Publish predictions directly instead — see `references/traditional-ml.md`.

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

For frameworks without a wrapper, decorate your own functions with `@trace()`. Nesting follows the
**call stack**: a decorated function becomes a child step only when it is called from *inside* another
decorated function — calling two decorated functions side-by-side from an undecorated parent yields two
separate (sibling) root traces, not one nested trace.

```python
from openlayer.lib import trace
from openlayer.lib.tracing import log_context, log_question   # explicit logging (NOT re-exported from openlayer.lib)

@trace()                                              # child step (called inside answer → nested)
def retrieve(question: str) -> list[str]:
    return vector_search(question)

@trace()                                              # root step
def answer(question: str) -> str:
    context = retrieve(question)                      # nested child of answer
    log_question(question); log_context(context)      # populate the question/context columns
    return llm(question, context)
```

`context_kwarg`/`question_kwarg` are an alternative to `log_context`/`log_question`, but they read from
the decorated function's **own declared parameters** — `@trace(context_kwarg="context")` errors with
`Context kwarg 'context' not found in inputs` unless `context` is a parameter of that function. When the
step *computes* its context internally (as above), call `log_context()`/`log_question()` instead.

### 4. Run once, then verify a trace lands BEFORE adding more

Execute one real request, then confirm the trace appears (Data page in the app, or
`client.inference_pipelines.rows.list(...)` / MCP `list_inference_pipelines`). Do not add ten spans
before confirming the first one publishes — most failures are "configured but nothing arrives."

### 5. Enrich (only what's relevant — infer from code, ask when unclear)

| If the code has…                          | Add                          | How | Docs |
| ----------------------------------------- | ---------------------------- | --- | ---- |
| Conversation history / chat endpoints     | user/session context         | `set_user_session_context(user_id=…, session_id=…)` → lands as `openlayer_user_id` / `openlayer_session_id` | https://docs.openlayer.com/monitoring/sessions-and-users.md |
| Retrieval / RAG                           | context (+ question)         | `@trace(context_kwarg="…", question_kwarg="…")` on the **root** fn — they resolve from its **input args** (NOT `update_current_trace`) | https://docs.openlayer.com/monitoring/context.md |
| Useful request attributes                 | custom columns               | `update_current_trace(field=value)` → first-class row column; `update_current_step(metadata={…})` for step-level metadata (see the `promote` caveat below) | https://docs.openlayer.com/monitoring/metadata.md |
| Ground truth arriving later               | update rows after the fact   | read the published row's `openlayer_inference_id`, then `inference_pipelines.rows.update(inference_id="…", …)` (details + trace-time id below) | https://docs.openlayer.com/monitoring/updating-data.md |

`set_user_session_context`, `update_current_trace`, `update_current_step`, `trace`, `trace_async`,
`trace_openai` are all importable from `openlayer.lib`. **Context/question are driven by the
`context_kwarg`/`question_kwarg` decorator args (read from the root function's inputs), not by
`update_current_trace`** — setting them via `update_current_trace` won't populate the row's
`context`/`_question` columns. Custom row columns come from keyword args to
`update_current_trace(field=value)`. To later update a row (e.g. add ground truth), correlate it by its
inference id: simplest is to read the published row's server-assigned `openlayer_inference_id` and pass it
to `rows.update(inference_id="…")`. If you instead want to choose the id at trace time, only the exact
camelCase `update_current_trace(inferenceId="…")` works — snake_case `inference_id` silently becomes an
ordinary column and the row still publishes under a server id. `@trace(promote=[...])` only promotes the decorated fn's input args
(or keys of a dict return) and errors on a computed scalar, so it isn't a general custom-column mechanism.
For local dev without publishing, set `OPENLAYER_DISABLE_PUBLISH=true`.
Offline buffering is available for unreliable networks (see the tracing docs).

### 6. Point the user to next steps

Tests run on the live traces — to add quality checks, see the tests docs
(https://docs.openlayer.com/tests/overview.md) and guardrails docs
(https://docs.openlayer.com/guardrails/overview.md).

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
