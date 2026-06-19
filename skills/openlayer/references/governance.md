---
name: openlayer-governance
description: Set up and track AI compliance in Openlayer governance — activate built-in frameworks (EU AI Act, ISO 42001, OSFI E-23) or build custom ones, manage platform vs evidence-based rules, scope to projects, and read compliance via the REST API or the UI. Use when the user asks about compliance, frameworks, audits, rules, or governance.
---

# Openlayer Governance

Governance tracks AI compliance across a workspace: a **framework** is a set of **rules** scoped to
projects, each scoped project gets a compliance checklist, and engineering work produces the evidence.
It is driveable **both via the UI and a full REST API**.

Docs (concepts): https://docs.openlayer.com/governance/overview.md and the per-topic pages
(`activate-framework`, `build-custom-framework`, `platform-rules`, `evidence-based-rules`,
`project-compliance`). Confirm request/response schemas from the API reference / OpenAPI.

## Two kinds of rules

- **Platform rules** — satisfied **automatically** as a byproduct of using Openlayer: capturing
  production traces, running CI/CD tests, evaluating bias/PII/hallucination, project metadata (owner,
  risk, approval). No upload. https://docs.openlayer.com/governance/platform-rules.md
- **Evidence-based rules** — a human uploads a document or link (model card, risk assessment, policy),
  per project or workspace-wide, with a renewal cadence. https://docs.openlayer.com/governance/evidence-based-rules.md

## REST API (frameworks, rules, compliance, evidence)

All endpoints take bearer `OPENLAYER_API_KEY` (workspace-scoped). Confirm payloads from the OpenAPI spec.

- **Frameworks:** `GET|POST /workspaces/{workspaceId}/frameworks` · `GET|PUT|DELETE /frameworks/{id}`
  (built-in frameworks can't be deleted) · `GET /frameworks/{id}/projects` ·
  `GET /frameworks/{id}/project-rule-stats` (per-project compliance stats).
- **Scope / activate:** `PUT /frameworks/{id}` with `enabled` + a `projectSelector` (by project,
  risk level, approval status, or task type).
- **Rules:** `GET|POST /workspaces/{workspaceId}/rules` · `POST /workspaces/{workspaceId}/rules/batch`
  (up to 50) · `GET|PUT|DELETE /rules/{id}` (built-in rules can't be deleted).
- **Compliance status:** `GET /workspaces/{workspaceId}/rule-results` · `GET|PUT /rule-results/{id}`
  (acknowledge / resolve).
- **Evidence:** `GET|POST /rule-results/{id}/evidence` (upload a file/link/attestation to satisfy a rule).

Typical flow: create/activate a framework → scope it to projects → rules generate `rule-results` per
project → satisfy platform rules by doing the work, upload evidence for evidence-based rules → read
`rule-results` / `project-rule-stats` for status.

## How an agent helps most

Platform rules are satisfied **by code you can write**: set up monitoring
(`references/monitoring-instrumentation.md`), add CI/CD eval gates (`references/ci-cd.md`), and create
the relevant tests (`references/tests.md`, e.g. PII / bias / hallucination). That turns compliance into
a byproduct of the integration work — then read `rule-results` to confirm it flipped to satisfied.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Assuming governance is UI-only | Misses automation | There is a full REST API (frameworks/rules/rule-results/evidence) |
| Activating a framework but not scoping it to projects | No checklist appears | Set `enabled` + a `projectSelector` on the framework |
| Confusing the two rule types | Wrong expectation | Platform rules auto-satisfy via usage; evidence rules need uploads |
| Trying to `DELETE` a built-in framework/rule | Rejected | Only custom frameworks/rules are deletable |
| Treating platform rules as manual config | Wasted effort | Do the monitoring/testing work; the rule-result flips automatically |
| Uploading evidence that doesn't match the rule's intent | Rule stays effectively unmet | Match the document to the specific rule |
