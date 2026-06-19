---
name: openlayer-guardrails
description: Add Openlayer runtime guardrails (PII, prompt-injection) to an app to block, redact, or log unsafe inputs/outputs. Use when the user must PREVENT bad outputs at request time, not just observe them. Covers the openlayer-guardrails Python package and gateway-level guardrails.
---

# Openlayer Guardrails

Guardrails are **runtime** checks in the request path that can **block**, **modify (redact)**, or
**log** unsafe inputs/outputs. They complement tests (which observe after the fact) — use a guardrail
when you must actively intervene. They add latency, so they are not a replacement for tests.

Docs: https://docs.openlayer.com/guardrails/overview.md

## Option A — in your app (openlayer-guardrails package)

Separate package (NOT `openlayer.lib.guardrails`):

```bash
pip install "openlayer-guardrails[pii]"            # extras: [pii], [prompt-injection]
```

Built-in classes: `PIIGuardrail`, `PromptInjectionGuardrail` (import from `openlayer_guardrails`). Two ways to use:

```python
from openlayer_guardrails import PIIGuardrail
from openlayer.lib.tracing import trace

pii_guard = PIIGuardrail()

@trace(guardrails=[pii_guard])          # monitored on the Openlayer platform
def handle(user_input: str) -> str:
    ...
```

Standalone (no platform): instantiate with `block_entities` / `redact_entities` sets and call
`check_input(...)` / check methods yourself. Confirm the exact signatures from the docs — don't guess.

## Option B — at the Gateway (no app code)

If traffic goes through the Openlayer Gateway, enable guardrails there (PII / prompt-injection, input
/ output / both, action block or redact) with zero code changes. See `references/gateway.md` and
https://docs.openlayer.com/gateway/guardrails.md. **Caveat: output guardrails don't run on streamed
responses** — tokens reach the user before the check.

## Tests vs guardrails

- **Test** = scored evaluation over data; pass/fail, trends, alerts. Proactive coverage.
- **Guardrail** = runtime intervention that can block/redact. Reactive protection. Adds latency.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| `pip install openlayer` / importing `openlayer.lib.guardrails` | Wrong package | Install `openlayer-guardrails` with the right extra; import from `openlayer_guardrails` |
| Missing the extra (`[pii]` / `[prompt-injection]`) | Runtime failure | Install the extra the guardrail needs |
| Expecting a guardrail to "just log" when it's set to block | Requests rejected unexpectedly | Pick the action (block vs redact vs log) deliberately |
| Relying on output guardrails with streaming | Unsafe tokens already sent | Don't stream when an output guardrail must hold, or guard at input |
| Using a guardrail where a monitoring test suffices | Needless latency | Reserve guardrails for prevention; observe with tests |
