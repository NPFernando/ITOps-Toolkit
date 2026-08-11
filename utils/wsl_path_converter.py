"""Convert a filesystem path between Windows and WSL/Git-Bash Unix-style forms.

WSL mounts a Windows drive at /mnt/<lowercase-drive-letter>/...; Git Bash
(MSYS) mounts it at /<lowercase-drive-letter>/... instead -- a real,
frequently-confused difference, so both are supported as explicit targets
rather than assuming one.
"""

from __future__ import annotations

import re
from typing import Any

MAX_INPUT_LENGTH = 4_096

_WINDOWS_DRIVE_RE = re.compile(r"^([A-Za-z]):[\\/]?(.*)$")
_WSL_PATH_RE = re.compile(r"^/mnt/([a-zA-Z])(?:/(.*))?$")
_GITBASH_PATH_RE = re.compile(r"^/([a-zA-Z])(?:/(.*))?$")

TARGETS: tuple[str, ...] = ("WSL (/mnt/c/...)", "Git Bash (/c/...)", "Windows (C:\\...)")


def _to_unix(drive: str, rest: str, style: str) -> str:
    rest = rest.replace("\\", "/")
    prefix = f"/mnt/{drive.lower()}" if style.startswith("WSL") else f"/{drive.lower()}"
    return f"{prefix}/{rest}" if rest else prefix


def convert_path(path: str, target: str) -> dict[str, Any]:
    """Convert ``path`` (Windows or WSL/Git-Bash form) into the requested ``target`` form."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    value = (path or "").strip()
    if not value:
        result["error"] = "Enter a path to convert."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result
    if target not in TARGETS:
        result["error"] = f"Unknown target. Choose one of: {', '.join(TARGETS)}."
        return result

    windows_match = _WINDOWS_DRIVE_RE.match(value)
    wsl_match = _WSL_PATH_RE.match(value)
    gitbash_match = _GITBASH_PATH_RE.match(value) if not wsl_match else None

    if windows_match:
        drive, rest = windows_match.groups()
    elif wsl_match:
        drive, rest = wsl_match.groups()
    elif gitbash_match:
        drive, rest = gitbash_match.groups()
    else:
        result["error"] = r"Could not recognize this as a Windows path (C:\...), a WSL path (/mnt/c/...), or a Git Bash path (/c/...)."
        return result
    rest = rest or ""

    if target == "Windows (C:\\...)":
        output = f"{drive.upper()}:\\" + rest.replace("/", "\\")
    else:
        output = _to_unix(drive, rest, target)

    result.update({"ok": True, "output": output})
    return result
