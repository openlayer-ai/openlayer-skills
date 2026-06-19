---
name: openlayer-docs-access
description: Look up Openlayer documentation reliably — the llms.txt index, fetching pages as markdown, and docs search. Use whenever you need current Openlayer API/SDK/CLI/test details instead of relying on memory.
---

# Openlayer Documentation Access

Openlayer docs change frequently. Resolve the current answer from docs before writing code.

## Methods (preference order)

1. **Search** (when you don't know the exact page): the `search_openlayer_docs` MCP tool, or the
   hosted docs MCP at `https://docs.openlayer.com/mcp`. Best for fuzzy topics and debugging.
2. **Index** — fetch `https://docs.openlayer.com/llms.txt`. Every page is listed as
   `[title](https://docs.openlayer.com/<path>.md): description`. Scan for the right page.
3. **Fetch a page as markdown** — append `.md` to any docs URL and fetch it
   (e.g. `https://docs.openlayer.com/monitoring/instrument.md`). Use your native fetch tool (`WebFetch`)
   when available; `curl` works too.

## Useful entry points

- Monitoring/tracing: `monitoring/instrument`, `monitoring/alternative-integrations`
- Development/offline: `development/overview`, `development/openlayer-json`, `development/tests-json`, `guides/cli-push`
- Tests: `tests/overview`, `tests/catalog/<test>`
- Guardrails: `guardrails/overview`
- CLI commands: `api-reference/cli/commands/<cmd>`
- REST API + SDKs (Go/Java/Python/Ruby/TypeScript): see their sections in `llms.txt`

## When you cite docs to the user

Link the page (without `.md`, so it opens in a browser) and quote only the relevant snippet. If a doc
contradicts this skill, trust the doc.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Implementing from memory | Outdated/wrong API | Fetch the page first |
| Fetching the HTML page | Noisy, hard to parse | Append `.md` for clean markdown |
| Not checking `llms.txt` | Miss the right page | Start from the index when unsure |
| Relying on a stale cached page | Wrong details | Re-fetch if results look off (pages can change) |
