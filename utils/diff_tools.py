"""Text diff helpers.

Runs the actual comparison in a separate, killable process with a hard
wall-clock timeout, same approach as utils/regex_tools.py. difflib's default
autojunk=True heuristic avoids the worst pathological cases (confirmed: a
naive autojunk=False comparison of 10,000 repeated lines plus one differing
line did not finish within 15 seconds; the autojunk=True default resolves
that same input in milliseconds) -- but it is a heuristic, not a guarantee,
against arbitrary adversarial input on a public server, so the process
timeout stays as a backstop rather than relying on the heuristic alone.
"""

from __future__ import annotations

import difflib
import multiprocessing as mp
from queue import Empty
from typing import Any

MAX_INPUT_LENGTH = 200_000
MAX_LINES = 20_000
DIFF_TIMEOUT_SECONDS = 3.0


def _diff_worker(original_lines: list[str], changed_lines: list[str], ignore_whitespace: bool, queue: mp.Queue) -> None:
    compare_original = [line.strip() for line in original_lines] if ignore_whitespace else original_lines
    compare_changed = [line.strip() for line in changed_lines] if ignore_whitespace else changed_lines

    matcher = difflib.SequenceMatcher(None, compare_original, compare_changed)
    lines: list[dict[str, Any]] = []
    added = 0
    removed = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            lines.extend({"type": "equal", "text": line} for line in original_lines[i1:i2])
        elif tag == "delete":
            lines.extend({"type": "removed", "text": line} for line in original_lines[i1:i2])
            removed += i2 - i1
        elif tag == "insert":
            lines.extend({"type": "added", "text": line} for line in changed_lines[j1:j2])
            added += j2 - j1
        elif tag == "replace":
            lines.extend({"type": "removed", "text": line} for line in original_lines[i1:i2])
            lines.extend({"type": "added", "text": line} for line in changed_lines[j1:j2])
            removed += i2 - i1
            added += j2 - j1

    queue.put(
        {
            "ok": True,
            "lines": lines,
            "similarity": round(matcher.ratio() * 100, 1),
            "added": added,
            "removed": removed,
        }
    )


def compare_text(original: str, changed: str, ignore_whitespace: bool = False) -> dict[str, Any]:
    """Line-by-line diff of ``original`` vs ``changed``, evaluated with a hard timeout."""
    result: dict[str, Any] = {
        "ok": False,
        "lines": [],
        "similarity": None,
        "added": 0,
        "removed": 0,
        "error": None,
    }

    if len(original) > MAX_INPUT_LENGTH or len(changed) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    original_lines = original.splitlines()
    changed_lines = changed.splitlines()
    if len(original_lines) > MAX_LINES or len(changed_lines) > MAX_LINES:
        result["error"] = f"Input has more than {MAX_LINES:,} lines."
        return result

    ctx = mp.get_context("spawn")
    queue: mp.Queue = ctx.Queue()
    process = ctx.Process(target=_diff_worker, args=(original_lines, changed_lines, ignore_whitespace, queue))
    process.start()

    # queue.get() first, THEN join -- not the other way around. A child that
    # finishes fast but writes a large result can block on queue.put() once
    # the pipe's OS buffer fills, and if the parent is sitting in
    # process.join() instead of draining the queue, neither side can
    # proceed: the child can't exit until put() returns, and join() won't
    # return until the child exits. Reading first avoids that deadlock.
    try:
        worker_result = queue.get(timeout=DIFF_TIMEOUT_SECONDS)
    except Empty:
        worker_result = None

    if worker_result is None:
        if process.is_alive():
            process.terminate()
            process.join(timeout=1.0)
            if process.is_alive():
                process.kill()
        process.join()
        result["error"] = f"Comparison took longer than {DIFF_TIMEOUT_SECONDS:g}s and was stopped."
        return result

    process.join(timeout=1.0)
    result.update(worker_result)
    return result
