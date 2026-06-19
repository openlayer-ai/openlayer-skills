---
name: openlayer-gateway
description: Route an app's LLM calls through the Openlayer Gateway for spend limits, gateway-issued API keys, runtime guardrails, model routing, and zero-instrumentation observability. Use when the user wants a proxy/gateway in front of providers without instrumenting app code.
---

# Openlayer Gateway

The Gateway is a proxy between your app and LLM providers. Point your client at it and you get spend
caps, gateway-issued keys, guardrails, provider routing, and auto-tracing — **with no app
instrumentation**. This is an alternative integration path to the SDK tracing in
`references/monitoring-instrumentation.md`.

Docs: https://docs.openlayer.com/gateway/overview.md (+ per-topic pages below). Confirm current code from the docs.

## Integrate an app (the only app-side change)

Override the base URL and use a **gateway key** (`sk-olga-…`), not a provider key:

```python
from openai import OpenAI
client = OpenAI(base_url="https://your-gateway.example.com/v1", api_key="sk-olga-...")
resp = client.responses.create(model="gpt-4o-mini", input="Hello!")
```

- **Endpoint is the Responses API (`/v1/responses`)**, not `/v1/chat/completions`. Don't assume the chat-completions path.
- Auth header: `Authorization: Bearer sk-olga-…` (or `X-Api-Key`). Never put the *admin* key in app code.
- First request: https://docs.openlayer.com/gateway/make-your-first-request.md

## Configure the gateway (admin, mostly UI)

- **Connect providers** (name, base URL, format `openai`/`anthropic`/`azure_openai`, and the env var holding the provider key): https://docs.openlayer.com/gateway/connect-providers.md
- **Issue/revoke API keys** (`sk-olga-…`), per app/teammate: https://docs.openlayer.com/gateway/api-keys.md
- **Budgets & limits** (cost/requests/tokens, per key or team, daily/weekly/monthly) — UI; hitting a cap returns `429` and the request is not forwarded: https://docs.openlayer.com/gateway/budgets-and-limits.md
- **Guardrails** (PII / prompt-injection; input/output/both; block or redact): https://docs.openlayer.com/gateway/guardrails.md — see `references/guardrails.md`. Output guardrails skip streamed responses.
- **Observability**: set an Openlayer API key + inference pipeline id in the gateway config and every request is published as a trace — no SDK in the app: https://docs.openlayer.com/gateway/observability.md
- **Model routing / use any model**: route OpenAI-format requests to Anthropic (and back) with auto-translation; images/docs/web-search aren't translated (`501`): https://docs.openlayer.com/gateway/route-requests.md , /gateway/use-any-model.md

## Gateway vs SDK tracing

Both publish traces to an inference pipeline. Gateway = zero app code, also gives spend/keys/routing;
SDK tracing = finer-grained custom spans via `@trace`. Don't run both for the same calls (duplicates).

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Calling `/v1/chat/completions` | Gateway uses the Responses API | Use `/v1/responses` (or the client's `.responses.create`) |
| Using a provider key in the app | Bypasses the gateway | Use the gateway `sk-olga-…` key |
| Putting the admin key in app code | Security risk | Admin key is for the portal only; ship issued API keys |
| Adding SDK tracing on top of the gateway | Duplicate traces | Pick one path per call |
| Expecting output guardrails to catch streamed tokens | They don't run on streams | Guard at input, or disable streaming where it matters |
| Assuming providers auto-connect | No upstream configured | Add providers in gateway config first |
