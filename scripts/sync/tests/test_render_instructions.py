"""Tests of render-instructions.py on a temporary repository root."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "render-instructions.py"


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


class RenderInstructions(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.source = self.root / ".claude" / "CLAUDE.md"
        self.source.parent.mkdir()
        self.source.write_text("# Kit\n\nRules.\n", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_writes_agents_md_with_header_and_source(self) -> None:
        self.assertEqual(run(self.root).returncode, 0)
        agents = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertTrue(agents.startswith("<!-- Generated from .claude/CLAUDE.md"))
        self.assertTrue(agents.endswith("# Kit\n\nRules.\n"))

    def test_check_fails_when_missing_or_stale(self) -> None:
        self.assertEqual(run(self.root, "--check").returncode, 1)
        run(self.root)
        self.source.write_text("# Kit\n\nNew rule.\n", encoding="utf-8")
        result = run(self.root, "--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("make sync", result.stderr)

    def test_check_passes_after_sync(self) -> None:
        run(self.root)
        self.assertEqual(run(self.root, "--check").returncode, 0)

    def test_missing_claude_md_fails(self) -> None:
        self.source.unlink()
        self.assertEqual(run(self.root).returncode, 1)


if __name__ == "__main__":
    unittest.main()
