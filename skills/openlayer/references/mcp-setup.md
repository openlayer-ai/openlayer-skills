---
name: openlayer-mcp-setup
description: Install and configure the Openlayer MCP server (openlayer-mcp) for Claude Code / Cursor / VSCode, and use its tools. Use when the user wants agent-native access to Openlayer projects, pipelines, test results, and the fix-loop.
---

# Openlayer MCP Server

The `openlayer-mcp` server gives agents typed tools for the Openlayer platform — the preferred
data-access tier and the engine for the fix-loop.

## Install & configure

Add to the MCP config of your client (Claude Code, Cursor, VSCode, Claude Desktop):

```json
{
  "mcpServers": {
    "openlayer": {
      "command": "uvx",
      "args": ["openlayer-mcp"],
      "env": { "OPENLAYER_API_KEY": "YOUR_OPENLAYER_API_KEY" }
    }
  }
}
```

Requires `uv`/`uvx` (or `pip install openlayer-mcp`). For self-hosted/local, also set
`OPENLAYER_BASE_URL` in `env`. Restart the client after editing the config so tools register.

> This is the **platform** MCP. There is a separate **docs** MCP at `docs.openlayer.com/mcp`
> (`search_openlayer_docs`) — see `references/docs-access.md`.

## Tool catalog

- **Discovery:** `discover_openlayer_schema` (task types, resource graph, test catalog),
  `generate_test_config` (valid test object from a catalog slug), `search_openlayer_docs`.
- **Projects / pipelines:** `list_projects`, `create_project`, `list_inference_pipelines`,
  `create_inference_pipeline`, `retrieve_inference_pipeline`.
- **Commits (development):** `list_commits`, `retrieve_commit`, `push_commit`.
- **Results:** `list_commit_test_results`, `list_inference_pipeline_test_results`,
  `wait_for_commit_results`.
- **Fix-loop:** `fetch_failed_rows_for_goal`, `propose_fix`, `apply_and_push`,
  `diagnose_monitoring_failure`, `add_rows_to_dataset` (see `references/mcp-fix-loop.md`).
- **Escape hatch:** `call_openlayer_api(method, endpoint, query_params, body)` for any REST call not
  covered by a typed tool.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| `uvx`/`uv` not installed | Server won't start | Install uv, or use `pip install openlayer-mcp` and run `uv run -m openlayer_mcp` |
| API key in `args` not `env` | Key ignored / leaks in process list | Put `OPENLAYER_API_KEY` under `env` |
| Expecting tools without restart | Tools don't appear | Restart the client after editing MCP config |
| Using `call_openlayer_api` when a typed tool exists | More error-prone | Prefer the domain tool; raw call only as fallback |
| Confusing platform MCP with docs MCP | Wrong tool/endpoint | Platform = `openlayer-mcp`; docs = `docs.openlayer.com/mcp` |
