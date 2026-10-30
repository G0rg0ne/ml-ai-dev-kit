#!/usr/bin/env python3
"""PreToolUse hook: block agent access to secret files such as .env.

Reads the hook event as JSON on stdin. Exits 2, with the reason on stderr,
to block a tool call that would read, edit, create, move, or delete a secret
file, or dump the environment. Exits 0 to let the call through. Template
files (.env.example, .env.sample, .env.template) stay accessible.
"""

from __future__ import annotations

import json
import re
import sys
from typing import Any

BLOCK_EXIT_CODE = 2

TEMPLATE_SUFFIXES = (".example", ".sample", ".template", ".dist")

SECRET_NAME_PATTERNS = [
    re.compile(r"^\.env(\..+)?$"),
    re.compile(r"^.+\.env$"),
    re.compile(r"^.+\.(pem|key|p12|pfx|jks|keystore)$"),
    re.compile(r"^id_(rsa|dsa|ecdsa|ed25519)$"),
    re.compile(r"^\.(netrc|pgpass|pypirc|npmrc)$"),
    re.compile(r"^credentials(\.json)?$"),
    re.compile(r"^secrets?\.(json|ya?ml|toml)$"),
]

SECRET_TOKEN_IN_COMMAND = re.compile(
    r"(?<![\w.-])"
    r"(\.env(?:\.[\w.-]+)?|[\w.-]+\.env|[\w.-]+\.(?:pem|key|p12|pfx|jks|keystore)"
    r"|id_(?:rsa|dsa|ecdsa|ed25519)|\.(?:netrc|pgpass|pypirc|npmrc)"
    r"|credentials\.json|secrets?\.(?:json|ya?ml|toml))"
    r"(?![\w-])"
)

ENV_DUMP_COMMAND = re.compile(
    r"(^|[;&|(]\s*)(printenv\b|env\s*($|[;&|)])|export\s+-p\b|set\s*($|[;&|)]))"
)

FILE_TOOLS = {"Read", "Edit", "Write", "MultiEdit", "NotebookEdit"}

REASON_SUFFIX = (
    "Secret files are off limits to the agent. Work from .env.example instead, "
    "and ask the person to edit their own .env."
)


def basename(path: str) -> str:
    """Return the last component of a POSIX or Windows path."""
    return re.split(r"[\\/]", path.rstrip("\\/"))[-1]


def is_secret_name(name: str) -> bool:
    """Tell whether a file name designates a secret file."""
    lowered = name.lower()
    if lowered.endswith(TEMPLATE_SUFFIXES):
        return False
    return any(pattern.match(lowered) for pattern in SECRET_NAME_PATTERNS)


def is_secret_path(path: str) -> bool:
    """Tell whether a path points to a secret file."""
    return bool(path) and is_secret_name(basename(path))


def secret_tokens_in_command(command: str) -> list[str]:
    """Return the secret file names referenced by a shell command."""
    return [
        match.group(1)
        for match in SECRET_TOKEN_IN_COMMAND.finditer(command)
        if is_secret_name(basename(match.group(1)))
    ]


def check(event: dict[str, Any]) -> str | None:
    """Return a block reason for the tool call, or None to allow it."""
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}

    if tool in FILE_TOOLS:
        path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        if is_secret_path(path):
            return f"{tool} on {basename(path)} is blocked."

    if tool == "Grep":
        for key in ("path", "glob"):
            value = tool_input.get(key) or ""
            if is_secret_path(value) or secret_tokens_in_command(value):
                return f"Grep into {value} is blocked."

    if tool == "Bash":
        command = tool_input.get("command") or ""
        tokens = secret_tokens_in_command(command)
        if tokens:
            return f"Shell command touching {', '.join(sorted(set(tokens)))} is blocked."
        if ENV_DUMP_COMMAND.search(command):
            return "Dumping environment variables is blocked."

    return None


def main() -> int:
    """Run the hook on the event read from stdin."""
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("protect_secrets: unreadable hook input, call blocked.", file=sys.stderr)
        return BLOCK_EXIT_CODE

    reason = check(event)
    if reason:
        print(f"{reason} {REASON_SUFFIX}", file=sys.stderr)
        return BLOCK_EXIT_CODE
    return 0


if __name__ == "__main__":
    sys.exit(main())
