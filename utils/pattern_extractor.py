"""Extract lines matching a regex pattern -- grep -E over pasted text.

Distinct from Regex Tester (single-string match/no-match) and Log
Troubleshooting Assistant (fixed known-issue patterns, not a user-supplied
pattern). Reuses utils.regex_tools's subprocess-isolated evaluation (see
that module's docstring for why) rather than calling re.search directly --
a catastrophic-backtracking pattern would otherwise hang a worker.
"""

from __future__ import annotations

from utils.regex_tools import FLAG_OPTIONS, MAX_PATTERN_LENGTH, MAX_TEXT_LENGTH, extract_matches

__all__ = ["FLAG_OPTIONS", "MAX_PATTERN_LENGTH", "MAX_TEXT_LENGTH", "extract_matches"]
