"""Build a <meta name="robots" content="..."> tag from selected directives.

Distinct from robots.txt / Sitemap Validator, which validates a site's
robots.txt file (a separate mechanism, fetched live) -- this builds the
per-page HTML meta tag, entirely locally. Directives follow Google's
documented robots meta tag values.
"""

from __future__ import annotations

from typing import Any

INDEXING = ("index", "noindex")
FOLLOWING = ("follow", "nofollow")
MAX_SNIPPET_DEFAULT = -1


def build_robots_meta(
    indexing: str = "index",
    following: str = "follow",
    noarchive: bool = False,
    nosnippet: bool = False,
    noimageindex: bool = False,
    max_snippet: int | None = None,
    max_image_preview: str = "",
    max_video_preview: int | None = None,
) -> dict[str, Any]:
    """Build a robots meta tag's content attribute from selected directives."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    if indexing not in INDEXING:
        result["error"] = f"Unknown indexing directive: {indexing}."
        return result
    if following not in FOLLOWING:
        result["error"] = f"Unknown following directive: {following}."
        return result
    if max_image_preview and max_image_preview not in ("none", "standard", "large"):
        result["error"] = f"Unknown max-image-preview value: {max_image_preview}."
        return result

    directives = [indexing, following]
    if noarchive:
        directives.append("noarchive")
    if nosnippet:
        directives.append("nosnippet")
    if noimageindex:
        directives.append("noimageindex")
    if max_snippet is not None:
        directives.append(f"max-snippet:{max_snippet}")
    if max_image_preview:
        directives.append(f"max-image-preview:{max_image_preview}")
    if max_video_preview is not None:
        directives.append(f"max-video-preview:{max_video_preview}")

    content = ", ".join(directives)
    result.update({"ok": True, "output": f'<meta name="robots" content="{content}">'})
    return result
