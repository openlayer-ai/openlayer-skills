# Agent Instructions

Guidance for agents editing this repo (adding or improving skill content).

## Adding or Improving a Use Case

- **Only add a use case if it beats the docs.** If an agent can already serve the user by fetching the Openlayer docs (`docs.openlayer.com`, see `references/docs-access.md`), add nothing. Reserve new content for where docs fall short and the agent needs extra context (mode routing, the MCP-vs-SDK-vs-REST decision, non-obvious pitfalls). *Every addition is maintenance surface and dilutes the skill.*

- **You should almost never touch the top-level `description` in `SKILL.md`.** It only controls whether the skill is invoked, and a user asking about Openlayer, tracing, evals, or `openlayer.json` already triggers it. Keep it short; in-skill routing handles the rest. (It must stay under 1024 characters and contain no `<` or `>`.)

- **Put "when to use" guidance in exactly two places:** the one-line entry in the use-case router table in `SKILL.md`, and the `description` in the reference file's frontmatter. Nowhere else — no prose routing section in a reference body. *A reference body is read only after the agent already chose to open it, so routing text there is dead weight.*

- **Never commit code that can go stale.** Link to the relevant Openlayer docs page (append `.md` to any page URL) so the agent fetches current code; use short pseudo-code only for logic-specific bits. Openlayer SDKs/CLI/MCP change frequently. *Committed code goes stale and teaches agents the wrong thing.*

- **In a reference file, less is more.** Add only what's useful or what an agent couldn't infer on its own. Each reference ends with a **Common Mistakes** table — that is usually the highest-value part.

- **Be cautious with `allowed-tools`.** A tool not in the list still works — the user just grants permission the first time. Only auto-allow no-brainer, low-risk commands. *A risky auto-allow makes people hesitate to install the skill at all.*

## Plugin Version Bumps

The repo ships to two marketplaces, each with its own manifest:
- `.claude-plugin/plugin.json` (Claude Code) and `.claude-plugin/marketplace.json`
- `.cursor-plugin/plugin.json` (Cursor)

Keep the `version` fields **in lockstep** — bump them together in the same PR (semver: patch for fixes/clarifications, minor for new capability, major for breaking renames/removals).

## Validation

Run the format check before committing:

```bash
python scripts/quick_validate.py skills/openlayer
```
