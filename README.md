# Openlayer Skills

[Agent Skills](https://github.com/anthropics/skills) that teach AI coding assistants (Claude Code, Cursor, GitHub Copilot, etc.) how to integrate apps with [Openlayer](https://openlayer.com) — the AI evaluation and observability platform.

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

### GitHub Copilot

GitHub Copilot reads the same plugin manifest as Claude Code.

In **VS Code**, add the marketplace to your `settings.json`, then install **Openlayer** from the Extensions view (search `@agentPlugins`):

```json
{
  "chat.plugins.marketplaces": ["openlayer-ai/openlayer-skills"]
}
```

In the **Copilot CLI**:

```bash
copilot plugin marketplace add openlayer-ai/openlayer-skills
copilot plugin install openlayer@openlayer
```

### Other agents

Codex, Gemini CLI, Windsurf, opencode, and dozens more install through the [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add openlayer-ai/openlayer-skills --skill "openlayer"
```

For claude.ai, Copilot's cloud coding agent and code review, a manual symlink, or anything else, see the [installation guide](https://docs.openlayer.com/openlayer-skills) — it is the source of truth and stays current as these tools change.

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
