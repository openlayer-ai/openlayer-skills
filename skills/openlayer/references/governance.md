---
name: openlayer-governance
description: Set up and track AI compliance in Openlayer governance — activate built-in frameworks (EU AI Act, ISO 42001, OSFI E-23) or build custom ones, manage platform vs evidence-based rules, scope to projects, and read compliance via the REST API or the UI. Use when the user asks about compliance, frameworks, audits, rules, or governance.
---

# Openlayer Governance

Governance tracks AI compliance across a workspace: a **framework** is a set of **rules** scoped to
projects, each scoped project gets a compliance checklist, and engineering work produces the evidence.
It is driveable **both via the UI and a full REST API**.

Docs (concepts): https://docs.openlayer.com/governance/overview.md and the per-topic pages
(`activate-framework`, `api-access`, `build-custom-framework`, `platform-rules`, `evidence-based-rules`,
`project-compliance`). Confirm request/response schemas from the API reference / OpenAPI.

## Two kinds of rules

- **Platform rules** — satisfied **automatically** as a byproduct of using Openlayer: capturing
  production traces, running CI/CD tests, evaluating bias/PII/hallucination, project metadata (owner,
  risk, approval). No upload. https://docs.openlayer.com/governance/platform-rules.md
- **Evidence-based rules** — a human uploads a document or link (model card, risk assessment, policy),
  per project or workspace-wide, with a renewal cadence. https://docs.openlayer.com/governance/evidence-based-rules.md

## REST API (frameworks, rules, compliance, evidence)

All endpoints take bearer `OPENLAYER_API_KEY` (workspace-scoped). Most are keyed by **`workspaceId`** —
get yours from `GET /projects` (each project carries a `workspaceId` field) or the workspace settings
page in the app. Governance endpoints are **not** in the public OpenAPI spec; the shapes below are
authoritative — cross-check the governance docs pages, not the spec.

- **Frameworks:** `GET|POST /workspaces/{workspaceId}/frameworks` (create needs only `name`) ·
  `GET|PUT|DELETE /frameworks/{id}` (only custom frameworks delete; built-ins are `immutable` with a
  non-null `builtInSlug`) · `GET /frameworks/{id}/projects` · `GET /frameworks/{id}/project-rule-stats`.
- **Scope / activate:** `PUT /frameworks/{id}` with `enabled` + a `projectSelector`. Picks,
  future-project criteria, and the selector round-trip:
  https://docs.openlayer.com/governance/api-access.md (UI:
  https://docs.openlayer.com/governance/activate-framework.md). `match` criteria are ANDed. With no
  `includeProjectIds`, an empty or null `match` applies to every project. `property` is `name`,
  `ownerId`, `taskType`, `riskLevel`, `riskTotalScore`, or `tagIds` (project tag UUIDs from
  `GET /workspaces/{workspaceId}/project-tags`; `operator` `in` = any, `notIn` = none;
  `equals`/`notEquals` fold into those; other operators and non-UUID values are rejected).
  `modelTypes` is not in the enum (legacy writes are auto-converted to `tagIds`). `id` and
  `approvalStatus` are not `match` properties.
- **Rules:** `GET|POST /workspaces/{workspaceId}/rules` (create requires `name`, `scope`
  [`workspace`|`project`], `type` [`evidence`|`platform`]) · `POST /workspaces/{workspaceId}/rules/batch`
  (body is a **bare JSON array**, not `{items:[...]}`) · `GET|PUT|DELETE /rules/{id}`. A `platform` rule
  also needs an **`automationType`** so the evaluator can auto-check it (without one the rule-result is
  `status: error` "Unknown automation type"); values: `development_mode_enabled`,
  `development_traces_enabled`, `development_notifications_enabled`, `monitoring_mode_enabled`,
  `monitoring_traces_enabled`, `monitoring_sessions_enabled`, `monitoring_users_enabled`,
  `monitoring_notifications_enabled`, `test_setup`, `project_risk_level_set`, `project_description_set`,
  `project_owner_set`.
- **Auto-create `test_setup` tests:** `autoCreateTests` and `autoCreateTestRuleIds` on
  `PUT /frameworks/{id}`, and the UI review:
  https://docs.openlayer.com/governance/api-access.md and
  https://docs.openlayer.com/governance/activate-framework.md. Nothing is created from framework POST,
  on a disabled framework, or in the PUT response. The job runs after a PUT that leaves an **enabled**
  framework with the switch on, including when the rule subset or `enabled` changes. A PUT that omits
  `autoCreateTests` keeps the stored value.
  `GET /frameworks/{id}/auto-creatable-tests?taskType=…` returns `autoCreatable`, `creatableTaskTypes`,
  `blocker` (`requires_column`, `requires_parameters`, `requires_reference_dataset`,
  `unsupported_subtype`, `no_default_threshold`), and `usesLlmJudge` per rule.
- **Attach rules to a framework:** rules are created standalone on the workspace, then linked via
  `PATCH /frameworks/{id}/rules` with `{"ops": [{"op": "attach", "ruleId": "<id>"}]}` (`"op": "detach"`
  to remove). Passing `frameworkId` in the rule-create body is **silently ignored** — you must PATCH.
  Built-in frameworks can't detach rules.
- **Compliance status:** `GET /workspaces/{workspaceId}/rule-results` (filter to one framework with
  `?frameworkId=<id>`; results are per scoped project) · `GET|PUT /rule-results/{id}`.
- **Evidence:** `GET|POST /rule-results/{id}/evidence` — the required field depends on the rule's
  `evidenceType`: document → `storageUri`, url → `url`, text → `text`. Send **only** that one field (e.g.
  `{"storageUri": "..."}`) — an extra field like `fileName` gets 400 "Unknown field." Posting valid
  evidence flips the rule-result from `pending` to `passing`. For a **document**, get the `storageUri` by
  uploading the file first via the storage presigned-URL flow (`client.storage.presigned_url` /
  `POST /storage/presigned-url?objectName=<name>`, which returns both a `storageUri` and a one-time upload
  `url`), then upload to that `url` as **multipart/form-data** (`curl -F "file=@..."`) — it rejects `PUT`
  (405) and a raw POST body (415) — and post the returned `storageUri` — see `references/data-access.md`.

Bearer `OPENLAYER_API_KEY` is sufficient for all of the above (no cookie/admin auth needed).

Typical flow: create/activate a framework → scope it to projects → rules generate `rule-results` per
project → satisfy platform rules by doing the work, upload evidence for evidence-based rules → read
`rule-results` / `project-rule-stats` for status.

## How an agent helps most

Platform rules are satisfied **by code you can write**: set up monitoring
(`references/monitoring-instrumentation.md`), add CI/CD eval gates (`references/ci-cd.md`), and create
the relevant tests (`references/tests.md`, e.g. PII / bias / hallucination). That turns compliance into
a byproduct of the integration work — then read `rule-results` to confirm it flipped to satisfied.
For a `test_setup` rule, flip `autoCreateTests` instead of hand-building tests. Check
`GET /frameworks/{id}/auto-creatable-tests` and create only rules that return a `blocker`
(`references/tests.md`).

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Assuming governance is UI-only | Misses automation | There is a full REST API (frameworks/rules/rule-results/evidence) |
| Activating a framework but not scoping it to projects | No checklist appears | Set `enabled` + a `projectSelector` on the framework |
| `match` on `id` or `approvalStatus` | Not `match` properties — matches nothing | Pin with `includeProjectIds` (governance API page). Criteria: `name`, `ownerId`, `taskType`, `riskLevel`, `riskTotalScore`, `tagIds` |
| Scoping by tag name or `modelTypes` | `modelTypes` is not in the enum (legacy writes auto-convert to `tagIds`); non-UUID values are rejected | `tagIds` of project tag UUIDs from `GET /workspaces/{workspaceId}/project-tags`, `operator` `in` (any) or `notIn` (none) |
| Read-modify-write of `projectSelector` | Silently unpins projects that joined through `match` | Omit `projectSelector` to keep the current scope (https://docs.openlayer.com/governance/api-access.md) |
| `/rules/batch` body as `{items:[...]}` | 400 "is not of type array" | Send a bare JSON array of rule objects |
| Setting `frameworkId` in the rule-create body to link it | Silently ignored — rule stays unattached | Create the rule, then `PATCH /frameworks/{id}/rules` with `{"ops":[{"op":"attach","ruleId":...}]}` |
| Creating a `platform` rule with no `automationType` | rule-result errors "Unknown automation type" | Set a valid `automationType` (e.g. `monitoring_traces_enabled`) so it can auto-evaluate |
| Expecting auto-created tests from framework POST, a disabled framework, or the PUT response | Nothing is created then | The job runs after a PUT that leaves an **enabled** framework with `autoCreateTests` on. A create POST has no rules yet, so a subset's `autoCreateTestRuleIds` goes on a later PUT. Hand-build only rules whose `blocker` is set (`requires_column`, `requires_parameters`, `requires_reference_dataset`, `unsupported_subtype`, `no_default_threshold`) |
| Rule create with only `name` | 400 (scope/type required) | Include `scope` and `type` |
| Evidence POST with the wrong field, or an extra field (e.g. `fileName`) | 400 (field required / "Unknown field") | Send exactly one field matching `evidenceType`: `storageUri`/`url`/`text`, nothing else |
| Uploading to the presigned URL with `PUT` or a raw body | 405 / 415 | POST as `multipart/form-data` (`curl -F "file=@..."`) |
| Confusing the two rule types | Wrong expectation | Platform rules auto-satisfy via usage; evidence rules need uploads |
| Trying to `DELETE` a built-in framework/rule | Rejected | Only custom frameworks/rules are deletable |
| Treating platform rules as manual config | Wasted effort | Do the monitoring/testing work; the rule-result flips automatically |
| Uploading evidence that doesn't match the rule's intent | Rule stays effectively unmet | Match the document to the specific rule |
