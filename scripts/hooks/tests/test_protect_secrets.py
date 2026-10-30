"""Tests of the protect_secrets hook, fed sample stdin JSON without a harness."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "protect_secrets.py"


def run_hook(payload: object) -> subprocess.CompletedProcess[str]:
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


def event(tool: str, **tool_input: str) -> dict:
    return {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input}


class BlocksSecretFiles(unittest.TestCase):
    def assert_blocked(self, payload: object) -> None:
        result = run_hook(payload)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertTrue(result.stderr.strip())

    def test_read_env(self) -> None:
        self.assert_blocked(event("Read", file_path="/repo/.env"))

    def test_read_env_windows_path(self) -> None:
        self.assert_blocked(event("Read", file_path=r"C:\repo\backend\.env.local"))

    def test_edit_and_write_env(self) -> None:
        self.assert_blocked(event("Edit", file_path="/repo/.env"))
        self.assert_blocked(event("Write", file_path="/repo/.env.production"))
        self.assert_blocked(event("MultiEdit", file_path="/repo/prod.env"))

    def test_private_keys(self) -> None:
        self.assert_blocked(event("Read", file_path="/home/me/.ssh/id_ed25519"))
        self.assert_blocked(event("Read", file_path="/repo/certs/server.pem"))
        self.assert_blocked(event("Read", file_path="/home/me/.aws/credentials"))
        self.assert_blocked(event("Bash", command="cat ~/.ssh/id_rsa"))

    def test_grep_into_env(self) -> None:
        self.assert_blocked(event("Grep", pattern="KEY", path="/repo/.env"))
        self.assert_blocked(event("Grep", pattern="KEY", glob=".env*"))

    def test_shell_reads_deletes_or_copies_env(self) -> None:
        for command in (
            "cat .env",
            "rm -f backend/.env",
            "mv .env .env.bak",
            "cp .env.example .env",
            "echo API_KEY=x >> .env",
            "source .env && run",
            "uv run --env-file .env app",
        ):
            with self.subTest(command=command):
                self.assert_blocked(event("Bash", command=command))

    def test_shell_dumps_environment(self) -> None:
        for command in ("printenv", "env", "env | grep KEY", "ls; set"):
            with self.subTest(command=command):
                self.assert_blocked(event("Bash", command=command))

    def test_unreadable_input_fails_closed(self) -> None:
        self.assert_blocked("not json")


class AllowsEverythingElse(unittest.TestCase):
    def assert_allowed(self, payload: dict) -> None:
        result = run_hook(payload)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_templates(self) -> None:
        self.assert_allowed(event("Read", file_path="/repo/.env.example"))
        self.assert_allowed(event("Edit", file_path="/repo/.env.example"))
        self.assert_allowed(event("Read", file_path="/repo/.env.sample"))

    def test_regular_files(self) -> None:
        self.assert_allowed(event("Read", file_path="/repo/src/app/config.py"))
        self.assert_allowed(event("Edit", file_path="/repo/.envrc.md"))
        self.assert_allowed(event("Read", file_path="/repo/.gitignore"))
        self.assert_allowed(event("Read", file_path="/repo/environment.yml"))

    def test_regular_commands(self) -> None:
        for command in (
            "uv add python-dotenv",
            "cat .env.example",
            "env FOO=1 pytest",
            "docker compose up",
            "git status",
            "grep -rn credentials src/",
        ):
            with self.subTest(command=command):
                self.assert_allowed(event("Bash", command=command))

    def test_glob_lists_names_only(self) -> None:
        self.assert_allowed(event("Glob", pattern="**/.env*"))


if __name__ == "__main__":
    unittest.main()
