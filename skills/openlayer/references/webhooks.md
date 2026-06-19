---
name: openlayer-webhooks
description: Subscribe to Openlayer events (test created/updated/deleted, test-suite results) via signed webhooks, and verify signatures. Use when wiring Openlayer into external systems — alerting, CI/CD triggers, or syncing on test results instead of polling.
---

# Openlayer Webhooks

Openlayer sends a signed HTTPS POST to your endpoint when a subscribed event occurs — use it to alert,
trigger CI/CD, or sync, without polling.

Docs: https://docs.openlayer.com/security/webhooks/overview.md , /manage-webhooks.md , /events.md , /verify-signatures.md

## Create / manage

Webhooks are gated by a feature flag — the deployment must have `ENABLE_WEBHOOKS` enabled. All endpoints
require **workspace-admin** auth.

- **UI:** Workspace settings → Webhooks → endpoint URL + event types. The **signing secret is shown
  once** — store it immediately (it can't be retrieved later).
- **REST** (workspace-admin **session/cookie** auth — not an API key): `POST /v1/workspaces/{workspaceId}/webhooks`
  with `url` + `eventTypes[]`; `GET`/`PUT`/`DELETE` to list/update/remove; `GET …/webhooks/{id}/deliveries`
  for the delivery log (90-day retention).

## Event types

`test.created`, `test.updated`, `test.deleted`, and `tests.result.updated` (a test suite finished —
includes total/passing/failing/skipped/running counts, projectId, inferencePipelineId). Envelope:
`{ "type": ..., "timestamp": ..., "data": {...} }`.

## Verify the signature (always)

HMAC-SHA256. Headers: `webhook-id`, `webhook-timestamp`, `webhook-signature` (space-delimited,
versioned). Signed content is `{webhook-id}.{webhook-timestamp}.{raw-body}`. The secret is `whsec_`-
prefixed **base64** — decode it before HMAC. Compare in constant time.

```python
import base64, hashlib, hmac

def verify(raw_body: bytes, headers: dict, secret: str) -> bool:
    signed = f'{headers["webhook-id"]}.{headers["webhook-timestamp"]}.{raw_body.decode()}'
    key = base64.b64decode(secret.removeprefix("whsec_"))
    expected = base64.b64encode(hmac.new(key, signed.encode(), hashlib.sha256).digest()).decode()
    return any(
        p.split(",", 1)[0] == "v1" and hmac.compare_digest(p.split(",", 1)[1], expected)
        for p in headers["webhook-signature"].split(" ")
    )
```

Deliveries expect a 2xx within ~10s; failures retry up to 3× with backoff. Dedupe on `webhook-id`
(constant across retries). Verify the doc page for current details before shipping.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Not saving the signing secret at creation | Can't verify; can't retrieve it later | Store it the moment it's shown |
| HMAC over the secret as-is | Verification always fails | Base64-decode after stripping `whsec_` |
| Signing only the body | Signature mismatch | Sign `{id}.{timestamp}.{body}` |
| `==` string compare on signatures | Timing-attack risk | Use `hmac.compare_digest` |
| Ignoring retries | Duplicate processing | Dedupe on `webhook-id` |
| Slow/non-2xx endpoint | Marked failed, retried | Respond 2xx fast; do work async |
