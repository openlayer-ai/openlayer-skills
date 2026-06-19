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

Built-in classes (import from `openlayer_guardrails`): `PIIGuardrail`, `PromptInjectionGuardrail`,
`ToxicityENGuardrail`, `ToxicityPTGuardrail`. Two ways to use:

```python
from openlayer_guardrails import PIIGuardrail
from openlayer.lib import trace                 # (openlayer.lib.tracing.trace also works)

pii_guard = PIIGuardrail(redact_entities={"EMAIL_ADDRESS", "PHONE_NUMBER"})

@trace(guardrails=[pii_guard])                   # monitored on the Openlayer platform
def handle(user_input: str) -> str:
    ...
```

Standalone (no platform): construct with `block_entities` / `redact_entities` sets (+ optional
`confidence_threshold`, `block_strategy`, `block_message`) and call `check_input(...)` /
`check_output(...)`. They return a `GuardrailResult` with `action` (`GuardrailAction.MODIFY` /
`BLOCK` / pass), `modified_data` (redacted text), `reason`, and `metadata` (detected/blocked/redacted
entities). Block mode can raise `GuardrailBlockedException`.

> Install note: the `[pii]` extra pulls Presidio, and `PIIGuardrail` auto-downloads a spaCy model
> (`en_core_web_lg`) on first construction. On a clean environment you may also need `click` (a spaCy
> transitive dep). `[prompt-injection]` / `[toxicity]` pull `torch` + `transformers` (large).

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
| Missing the extra (`[pii]` / `[prompt-injection]` / `[toxicity]`) | Runtime failure | Install the extra the guardrail needs |
| `[pii]` installed but PIIGuardrail still errors ("Presidio is required") | spaCy import chain incomplete on a clean env | Ensure `click` is present; the spaCy model auto-downloads on first construction (allow network) |
| Expecting a guardrail to "just log" when it's set to block | Requests rejected unexpectedly | Pick the action (block vs redact vs log) deliberately |
| Relying on output guardrails with streaming | Unsafe tokens already sent | Don't stream when an output guardrail must hold, or guard at input |
| Using a guardrail where a monitoring test suffices | Needless latency | Reserve guardrails for prevention; observe with tests |
