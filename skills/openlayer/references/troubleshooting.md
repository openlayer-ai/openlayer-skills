---
name: openlayer-troubleshooting
description: Diagnose a broken Openlayer setup — traces not appearing, push/bundle failures, auth and base-URL problems, validation errors. Use when something that should be working isn't, or when asked to debug an existing integration rather than build one.
---

# Openlayer — Troubleshooting

Use this when Openlayer is already set up and something isn't working. `openlayer init` routes its
"something went wrong" escape hatch here, so the report you're handed is often a user's paste of an
error with little else.

**Diagnose before you change anything.** The most common wrong turn is rewriting instrumentation that
was already correct, when the actual problem was an unset env var, a base URL missing `/v1`, or an app
that never loaded `.env.openlayer`. Confirm where the failure is before editing code.

## Triage order

1. **Reproduce.** Run the thing that fails and read the actual error. Don't work from the user's
   summary alone — a "traces aren't showing up" report is frequently a 400 or 401 in the app logs.
2. **Check credentials and target** (below) — this covers most "nothing arrives" cases.
3. **Confirm the request leaves the app.** Set `OPENLAYER_VERBOSE=true` if available, or log around
   the publish call. A trace that is never published fails differently from one rejected by the API.
4. **Only then read the instrumentation** for logic errors.

## Nothing arrives in Openlayer

Check in this order — each is a silent failure, not an exception:

| Check | How | If wrong |
| --- | --- | --- |
| `OPENLAYER_API_KEY` set **in the app's process** | Print it (masked) at startup | The app doesn't inherit your shell. `init` writes `.env.openlayer`; the app must load it (dotenv, or your framework's env config) |
| `OPENLAYER_INFERENCE_PIPELINE_ID` set | Same | Without it traces are created and never published — the single most common cause |
| `OPENLAYER_BASE_URL` (self-hosted/local only) ends in `/v1` | Print it | SDKs need the full API root **with** `/v1`; the CLI profile URL omits it. See `references/cli.md` |
| `OPENLAYER_DISABLE_PUBLISH` unset | Same | If truthy, everything is traced and nothing is sent — common leftover from local dev |
| The traced code path actually ran | Add a log line inside the traced function | Wrapping a client the request path doesn't use traces nothing |
| The wrapped client is the one used | Grep for other client constructions | A second, unwrapped client elsewhere bypasses tracing |

If all of these are right and traces still don't appear, the request is probably being **rejected**.
Look for a 4xx in the app's logs and match it below.

## API errors

| Error | Cause | Fix |
| --- | --- | --- |
| `400 Not all input variables specified in inputVariableNames are in the dataset` | A traced function declares a parameter whose value isn't JSON-serializable (callback, client, DB session). The name is declared; the value is dropped on serialization | Pass plain data and derive the non-serializable value inside the function — see `references/monitoring-instrumentation.md` |
| `401` / `403` | Wrong key, or a key from a different workspace | `openlayer whoami`. Keys are per-workspace: Workspace settings → API keys |
| `404` on every call, self-hosted | Base URL missing `/v1` | See the base-URL row above |
| `413 Request Entity Too Large` on push | The bundle includes dependency trees or build output | `.openlayerignore` next to `openlayer.json` — see `references/cli.md` |
| `Context kwarg 'context' not found in inputs` | `@trace(context_kwarg=…)` names something that isn't a parameter of that function | Use `log_context()` / `log_question()` when the step computes its context internally |
| Row published but a column is empty | Set through the wrong mechanism (e.g. context via `update_current_trace`) | Check the enrichment table in `references/monitoring-instrumentation.md` |

## `openlayer push` and bundling

| Symptom | Cause | Fix |
| --- | --- | --- |
| Upload is huge or slow; `413` | `push` bundles the **entire directory containing `openlayer.json`** — a virtualenv, `node_modules`, `.next`, or checkpoints beside it are swept in | Add `.openlayerignore`. Recent CLI versions exclude common dependency/build directories by default and warn before an oversized upload |
| Generated outputs missing from the run | `model.outputDirectory` matches an ignore pattern (`dist`, `build`, …) | Rename it, or re-include with `!dist/` |
| `project id not found. Run 'openlayer link'` in an agent/CI | `link` is TTY-only | Set `OPENLAYER_PROJECT_ID`; never run `link` non-interactively |
| Push fails late with a cryptic error | Skipped validation | `openlayer validate` first |
| Tests SKIPPED rather than failing | Output column isn't the canonical `openlayer_output` | Align the column name — see `references/development-setup.md` |
| Commit "passes" before results exist | `--wait=false` | Keep the default `--wait` — see `references/ci-cd.md` |

## Environment and process problems

- **The app doesn't see the env vars.** `.env.openlayer` is a file, not magic: something has to load
  it. Check for `dotenv`/`python-dotenv` and that it runs *before* the Openlayer import. Next.js and
  similar frameworks only expose specific env files — verify rather than assume.
- **Two Python/Node environments.** The SDK installed in one and the app running in another looks
  exactly like "the SDK doesn't work". Check the interpreter/`node_modules` the app actually uses.
- **Stale SDK.** Method names and wrapper signatures change; an old version fails in confusing ways.
  See `references/sdk-upgrade.md`.
- **Local backend not reachable.** `curl $OPENLAYER_BASE_URL/...` from the same shell before blaming
  the SDK.

## When the root cause is in the user's app

Say so plainly rather than working around it in the instrumentation. Restructuring a function so its
traced parameters are serializable is a legitimate fix; disabling tracing, catching and swallowing the
publish error, or removing columns to make a 400 go away are not — they hide the failure instead of
fixing it.

## Escalation

If the failure survives all of the above, collect for a bug report: SDK version and language, the
exact error with its status code, the relevant env vars (**masked**), and whether it reproduces with a
minimal script. Confirm current behaviour against the docs (`references/docs-access.md`) before
concluding it's a platform bug — the SDKs change often.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Rewriting instrumentation before reproducing the failure | Correct code gets churned while the real cause (env var, base URL, unloaded `.env`) survives | Reproduce and read the actual error first |
| Trusting the user's summary over the logs | "No traces" is often a 400/401 the app swallowed | Find the status code before theorising |
| Fixing a 400 by deleting the offending column | Hides a real config/row mismatch | Make the value serializable — see `references/monitoring-instrumentation.md` |
| Wrapping the publish call in try/except to silence it | Failures become invisible instead of fixed | Let it raise until the cause is understood |
| Assuming the app inherits your shell's env | The process may load nothing at all | Verify from inside the running app |
| Debugging the SDK when the CLI is what's failing (or vice-versa) | Wrong plane entirely | Dev/push problems → `references/cli.md`; trace problems → `references/monitoring-instrumentation.md` |
