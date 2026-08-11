"""Regex find & replace -- shows the substituted output, not just match/no-match.

Distinct from Regex Tester (which only shows match/no-match and capture
groups, not a substituted result). Reuses utils.regex_tools's subprocess-
isolated evaluation (see that module's docstring for why) rather than
calling re.sub directly -- a catastrophic-backtracking pattern would
otherwise hang a worker.
"""

from __future__ import annotations

from utils.regex_tools import FLAG_OPTIONS, MAX_PATTERN_LENGTH, MAX_REPLACEMENT_LENGTH, MAX_TEXT_LENGTH, find_and_replace

__all__ = ["FLAG_OPTIONS", "MAX_PATTERN_LENGTH", "MAX_REPLACEMENT_LENGTH", "MAX_TEXT_LENGTH", "find_and_replace"]
