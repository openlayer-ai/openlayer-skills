#!/usr/bin/env python3
"""Validate the Openlayer skills repo for CI.

Checks, for every skill under skills/*:
  - SKILL.md exists with valid YAML frontmatter (name, description)
  - name is kebab-case (<=64 chars); description has no angle brackets and <=1024 chars
  - every references/*.md has the same frontmatter constraints
  - every `references/<x>.md` cross-link in the skill resolves to a file that exists
  - every references/*.md is linked from SKILL.md (no orphans invisible to the router)

And repo-wide:
  - the `version` in .claude-plugin/plugin.json, .claude-plugin/marketplace.json,
    and .cursor-plugin/plugin.json are all identical (lockstep)

Exit code 0 if everything passes, 1 otherwise. Stdlib + pyyaml only.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
ALLOWED_FM = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def frontmatter(md: Path) -> dict | None:
    text = md.read_text()
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        err(f"{md}: no YAML frontmatter")
        return None
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        err(f"{md}: invalid YAML frontmatter: {e}")
        return None
    if not isinstance(fm, dict):
        err(f"{md}: frontmatter is not a mapping")
        return None
    return fm


def check_fm(md: Path, fm: dict, *, top_level: bool) -> None:
    name = (fm.get("name") or "").strip()
    desc = (fm.get("description") or "").strip()
    if not name:
        err(f"{md}: missing 'name'")
    elif not re.match(r"^[a-z0-9-]+$", name) or name.startswith("-") or name.endswith("-") or "--" in name:
        err(f"{md}: name '{name}' must be kebab-case")
    elif len(name) > 64:
        err(f"{md}: name too long ({len(name)} > 64)")
    if not desc:
        err(f"{md}: missing 'description'")
    else:
        if "<" in desc or ">" in desc:
            err(f"{md}: description must not contain angle brackets")
        if len(desc) > 1024:
            err(f"{md}: description too long ({len(desc)} > 1024)")
    if top_level:
        unexpected = set(fm) - ALLOWED_FM
        if unexpected:
            err(f"{md}: unexpected frontmatter keys: {sorted(unexpected)}")


def validate_skill(skill_dir: Path) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        err(f"{skill_dir}: missing SKILL.md")
        return
    fm = frontmatter(skill_md)
    if fm:
        check_fm(skill_md, fm, top_level=True)

    md_files = [skill_md, *sorted((skill_dir / "references").glob("*.md"))]
    for ref in (skill_dir / "references").glob("*.md"):
        rfm = frontmatter(ref)
        if rfm:
            check_fm(ref, rfm, top_level=False)

    # cross-links resolve
    for md in md_files:
        for link in re.findall(r"references/[a-z][a-z0-9-]*\.md", md.read_text()):
            if not (skill_dir / link).exists():
                err(f"{md}: dangling cross-link -> {link}")

    # no orphan references: every references/*.md must be linked from SKILL.md
    skill_links = set(re.findall(r"references/[a-z][a-z0-9-]*\.md", skill_md.read_text()))
    for ref in sorted((skill_dir / "references").glob("*.md")):
        if f"references/{ref.name}" not in skill_links:
            err(f"{ref}: orphan reference — not linked from {skill_md.name}")


def check_version_lockstep() -> None:
    files = [
        REPO / ".claude-plugin/plugin.json",
        REPO / ".claude-plugin/marketplace.json",
        REPO / ".cursor-plugin/plugin.json",
    ]
    versions = {}
    for f in files:
        if f.exists():
            try:
                versions[str(f.relative_to(REPO))] = json.loads(f.read_text()).get("version")
            except json.JSONDecodeError as e:
                err(f"{f}: invalid JSON: {e}")
    distinct = set(versions.values())
    if len(distinct) > 1:
        err(f"plugin versions out of lockstep: {versions}")


def main() -> int:
    skills_root = REPO / "skills"
    skill_dirs = [d for d in skills_root.iterdir() if (d / "SKILL.md").exists()] if skills_root.exists() else []
    if not skill_dirs:
        err("no skills found under skills/*/SKILL.md")
    for d in skill_dirs:
        validate_skill(d)
    check_version_lockstep()

    if errors:
        print("Skill validation FAILED:")
        for e in errors:
            print("  -", e)
        return 1
    print(f"OK — {len(skill_dirs)} skill(s) valid, cross-links resolve, versions in lockstep.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
