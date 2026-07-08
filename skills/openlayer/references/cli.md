---
name: openlayer-cli
description: Install and use the Openlayer CLI — the development/push workflow tool (push, validate, login, inspect, export, projects). Use for pushing commits and managing the offline workflow. NOT a generic REST client; for data access use MCP/SDK.
---

# Openlayer CLI

The Openlayer CLI is a binary for the **development/push workflow**. It is *not* a generic REST client
— to read/modify data programmatically, use `references/data-access.md`.

Docs: https://docs.openlayer.com/guides/cli-push.md and the command pages under
`https://docs.openlayer.com/api-reference/cli/commands/<cmd>.md` (discover via `llms.txt`).

## Install

Use the platform install script (NOT npx — it's a Go binary):

```bash
curl -o- "https://downloads.openlayer.com/cli/install/osx_arm64.sh" | sh   # macOS Apple Silicon
# osx_64.sh (Intel mac), linux_arm64.sh / linux_64.sh (Linux) variants also exist
```

Confirm the current install command/URL from the docs if it fails.

## Auth & profiles

```bash
openlayer login            # INTERACTIVE (browser/TTY) — stores key in ~/.openlayer/config.toml
openlayer whoami           # verify auth / current profile
```

Global flags: `--api-key`, `--profile-name`, `--output-mode terminal|ci`, `--debug`.

### Non-interactive auth (agents & CI) — prefer this

`openlayer login` and `openlayer link` are **interactive (TTY-only)** and will hang an agent or CI job.
You do NOT need them: the CLI reads everything from env vars, so push works headless.

```bash
export OPENLAYER_API_KEY=...
export OPENLAYER_PROJECT_ID=...     # the target project's id — replaces `openlayer link`
export OPENLAYER_BASE_URL=...       # self-hosted/local only
openlayer push -m "msg"             # no login, no link needed; waits for results by default
```

If you ever see `Error: project id not found. Run 'openlayer link'`, do **not** run `link` — set
`OPENLAYER_PROJECT_ID` instead. (`OPENLAYER_WORKSPACE_ID` is also read from env if needed; the
workspace is otherwise derived from the API key.)

## Core commands

| Command | Use |
| --- | --- |
| `openlayer push -m "msg"` | Push a commit and wait for results (`--wait` defaults to true; `-w=false` to skip, `-t` to tail logs) |
| `openlayer validate` | Validate `openlayer.json` + `tests.json` before pushing |
| `openlayer inspect <versionID>` | Inspect a commit's details |
| `openlayer export <pipelineId> <start> <end>` | Export monitoring data from a pipeline |
| `openlayer projects` | Manage projects (`projects create`) |
| `openlayer tests` / `metrics` / `batch` / `data-sources` | Export tests, manage metrics, batch runs, data sources |
| `openlayer link` | Link a directory to a project (INTERACTIVE — for automation set `OPENLAYER_PROJECT_ID` instead) |
| `openlayer profile` | Manage CLI profiles |
| `openlayer update` | Update the CLI |

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Running `openlayer login`/`link` in an agent or CI job | They are TTY-only and hang (even emit a cursor-position query) | Set `OPENLAYER_API_KEY` + `OPENLAYER_PROJECT_ID` (+ `OPENLAYER_BASE_URL`) and push headless |
| Following the `project id not found. Run 'openlayer link'` hint into interactive `link` | Hangs without a TTY | Set `OPENLAYER_PROJECT_ID` instead |
| Expecting a generic REST client | CLI is push/workflow only | Use MCP/SDK/REST for data (`references/data-access.md`) |
| `npx`/`pip` install | Wrong — it's a Go binary | Use the platform install script |
| `push` without `validate` | Late, cryptic failures | `openlayer validate` first |
| Passing `--wait=false` in CI | Job passes before results land | Keep the default (`--wait` is true) and fail on failed tests (`references/ci-cd.md`) |
| Wrong `export` arg order | Empty/incorrect export | `export <pipelineId> <start> <end>` |
| Wrong profile/workspace | Pushes to the wrong place | Check `openlayer whoami` / `--profile-name` |
