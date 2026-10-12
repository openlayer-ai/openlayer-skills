---
name: openlayer-self-hosted
description: Point the SDKs and CLI at a self-hosted / on-prem Openlayer deployment — base URL, private CA certificates, reverse-proxy headers, and SDK-vs-server version skew. Use when the backend is not app.openlayer.com, or when instrumentation that works against the cloud fails against an internal deployment.
---

# Openlayer — Instrumenting against a self-hosted deployment

Instrumentation is identical against on-prem; only *reaching* the backend differs. Everything here
is a **silent** failure — traces are created and dropped, or go to the wrong host — so verify rather
than assume.

Deploying or operating the backend itself is a different job: see the `openlayer-onprem` skill that
ships in the `openlayer-onpremise` repo.

## The base URL

The deployment is fronted by nginx on **port 9000**, and the API root is `${OPENLAYER_URL}/v1`:

```bash
export OPENLAYER_BASE_URL=https://openlayer.internal.example.com/v1   # or http://<host>:9000/v1
```

- **Port 8080 is internal** — it is the backend's in-container port and is not published. Pointing the
  SDK at `:8080` from outside the host will not connect.
- The CLI and the SDKs disagree about the `/v1` suffix. This is the single most common self-hosted
  failure — see `references/cli.md`.
- Python can also set it in code, which beats the env var and is easier to get right in notebooks:
  `openlayer.lib.init(base_url="https://openlayer.internal.example.com/v1")`.
- Verify what was actually resolved with `openlayer.lib.get_tracer_config()` (the key is redacted).
  If `base_url` reads `<sdk default>`, your env var never reached the process.

## TLS with a private CA

Prefer making the certificate **trusted** over disabling verification:

| Runtime | Trust a private CA | Disable verification (last resort) |
| --- | --- | --- |
| Python | `SSL_CERT_FILE` / `REQUESTS_CA_BUNDLE` pointing at the PEM bundle | `OPENLAYER_VERIFY_SSL=false` |
| TypeScript | `NODE_EXTRA_CA_CERTS=/path/to/ca.pem` | No equivalent — build a client by hand with a custom `fetch`/`fetchOptions` |

`OPENLAYER_VERIFY_SSL` has two sharp edges: it is **Python-only**, and it is read **once at module
import**, so it must be set before `import openlayer` — setting it later in the process has no
effect. It is deliberately *not* a parameter of `init()`.

## Reverse proxies and auth gateways

If the deployment sits behind a proxy that needs extra headers, Python has
`OPENLAYER_CUSTOM_HEADERS` — newline-separated `Key: value` lines:

```bash
export OPENLAYER_CUSTOM_HEADERS=$'X-Proxy-Auth: token123\nX-Team: ml-platform'
```

TypeScript has no equivalent env var; pass `defaultHeaders` to a hand-constructed client instead.

## TypeScript: env vars must be set before the import

`src/lib/tracing/tracer.ts` constructs its client at **module scope**, when the module is first
imported. A `dotenv` call placed after the imports runs too late, and traces go to
`api.openlayer.com` with no error:

```ts
import 'dotenv/config';              // must come FIRST
import { traceOpenAI } from 'openlayer/lib';
```

Or set the variables in the process environment before the app starts. Python is lazy here and has
`init(base_url=...)` as a second chance; TypeScript has neither.

## Version skew

There is no version negotiation — no API-version header, no compatibility check. A current SDK
against an older pinned deployment fails as `404`/`422` on endpoints the server doesn't have yet,
with nothing identifying the cause. When something works against the cloud and 404s on-prem, compare
the deployment's `/v1/diagnostics/build-info` against the SDK version before debugging the code.

## Airgapped deployments

Tracing, publishing, and the CLI need no public egress. Two things still do: the MCP's
`search_openlayer_docs` tool calls a separate docs endpoint (`OPENLAYER_DOCS_MCP_URL`), not
`OPENLAYER_BASE_URL`; and installing or upgrading the SDK needs PyPI/npm or an internal mirror.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| `OPENLAYER_BASE_URL` without `/v1` | `404` on every call | The SDK base URL is the full API root — see `references/cli.md` |
| Pointing the SDK at port `8080` | Connection refused/timeout from outside the host | Use the nginx port (`9000`) or the fronting domain |
| Setting `OPENLAYER_VERIFY_SSL` after `import openlayer` | Silently ignored; TLS still verified | Set it before the import — or better, trust the CA via `SSL_CERT_FILE` |
| Expecting `OPENLAYER_VERIFY_SSL` / `OPENLAYER_CUSTOM_HEADERS` to work in TypeScript | Neither exists there | `NODE_EXTRA_CA_CERTS`, or a hand-built client |
| `dotenv` imported after the Openlayer import in TS | Traces silently go to the public cloud | Load env first, or set it outside the process |
| Debugging instrumentation when the server is simply older | Correct code gets churned | Check `/v1/diagnostics/build-info` against the SDK version |
| Disabling TLS verification as the first move | Ships an insecure default to production | Trust the CA bundle; reserve `verify=false` for a local throwaway |
