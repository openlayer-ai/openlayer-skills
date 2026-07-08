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
pip install "openlayer-guardrails[pii]"            # extras: [pii], [prompt-injection], [toxicity]
```

Built-in classes (import from `openlayer_guardrails`): `PIIGuardrail` (entity-based: `block_entities` /
`redact_entities`), and the threshold-based `PromptInjectionGuardrail`, `ToxicityENGuardrail`,
`ToxicityPTGuardrail` (`confidence_threshold` / `threshold`, no entity sets) which need
`[prompt-injection]` / `[toxicity]` (torch + transformers — large; they raise a clear `ImportError`
naming the extra if missing). Two ways to use:

```python
from openlayer_guardrails import PIIGuardrail
from openlayer.lib import trace                 # (openlayer.lib.tracing.trace also works)

pii_guard = PIIGuardrail(redact_entities={"EMAIL_ADDRESS", "PHONE_NUMBER"})

@trace(guardrails=[pii_guard])                   # monitored on the Openlayer platform
def handle(user_input: str) -> str:
    ...
```

Standalone (no platform): call `check_input(inputs)` / `check_output(output, inputs)` — both take a
**dict** of inputs (not a bare string; `check_output` needs both args). They **return a `GuardrailResult`
and never raise or substitute on their own** — `block_strategy` is acted on only by the `@trace` wrapper.
In standalone you enforce the verdict yourself:

```python
from openlayer_guardrails import (
    PIIGuardrail, BlockStrategy, GuardrailAction, GuardrailBlockedException,
)

# Hard block: check_input returns BLOCK but does NOT raise — you raise it.
block_guard = PIIGuardrail(block_entities={"EMAIL_ADDRESS"},          # reliably-detected entity
                           block_strategy=BlockStrategy.RAISE_EXCEPTION)
res = block_guard.check_input({"user_message": text})
if res.action == GuardrailAction.BLOCK:
    raise GuardrailBlockedException(guardrail_name=block_guard.name,
                                    reason=res.reason, metadata=res.metadata)

# Redact: substitute the cleaned text yourself from modified_data.
redact_guard = PIIGuardrail(redact_entities={"EMAIL_ADDRESS"})
out = redact_guard.check_output(model_output, {"user_message": text})
safe = out.modified_data if out.action == GuardrailAction.MODIFY else model_output
```

`GuardrailResult` fields: `action` (`MODIFY`/`BLOCK`/`ALLOW`), `modified_data` (redacted text, `None` when
blocked), `reason`, `metadata` (detected/blocked/redacted entities), `block_strategy`, `error_message`.

**Block does NOT raise by default.** Behavior is set by `block_strategy` (4 options): the default
`RETURN_ERROR_MESSAGE` substitutes inputs/output with `block_message` and lets the function run;
`RAISE_EXCEPTION` raises `GuardrailBlockedException`; `RETURN_EMPTY` / `SKIP_FUNCTION` blank or skip. So
to actually stop a request in a `@trace` path, construct the guard with
`block_strategy=BlockStrategy.RAISE_EXCEPTION`.

On a guarded trace, the published row carries `has_guardrails: true`, top-level
`guardrail_allowed`/`blocked`/`modified` flags, and a root-step `metadata.guardrails` map keyed
`input_<name>` / `output_<name>` with each check's action + reason + entity metadata.

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
| Expecting a block guardrail to raise/stop by default | Default `block_strategy` substitutes inputs and the function still runs | Set `block_strategy=BlockStrategy.RAISE_EXCEPTION` (effective in the `@trace` path; in standalone, act on `result.action` yourself) |
| Assuming every PII entity is detected | Presidio recognizers are confidence-based; some entities/formats (e.g. `US_SSN`, bare local phone numbers) fall below the threshold and pass through | Verify detection for your entity set; lean on well-supported entities (`EMAIL_ADDRESS`, `CREDIT_CARD`, `IP_ADDRESS`) |
| Calling `check_input("text")` / `check_output("text")` | They take an inputs **dict** (output check needs both args) | `check_input({...})` / `check_output(output, {...})` |
| Relying on output guardrails with streaming | Unsafe tokens already sent | Don't stream when an output guardrail must hold, or guard at input |
| Using a guardrail where a monitoring test suffices | Needless latency | Reserve guardrails for prevention; observe with tests |
