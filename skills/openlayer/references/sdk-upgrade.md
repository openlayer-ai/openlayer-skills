---
name: openlayer-sdk-upgrade
description: Install or upgrade the Openlayer SDK (Python pip / TypeScript npm) to the latest version and re-verify imports. Use when setting up the SDK, bumping versions, or fixing import errors after an upgrade.
---

# Openlayer SDK Install / Upgrade

Use the latest SDK — older versions miss integrations and change import paths. Don't downgrade to match
an old snippet; update the snippet instead.

## Install / upgrade

```bash
# Python
pip install -U openlayer
python -c "import openlayer; print(openlayer.__version__)"

# TypeScript / Node
npm install openlayer@latest      # (or pnpm/yarn/bun add openlayer)
```

Both publish under the package name `openlayer`. Pin a known-good version in your lockfile/requirements
for reproducibility; bump deliberately.

## After upgrading

- Re-verify tracing imports — integration helpers live in `openlayer.lib` (Python). Confirm the names
  you use still exist (fetch `monitoring/instrument` / `alternative-integrations` docs if an import fails).
- Check release notes / the docs (`references/docs-access.md`) for breaking changes before bumping a major.
- Keep SDK major versions consistent across services that share a pipeline.

## Common Mistakes

| Mistake | Problem | Fix |
| ------- | ------- | --- |
| Downgrading to match an old example | Loses fixes/integrations | Upgrade the SDK; update the code |
| Assuming an old import path still works | ImportError after upgrade | Re-check exports in `openlayer.lib` via the docs |
| Mixing SDK majors across services | Inconsistent trace/payload behavior | Align versions |
| Not pinning in CI | Non-reproducible builds | Pin in requirements/lockfile, bump deliberately |
