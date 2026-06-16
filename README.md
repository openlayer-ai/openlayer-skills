# Openlayer Skills

[Agent Skills](https://github.com/anthropics/skills) that teach AI coding assistants (Claude Code, Cursor, etc.) how to integrate apps with [Openlayer](https://openlayer.com) — the AI evaluation and observability platform — correctly and fast.

Coding agents produce significantly better results with the skill installed, because they are conditioned to follow Openlayer's current best practices instead of guessing from memory (outdated SDK calls, wrong env vars, invented test configs).

## Skills

| Skill                         | Description                                                                                                                              |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| [openlayer](./skills/openlayer) | Main skill. Instrument code with tracing (monitoring), set up offline `openlayer.json` + `tests.json` evals (development), create tests/guardrails, gate CI/CD, run the MCP fix-loop, and access data and docs. |

## Installation

### Claude Code plugin

```bash
claude plugin marketplace add openlayer-ai/openlayer-skills
claude plugin install openlayer@openlayer
```

### Cursor plugin

```
/add-plugin openlayer
```

### skills CLI

```bash
npx skills add openlayer-ai/openlayer-skills --skill "openlayer"
```

### Manual symlink

```bash
git clone https://github.com/openlayer-ai/openlayer-skills.git /path/to/openlayer-skills
ln -s /path/to/openlayer-skills/skills/openlayer /path/to/skills-directory/openlayer
```

## Prerequisites

An [Openlayer account](https://app.openlayer.com) and an API key:

```bash
export OPENLAYER_API_KEY=...
# self-hosted / local only:
export OPENLAYER_BASE_URL=https://api.openlayer.com/v1
```

Find your API key in the Openlayer app under **Workspace settings → API keys** (see https://docs.openlayer.com/workspace-and-projects/find-your-api-key).

## Usage

Once installed, the agent uses the skill automatically when relevant — for example:

- Adding Openlayer tracing/monitoring to an LLM or agent app
- Setting up offline evals (`openlayer.json` + `tests.json`) and pushing commits
- Creating tests from the catalog and configuring guardrails
- Gating CI/CD on eval results
- Debugging failing tests via the Openlayer MCP fix-loop
- Querying projects, pipelines, test results, or looking up Openlayer docs

## Feedback & Requests

Something not working as expected, or want a new use case covered? Open an issue at https://github.com/openlayer-ai/openlayer-skills/issues or email support@openlayer.com.
