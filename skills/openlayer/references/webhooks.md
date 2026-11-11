---
name: openlayer-webhooks
description: Subscribe to Openlayer events (test created/updated/deleted, test-suite results, project and governance changes) via signed webhooks, and verify signatures. Use when wiring Openlayer into external systems — alerting, CI/CD triggers, or syncing test results and project/governance state instead of polling.
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

`test.created`, `test.updated`, `test.deleted`, and `tests.result.updated` (a test suite finished).
Envelope: `{ "type": ..., "timestamp": ..., "data": {...} }`. For `tests.result.updated`, the counts and
ids are nested under **`data.tests`**: `{ total, passing, failing, skipped, running, projectId,
projectVersionId, inferencePipelineId }` (verified).

`project.*` uses the same create/update `eventTypes[]`. UI groups **Projects** — `project.created`,
`project.updated`, `project.deleted`, `project.restored` — and **Governance** — `project.intake.updated`,
`project.risk.assessed`, `project.risk_exception.updated`, `project.lifecycle.changed`,
`project.lifecycle.approved`.

Every `project.*` `data` is `{ project, actorId, ...event-specific details }`. `project` is the full
current snapshot: `id`, `workspaceId`, `name`, `description`, `taskType`, `creatorId`, `ownerId`, `tags`
(sorted names), `lifecycleStage` (`{id, name}` or null), `retired` (bool), `risk` (`{level, totalScore,
maxScore, scores: [{dimensionId, label, score}]}`), `intake` (`[{fieldId, label, type, value}]`),
`dateCreated`, `dateUpdated`, `dateRetired`, `dateDeleted`, `links.app`. Upsert by `data.project.id`
from any single delivery, in any order. Each delivery already has the whole record — do not replay
history or call the API.

Event-specific details:

- `project.updated` — `changes: {field: {from, to}}`, only fields that changed (`dateUpdated` ignored).
  Not sent when nothing changed. Fires on name, description, owner, and tags changes.
- `project.lifecycle.changed` — `lifecycle: {kind, fromStage: {id, name}, toStage: {id, name}, reason}`.
  `kind` is `advance`, `revert`, `retire`, or `reopen`. Retire has `toStage.id: null`; reopen has
  `fromStage.id: null` (both read as stage name "Retired"). Also fires when a workspace
  lifecycle-definition edit moves the project.
- `project.lifecycle.approved` — `approval: {stage: {id, name}, note}`. On a final approval this is
  enqueued before the resulting `project.lifecycle.changed`.
- `project.created` fires for projects created in the app or by any integration. Rolled-back creations
  send nothing.

Sample projects never emit `project.*`. A workspace template edit (intake form, risk template, or
lifecycle definition) emits no event of its own. Auth, signing, and HTTPS rules are unchanged.

> The endpoint **URL must be HTTPS for delivery.** A plain `http://` URL is *accepted at subscription
> creation* but the delivery worker refuses it ("Refusing to deliver to non-HTTPS URL"), so deliveries
> fail. Register an HTTPS endpoint.

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
| Treating `project.updated` as a full sync, or expecting it on every save | No-op saves send nothing; `changes` lists only fields that changed | Upsert `data.project` from any `project.*` delivery |
| Building state by replaying events in order | Each delivery is a full snapshot; order does not matter | Upsert by `data.project.id`; do not replay history or call the API |
| Expecting `project.*` for sample projects or template edits | Samples never emit; intake, risk, and lifecycle template edits emit nothing | Sync real projects only. A project moved by a lifecycle-definition edit still gets `project.lifecycle.changed` |
| Assuming `toStage.id` is always set | Retire sets `toStage.id` to null; reopen sets `fromStage.id` to null (name "Retired") | Treat a null stage id as Retired |
