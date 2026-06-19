---
name: openlayer-governance
description: Set up and track AI compliance in Openlayer governance — activate built-in frameworks (EU AI Act, ISO 42001, OSFI E-23) or build custom ones, satisfy platform vs evidence-based rules, and track project/workspace compliance. Use when the user asks about compliance, frameworks, audits, or governance.
---

# Openlayer Governance

Governance tracks AI compliance across a workspace: a **framework** is a set of **rules** scoped to
projects, each project gets a compliance checklist, and engineering work produces the evidence.

> **Mostly UI-driven.** Activating frameworks, building custom ones, and uploading evidence are done
> in the Openlayer app (Governance section) — there is no documented API/SDK/CLI for these. Your job
> as an agent is usually to (a) explain the model, (b) walk the user through the UI steps, and (c) do
> the *engineering* work that auto-satisfies platform rules (instrument monitoring, run CI/CD tests).

Docs: https://docs.openlayer.com/governance/overview.md and the per-topic pages below.

## Two kinds of rules

- **Platform rules** — satisfied automatically as a byproduct of using Openlayer: capturing production
  traces, running CI/CD tests, evaluating bias/PII/hallucination, project metadata (owner, risk,
  approval). No upload. https://docs.openlayer.com/governance/platform-rules.md
- **Evidence-based rules** — require a human to upload a document or paste a link (model card, risk
  assessment, responsible-AI policy), per project or workspace-wide, with a renewal cadence.
  https://docs.openlayer.com/governance/evidence-based-rules.md

## Workflows (UI)

- **Activate a built-in framework** and scope it to projects (by individual project, risk level,
  approval status, or task type) → each scoped project gets a checklist.
  https://docs.openlayer.com/governance/activate-framework.md
- **Build a custom framework** from the rule library (pick platform rules, add evidence-based rules
  with scope + renewal). https://docs.openlayer.com/governance/build-custom-framework.md
- **Track compliance** per project (Governance mode) and across the workspace; platform rules update
  in real time as you do the work. https://docs.openlayer.com/governance/project-compliance.md and
  /governance/workspace-compliance.md

## How an agent helps most

Frameworks are configured in the UI, but **platform rules are satisfied by code you can write**: set
up monitoring (`references/monitoring-instrumentation.md`), add CI/CD eval gates
(`references/ci-cd.md`), and create the relevant tests (`references/tests.md`, e.g. PII / bias /
hallucination). That turns "compliance" into a byproduct of the integration work.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Looking for a governance API/SDK | Not available | Frameworks/evidence are UI-only; drive the user through the app |
| Confusing the two rule types | Wrong expectation | Platform rules auto-satisfy via usage; evidence rules need uploads |
| Activating a framework but not scoping it to projects | No checklist appears | Scope it to the target projects |
| Treating platform rules as manual config | Wasted effort | They satisfy automatically — just do the monitoring/testing work |
| Uploading evidence that doesn't match the rule's intent | Rule stays effectively unmet | Match the document to the specific rule |
