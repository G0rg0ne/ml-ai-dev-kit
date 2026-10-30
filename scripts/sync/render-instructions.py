#!/usr/bin/env python3
"""Generate AGENTS.md from .claude/CLAUDE.md, so every host reads the same instructions.

Run without arguments to write AGENTS.md at the repository root. Run with
--check to exit 1 when AGENTS.md is missing or differs from what
.claude/CLAUDE.md would produce.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]

HEADER = (
    "<!-- Generated from .claude/CLAUDE.md by `make sync`. "
    "Edit .claude/CLAUDE.md, not this file. -->\n\n"
)


def render(source: Path) -> str:
    """Return the AGENTS.md content for the given .claude/CLAUDE.md."""
    return HEADER + source.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Write or check AGENTS.md."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="fail if AGENTS.md is out of date"
    )
    parser.add_argument(
        "--root", type=Path, default=DEFAULT_ROOT, help="repository root"
    )
    args = parser.parse_args(argv)

    source = args.root / ".claude" / "CLAUDE.md"
    target = args.root / "AGENTS.md"
    if not source.is_file():
        print(f"{source} not found.", file=sys.stderr)
        return 1

    expected = render(source)
    if args.check:
        current = target.read_text(encoding="utf-8") if target.is_file() else ""
        if current != expected:
            print("AGENTS.md is out of date: run `make sync`.", file=sys.stderr)
            return 1
        print("AGENTS.md is up to date.")
        return 0

    target.write_text(expected, encoding="utf-8", newline="\n")
    print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
