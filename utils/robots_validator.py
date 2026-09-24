"""Fetch and validate a domain's robots.txt, and check its referenced sitemaps.

Reuses utils.http_tools's connection/error-handling pattern (requests.get
with a custom User-Agent, SSLError/Timeout/ConnectionError/RequestException
handled distinctly). Sitemap validation is capped at 5 fetches to keep this
a bounded number of real network round trips.
"""

from __future__ import annotations

import time
from typing import Any
from xml.etree import ElementTree as ET

import requests

from utils.dns_tools import MAX_DOMAIN_LENGTH, normalize_domain
from utils.reliability import diagnostics

MAX_SITEMAPS_CHECKED = 5
RETRY_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 0.3
RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}
_KNOWN_DIRECTIVES = {"user-agent", "disallow", "allow", "sitemap", "crawl-delay", "host", "clean-param"}
_HEADERS = {"User-Agent": "ITOpsToolkit/1.0 public-safe-checker"}
_SITEMAP_ROOT_TAGS = {"urlset", "sitemapindex"}


def _parse_robots_txt(text: str) -> dict[str, Any]:
    issues: list[str] = []
    sitemaps: list[str] = []
    seen_user_agent = False

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            issues.append(f"Line {line_number}: no ':' separator -- not a valid directive.")
            continue

        directive, _, value = stripped.partition(":")
        directive_key = directive.strip().lower()
        value = value.strip()

        if directive_key not in _KNOWN_DIRECTIVES:
            issues.append(f"Line {line_number}: unrecognized directive '{directive.strip()}'.")
            continue

        if directive_key == "user-agent":
            seen_user_agent = True
        elif directive_key == "sitemap":
            sitemaps.append(value)
        elif directive_key in {"disallow", "allow", "crawl-delay"} and not seen_user_agent:
            issues.append(f"Line {line_number}: '{directive.strip()}' appears before any 'User-agent' directive.")

    return {"issues": issues, "sitemaps": sitemaps}


def _validate_sitemap(url: str) -> dict[str, Any]:
    response = None
    try:
        response = requests.get(url, headers=_HEADERS, timeout=10)
    except requests.exceptions.Timeout:
        return {"url": url, "ok": False, "detail": "Could not fetch: request timed out."}
    except requests.exceptions.SSLError:
        return {"url": url, "ok": False, "detail": "Could not fetch: TLS/SSL connection failed."}
    except requests.exceptions.ConnectionError:
        return {"url": url, "ok": False, "detail": "Could not fetch: connection failed."}
    except requests.exceptions.RequestException:
        return {"url": url, "ok": False, "detail": "Could not fetch: request failed."}

    try:
        if response.status_code >= 400:
            return {"url": url, "ok": False, "detail": f"HTTP {response.status_code}."}

        try:
            root = ET.fromstring(response.content)
        except ET.ParseError:
            return {"url": url, "ok": False, "detail": "Not well-formed XML."}

        root_tag = root.tag.rsplit("}", 1)[-1]  # strip XML namespace, if present
        if root_tag not in _SITEMAP_ROOT_TAGS:
            return {"url": url, "ok": False, "detail": "Unexpected XML root element."}

        return {"url": url, "ok": True, "detail": f"Valid <{root_tag}>."}
    finally:
        close = getattr(response, "close", None)
        if close:
            close()


def validate_robots_txt(domain: str) -> dict[str, Any]:
    """Fetch a domain's robots.txt, validate its syntax, and check its sitemaps."""
    normalized = normalize_domain(domain)
    result: dict[str, Any] = {
        "ok": False,
        "error": None,
        "domain": normalized,
        "issues": [],
        "sitemaps": [],
        **diagnostics(provider="robots"),
    }

    if not normalized:
        result["error"] = "Enter a domain name."
        return result
    if len(normalized) > MAX_DOMAIN_LENGTH:
        result["error"] = f"Domain is longer than {MAX_DOMAIN_LENGTH} characters."
        return result

    url = f"https://{normalized}/robots.txt"
    response = None
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        result["attempts"] = attempt
        try:
            response = requests.get(url, headers=_HEADERS, timeout=10)
            if response.status_code in RETRYABLE_STATUS_CODES and attempt < RETRY_ATTEMPTS:
                close = getattr(response, "close", None)
                if close:
                    close()
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            break
        except requests.exceptions.SSLError:
            result["error"] = "TLS/SSL error while connecting to robots.txt."
            result.update(diagnostics(error_code="tls_error", failure_mode="persistent", attempts=attempt))
            return result
        except requests.exceptions.Timeout:
            if attempt < RETRY_ATTEMPTS:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            result["error"] = "Request timed out."
            result.update(diagnostics(error_code="timeout", failure_mode="transient", attempts=attempt, retryable=True))
            return result
        except requests.exceptions.ConnectionError:
            if attempt < RETRY_ATTEMPTS:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            result["error"] = "Connection failed while reaching robots.txt."
            result.update(diagnostics(error_code="connection_error", failure_mode="transient", attempts=attempt, retryable=True))
            return result
        except requests.exceptions.RequestException:
            result["error"] = "Request failed before robots.txt was received."
            result.update(diagnostics(error_code="request_error", failure_mode="persistent", attempts=attempt))
            return result

    try:
        if response.status_code == 404:
            result["error"] = "No robots.txt found at this domain (404)."
            result.update(diagnostics(error_code="not_found", failure_mode="persistent", attempts=result["attempts"]))
            return result
        if response.status_code >= 400:
            result["error"] = f"Could not fetch robots.txt: HTTP {response.status_code}."
            result.update(diagnostics(error_code=f"http_{response.status_code}", failure_mode="transient" if response.status_code in RETRYABLE_STATUS_CODES else "persistent", attempts=result["attempts"], retryable=response.status_code in RETRYABLE_STATUS_CODES))
            return result

        parsed = _parse_robots_txt(response.text)
        sitemap_results = [
            _validate_sitemap(sitemap_url)
            for sitemap_url in parsed["sitemaps"][:MAX_SITEMAPS_CHECKED]
        ]

        result.update({"ok": True, "issues": parsed["issues"], "sitemaps": sitemap_results, **diagnostics(attempts=result["attempts"], provider="robots")})
        return result
    finally:
        close = getattr(response, "close", None)
        if close:
            close()
