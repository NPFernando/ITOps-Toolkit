"""Static reference table of Linux/Bash process exit codes.

Codes 0-2 and 126-165 have widely-documented conventional meanings (Bash
manual, and the POSIX convention that a process killed by signal N exits
with code 128+N). 3-125 are reserved for application-defined meanings and
have no universal interpretation, so they are deliberately not listed as
if they meant something specific.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExitCodeEntry:
    code: int
    meaning: str
    detail: str


EXIT_CODES: tuple[ExitCodeEntry, ...] = (
    ExitCodeEntry(0, "Success", "Command completed without error."),
    ExitCodeEntry(1, "General error", "Catchall for miscellaneous errors -- the most common non-zero exit code."),
    ExitCodeEntry(2, "Misuse of shell builtin", "Missing argument, invalid option, or similar shell-level usage error."),
    ExitCodeEntry(126, "Command found but not executable", "Often a permissions problem, or the file isn't actually a valid executable/script."),
    ExitCodeEntry(127, "Command not found", "Typo, or the binary isn't on $PATH."),
    ExitCodeEntry(128, "Invalid exit argument", "exit was called with a non-integer argument."),
    ExitCodeEntry(130, "Terminated by SIGINT (128+2)", "The process was interrupted, usually by Ctrl+C."),
    ExitCodeEntry(131, "Terminated by SIGQUIT (128+3)", "Quit signal, usually Ctrl+\\."),
    ExitCodeEntry(134, "Terminated by SIGABRT (128+6)", "The process called abort(), often from a failed assertion."),
    ExitCodeEntry(135, "Terminated by SIGBUS (128+7)", "Bus error -- misaligned or invalid memory access."),
    ExitCodeEntry(136, "Terminated by SIGFPE (128+8)", "Fatal arithmetic error, e.g. integer division by zero."),
    ExitCodeEntry(137, "Terminated by SIGKILL (128+9)", "Force-killed, e.g. kill -9 or an OOM killer."),
    ExitCodeEntry(139, "Terminated by SIGSEGV (128+11)", "Segmentation fault -- invalid memory access."),
    ExitCodeEntry(141, "Terminated by SIGPIPE (128+13)", "Wrote to a pipe with no reader, e.g. the read end of a | pipeline exited early."),
    ExitCodeEntry(143, "Terminated by SIGTERM (128+15)", "Graceful termination request, e.g. kill's default signal."),
    ExitCodeEntry(148, "Terminated by SIGTSTP (128+20)", "Terminal stop request, usually Ctrl+Z."),
    ExitCodeEntry(255, "Exit status out of range", "Exit codes are 0-255; a program that tries to exit with a larger or negative value wraps into this range."),
)


def search_exit_codes(query: str) -> tuple[ExitCodeEntry, ...]:
    """Filter EXIT_CODES by code, meaning, or detail (case-insensitive substring match)."""
    needle = (query or "").strip().lower()
    if not needle:
        return EXIT_CODES
    return tuple(
        entry
        for entry in EXIT_CODES
        if needle in str(entry.code) or needle in entry.meaning.lower() or needle in entry.detail.lower()
    )
