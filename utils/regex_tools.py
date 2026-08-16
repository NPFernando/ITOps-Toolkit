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
from queue import Empty
from typing import Any

MAX_PATTERN_LENGTH = 500
MAX_TEXT_LENGTH = 50_000
MAX_REPLACEMENT_LENGTH = 500
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


def _run_worker_with_timeout(target: Any, args: tuple[Any, ...]) -> dict[str, Any] | None:
    """Run ``target`` in a killable subprocess; return its result, or None on timeout.

    Shared by every regex operation in this module (matching, replacing,
    line extraction) so the ReDoS-safety mechanics -- spawn (not fork),
    read-before-join ordering, forced termination on timeout -- live in
    exactly one place.
    """
    # "spawn", not "fork": Streamlit's server is multi-threaded (each page
    # run happens in its own ScriptRunner thread), and forking from a
    # multi-threaded process is a known deadlock hazard (this is also why
    # CPython 3.12+ warns on it). Spawn re-imports the module in a fresh
    # process instead -- slightly slower to start, but safe here.
    ctx = mp.get_context("spawn")
    queue: mp.Queue = ctx.Queue()
    process = ctx.Process(target=target, args=(*args, queue))
    process.start()

    # queue.get() first, THEN join -- not the other way around. A child that
    # finishes fast but writes a large result (e.g. MAX_MATCHES long matches)
    # can block on queue.put() once the pipe's OS buffer fills, and if the
    # parent is sitting in process.join() instead of draining the queue,
    # neither side can proceed. Reading first avoids that deadlock. (Found
    # via the equivalent bug in utils/diff_tools.py, where a fast-but-large
    # result reliably hung for the full timeout with the join-first order.)
    try:
        worker_result = queue.get(timeout=MATCH_TIMEOUT_SECONDS)
    except Empty:
        worker_result = None

    if worker_result is None:
        if process.is_alive():
            process.terminate()
            process.join(timeout=1.0)
            if process.is_alive():
                process.kill()
        process.join()
        return None

    process.join(timeout=1.0)
    return worker_result


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
    worker_result = _run_worker_with_timeout(_match_worker, (pattern, flags_value, text))

    if worker_result is None:
        result["error"] = (
            f"Pattern took longer than {MATCH_TIMEOUT_SECONDS:g}s to evaluate "
            "(possible catastrophic backtracking) and was stopped."
        )
        return result

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


def _replace_worker(pattern: str, flags_value: int, replacement: str, text: str, queue: mp.Queue) -> None:
    try:
        compiled = re.compile(pattern, flags_value)
    except re.error as exc:
        queue.put({"ok": False, "error": f"Invalid pattern: {exc}", "output": None, "replacement_count": 0})
        return

    try:
        output, count = compiled.subn(replacement, text)
    except re.error as exc:
        # e.g. an invalid backreference like \9 when the pattern has fewer groups.
        queue.put({"ok": False, "error": f"Invalid replacement: {exc}", "output": None, "replacement_count": 0})
        return

    queue.put({"ok": True, "error": None, "output": output, "replacement_count": count})


def find_and_replace(pattern: str, replacement: str, text: str, flag_names: tuple[str, ...] = ()) -> dict[str, Any]:
    """Substitute every match of ``pattern`` in ``text`` with ``replacement`` (backreferences like \\1 supported).

    Evaluated in a separate process with a hard timeout, same as test_regex.
    """
    result: dict[str, Any] = {"ok": False, "error": None, "output": None, "replacement_count": 0}

    if not pattern:
        result["error"] = "Enter a regex pattern."
        return result
    if len(pattern) > MAX_PATTERN_LENGTH:
        result["error"] = f"Pattern is longer than {MAX_PATTERN_LENGTH} characters."
        return result
    if len(replacement) > MAX_REPLACEMENT_LENGTH:
        result["error"] = f"Replacement is longer than {MAX_REPLACEMENT_LENGTH} characters."
        return result
    if len(text) > MAX_TEXT_LENGTH:
        result["error"] = f"Text is longer than {MAX_TEXT_LENGTH:,} characters."
        return result

    flags_value = _flags_from_names(flag_names)
    worker_result = _run_worker_with_timeout(_replace_worker, (pattern, flags_value, replacement, text))

    if worker_result is None:
        result["error"] = (
            f"Pattern took longer than {MATCH_TIMEOUT_SECONDS:g}s to evaluate "
            "(possible catastrophic backtracking) and was stopped."
        )
        return result

    if not worker_result["ok"]:
        result["error"] = worker_result["error"]
        return result

    result.update({"ok": True, "output": worker_result["output"], "replacement_count": worker_result["replacement_count"]})
    return result


def _extract_worker(pattern: str, flags_value: int, text: str, queue: mp.Queue) -> None:
    try:
        compiled = re.compile(pattern, flags_value)
    except re.error as exc:
        queue.put({"ok": False, "error": f"Invalid pattern: {exc}", "matching_lines": []})
        return

    matching_lines: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = compiled.search(line)
        if match is None:
            continue
        matching_lines.append({"line_number": line_number, "line": line, "groups": list(match.groups())})
        if len(matching_lines) >= MAX_MATCHES:
            break
    queue.put({"ok": True, "error": None, "matching_lines": matching_lines})


def extract_matches(pattern: str, text: str, flag_names: tuple[str, ...] = ()) -> dict[str, Any]:
    """Return every line of ``text`` that matches ``pattern`` (grep -E style).

    Evaluated in a separate process with a hard timeout, same as test_regex.
    """
    result: dict[str, Any] = {"ok": False, "error": None, "matching_lines": [], "match_count": 0, "truncated": False}

    if not pattern:
        result["error"] = "Enter a regex pattern."
        return result
    if len(pattern) > MAX_PATTERN_LENGTH:
        result["error"] = f"Pattern is longer than {MAX_PATTERN_LENGTH} characters."
        return result
    if len(text) > MAX_TEXT_LENGTH:
        result["error"] = f"Text is longer than {MAX_TEXT_LENGTH:,} characters."
        return result

    flags_value = _flags_from_names(flag_names)
    worker_result = _run_worker_with_timeout(_extract_worker, (pattern, flags_value, text))

    if worker_result is None:
        result["error"] = (
            f"Pattern took longer than {MATCH_TIMEOUT_SECONDS:g}s to evaluate "
            "(possible catastrophic backtracking) and was stopped."
        )
        return result

    if not worker_result["ok"]:
        result["error"] = worker_result["error"]
        return result

    matching_lines = worker_result["matching_lines"]
    result.update(
        {
            "ok": True,
            "matching_lines": matching_lines,
            "match_count": len(matching_lines),
            "truncated": len(matching_lines) >= MAX_MATCHES,
        }
    )
    return result
