# Contributing

Thanks for improving the Openlayer skills. See [`agents.md`](./agents.md) for the editorial rules
(lean references, link to docs, "only add a use case if it beats the docs").

## Add or edit a skill

- Skills live under `skills/<name>/SKILL.md` with use-case files in `skills/<name>/references/`.
- Frontmatter must have `name` (kebab-case) and `description`; the description must be ≤1024 chars
  and contain no angle brackets (`<` / `>`).
- Add new references to the router table in `SKILL.md` and end each reference with a Common Mistakes table.

## Validate before opening a PR

```bash
python3 -m pip install pyyaml
python3 scripts/validate_skills.py
```

This checks frontmatter, that every `references/<x>.md` cross-link resolves, and that the plugin
versions are in lockstep. CI runs the same check on every PR (`.github/workflows/validate-skills.yml`).

## Versioning (semver) & releases

The repo ships as a plugin to two marketplaces, each with its own manifest:

- `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` (Claude Code)
- `.cursor-plugin/plugin.json` (Cursor)

All three `version` fields **must stay in lockstep** — bump them together in the same PR (CI enforces this):

- **patch** (`0.1.0` → `0.1.1`): content fixes / clarifications
- **minor** (`0.1.0` → `0.2.0`): a new reference or meaningful new capability
- **major** (`0.1.0` → `1.0.0`): removing/renaming a skill or any breaking change to how users invoke it

No bump for: typos, formatting, or changes outside the published skill (this file, CI, `agents.md`).

To cut a release: bump the three versions, merge, then tag `vX.Y.Z` on `main`.
