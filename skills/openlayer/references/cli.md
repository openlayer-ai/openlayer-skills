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
openlayer login            # stores key in ~/.openlayer/config.json (supports multiple profiles)
openlayer whoami           # verify auth / current profile
```

Global flags: `--api-key`, `--profile-name`, `--output-mode terminal|ci`, `--debug`.

## Core commands

| Command | Use |
| --- | --- |
| `openlayer push -m "msg" -w -t` | Push a commit; `-w` wait for results, `-t` tail logs (the main dev loop) |
| `openlayer validate` | Validate `openlayer.json` + `tests.json` before pushing |
| `openlayer inspect <versionID>` | Inspect a commit's details |
| `openlayer export <pipelineId> <start> <end>` | Export monitoring data from a pipeline |
| `openlayer projects` | List/manage projects |
| `openlayer tests` / `metrics` / `batch` / `bundle` / `datasources` | Manage tests, metrics, batch runs, bundles, data sources |
| `openlayer link` | Link a Git repo to a project |
| `openlayer profile` | Manage CLI profiles |
| `openlayer update` | Update the CLI |

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Expecting a generic REST client | CLI is push/workflow only | Use MCP/SDK/REST for data (`references/data-access.md`) |
| `npx`/`pip` install | Wrong — it's a Go binary | Use the platform install script |
| `push` without `validate` | Late, cryptic failures | `openlayer validate` first |
| `push` without `-w` in CI | Job passes before results land | Use `-w` and fail on failed tests (`references/ci-cd.md`) |
| Wrong `export` arg order | Empty/incorrect export | `export <pipelineId> <start> <end>` |
| Wrong profile/workspace | Pushes to the wrong place | Check `openlayer whoami` / `--profile-name` |
