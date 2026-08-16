#!/usr/bin/env python3
"""Small repository-local skill validator for CI."""

from __future__ import annotations

import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")
    try:
        _, block, _ = text.split("---\n", 2)
    except ValueError:
        fail("SKILL.md frontmatter is not closed")
    values: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            fail(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: quick_validate.py <skill-dir>")
    skill_dir = Path(sys.argv[1])
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        fail("missing SKILL.md")
    meta = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    name = meta.get("name", "")
    description = meta.get("description", "")
    if not NAME_RE.fullmatch(name):
        fail("invalid skill name")
    if skill_dir.name != name:
        fail("skill directory name must match frontmatter name")
    if not description or "TODO" in description:
        fail("description is missing or incomplete")
    if "TODO" in skill_md.read_text(encoding="utf-8"):
        fail("SKILL.md contains TODO placeholders")
    if not (skill_dir / "agents" / "openai.yaml").is_file():
        fail("missing agents/openai.yaml")
    print(f"PASS: {name} is structurally valid")


if __name__ == "__main__":
    main()
