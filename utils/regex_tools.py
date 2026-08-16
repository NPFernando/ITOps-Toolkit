"""Regex testing helpers.

Runs the actual match in a separate, killable process with a hard wall-clock
timeout. This is not a length-limit or best-effort precaution -- a
catastrophic-backtracking pattern like ``(a+)+$`` against 30 characters of
input can hang Python's `re` engine for 50+ seconds (confirmed locally), and
the GIL means a pure-Python timeout can't actually stop a runaway match, only
abandon waiting for it while it keeps burning a worker thread. A forcibly
terminated subprocess is the only reliable way to bound this on a public,
shared server.
"""

from __future__ import annotations

import multiprocessing as mp
import re
from typing import Any

MAX_PATTERN_LENGTH = 500
MAX_TEXT_LENGTH = 50_000
MAX_MATCHES = 500
MATCH_TIMEOUT_SECONDS = 2.0

FLAG_OPTIONS = ("IGNORECASE", "MULTILINE", "DOTALL")


def _flags_from_names(names: tuple[str, ...]) -> int:
    value = 0
    for name in names:
        value |= getattr(re, name)
    return value


def _match_worker(pattern: str, flags_value: int, text: str, queue: mp.Queue) -> None:
    try:
        compiled = re.compile(pattern, flags_value)
    except re.error as exc:
        queue.put({"ok": False, "error": f"Invalid pattern: {exc}", "matches": []})
        return

    matches: list[dict[str, Any]] = []
    for match in compiled.finditer(text):
        matches.append(
            {
                "match": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "groups": list(match.groups()),
            }
        )
        if len(matches) >= MAX_MATCHES:
            break
    queue.put({"ok": True, "error": None, "matches": matches})


def test_regex(pattern: str, text: str, flag_names: tuple[str, ...] = ()) -> dict[str, Any]:
    """Find all non-overlapping matches of ``pattern`` in ``text``.

    Evaluated in a separate process with a hard timeout so a catastrophic-
    backtracking pattern gets killed instead of hanging a worker.
    """
    result: dict[str, Any] = {"ok": False, "matches": [], "match_count": 0, "truncated": False, "error": None}

    if not pattern:
        result["error"] = "Enter a regex pattern."
        return result
    if len(pattern) > MAX_PATTERN_LENGTH:
        result["error"] = f"Pattern is longer than {MAX_PATTERN_LENGTH} characters."
        return result
    if len(text) > MAX_TEXT_LENGTH:
        result["error"] = f"Test text is longer than {MAX_TEXT_LENGTH:,} characters."
        return result

    flags_value = _flags_from_names(flag_names)
    # "spawn", not "fork": Streamlit's server is multi-threaded (each page
    # run happens in its own ScriptRunner thread), and forking from a
    # multi-threaded process is a known deadlock hazard (this is also why
    # CPython 3.12+ warns on it). Spawn re-imports the module in a fresh
    # process instead -- slightly slower to start, but safe here.
    ctx = mp.get_context("spawn")
    queue: mp.Queue = ctx.Queue()
    process = ctx.Process(target=_match_worker, args=(pattern, flags_value, text, queue))
    process.start()
    process.join(timeout=MATCH_TIMEOUT_SECONDS)

    if process.is_alive():
        process.terminate()
        process.join(timeout=1.0)
        if process.is_alive():
            process.kill()
            process.join()
        result["error"] = (
            f"Pattern took longer than {MATCH_TIMEOUT_SECONDS:g}s to evaluate "
            "(possible catastrophic backtracking) and was stopped."
        )
        return result

    if queue.empty():
        result["error"] = "Pattern evaluation failed unexpectedly."
        return result

    worker_result = queue.get()
    if not worker_result["ok"]:
        result["error"] = worker_result["error"]
        return result

    matches = worker_result["matches"]
    result.update(
        {
            "ok": True,
            "matches": matches,
            "match_count": len(matches),
            "truncated": len(matches) >= MAX_MATCHES,
        }
    )
    return result
