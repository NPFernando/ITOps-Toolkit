"""Public-safe log analysis and optional Azure AI summaries."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from utils.text_tools import MAX_LOG_LENGTH, validate_length


SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.I | re.S),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bASIA[0-9A-Z]{16}\b"),
    re.compile(r"\b[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"(?i)(password|passwd|pwd|secret|token|api[_-]?key|client[_-]?secret)\s*[:=]\s*['\"]?[^'\"\s]+"),
]

AZURE_OPENAI_REQUIRED_KEYS = (
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_DEPLOYMENT",
)
AZURE_OPENAI_OPTIONAL_KEYS = ("AZURE_OPENAI_API_VERSION",)

AZURE_AI_SYSTEM_INSTRUCTIONS = """You are helping an IT operations engineer troubleshoot sanitized logs.
Use only the supplied sanitized log text and rule-based findings.
Do not reproduce secrets, tokens, private keys, customer data, or long raw log excerpts.
If data is redacted, treat it as intentionally hidden.
Return a concise summary with likely cause, impact, and safe next steps."""


def sanitize_text(text: str) -> str:
    """Mask common secret shapes before any optional downstream processing."""
    sanitized = text or ""
    for pattern in SECRET_PATTERNS:
        sanitized = pattern.sub("[REDACTED]", sanitized)
    return sanitized


def _secret_value(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st

        return str(st.secrets.get(name, "") or "")
    except Exception:
        return ""


def azure_openai_config() -> dict[str, str]:
    """Return Azure OpenAI config values without logging or validating externally."""
    keys = (*AZURE_OPENAI_REQUIRED_KEYS, *AZURE_OPENAI_OPTIONAL_KEYS)
    return {key: _secret_value(key).strip() for key in keys}


def azure_openai_missing_keys() -> list[str]:
    config = azure_openai_config()
    return [key for key in AZURE_OPENAI_REQUIRED_KEYS if not config.get(key)]


def azure_openai_configured() -> bool:
    return not azure_openai_missing_keys()


def optional_ai_provider() -> str | None:
    """Return the configured AI provider name without exposing secrets."""
    if azure_openai_configured():
        return "azure_openai"
    return None


def optional_ai_configured() -> bool:
    """Return whether optional AI credentials exist without exposing them."""
    return optional_ai_provider() is not None


def _azure_openai_base_url(endpoint: str) -> str:
    normalized = (endpoint or "").strip().rstrip("/")
    if not normalized:
        return ""
    if normalized.endswith("/openai/v1"):
        return f"{normalized}/"
    if normalized.endswith("/openai"):
        return f"{normalized}/v1/"
    return f"{normalized}/openai/v1/"


def _default_azure_openai_client(api_key: str, base_url: str) -> Any:
    from openai import OpenAI

    return OpenAI(api_key=api_key, base_url=base_url, timeout=20.0)


def _safe_findings_summary(findings: list[dict[str, Any]] | None) -> list[dict[str, str]]:
    safe_findings = []
    for item in findings or []:
        safe_findings.append(
            {
                "severity": str(item.get("severity", "")),
                "likely_issue": str(item.get("likely_issue", "")),
                "possible_cause": str(item.get("possible_cause", "")),
            }
        )
    return safe_findings


def _response_output_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return str(output_text).strip()

    parts: list[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                parts.append(str(text))
    return "\n".join(parts).strip()


def summarize_logs_with_azure(
    sanitized_text: str,
    findings: list[dict[str, Any]] | None = None,
    client_factory: Any | None = None,
) -> dict[str, Any]:
    """Generate an optional Azure AI summary from sanitized logs only."""
    missing = azure_openai_missing_keys()
    if missing:
        return {
            "enabled": False,
            "provider": "azure_openai",
            "status": "unavailable",
            "message": "Azure AI summary unavailable until Azure OpenAI settings are configured.",
        }

    sanitized = (sanitized_text or "").strip()
    if not sanitized:
        return {
            "enabled": False,
            "provider": "azure_openai",
            "status": "unavailable",
            "message": "Azure AI summary unavailable because there is no sanitized log text to summarize.",
        }

    ok, error = validate_length(sanitized, MAX_LOG_LENGTH, "Sanitized log text")
    if not ok:
        return {
            "enabled": False,
            "provider": "azure_openai",
            "status": "error",
            "message": error,
        }

    input_text = "\n\n".join(
        [
            "Rule-based findings:",
            json.dumps(_safe_findings_summary(findings), ensure_ascii=False),
            "Sanitized logs:",
            sanitized,
        ]
    )

    try:
        config = azure_openai_config()
        client_builder = client_factory or _default_azure_openai_client
        client = client_builder(
            api_key=config["AZURE_OPENAI_API_KEY"],
            base_url=_azure_openai_base_url(config["AZURE_OPENAI_ENDPOINT"]),
        )
        response = client.responses.create(
            model=config["AZURE_OPENAI_DEPLOYMENT"],
            instructions=AZURE_AI_SYSTEM_INSTRUCTIONS,
            input=input_text,
            max_output_tokens=500,
        )
        summary = _response_output_text(response)
    except Exception as exc:
        return {
            "enabled": False,
            "provider": "azure_openai",
            "status": "error",
            "message": "Azure AI summary could not be generated. Rule-based results are still available.",
            "error_type": type(exc).__name__,
        }

    if not summary:
        return {
            "enabled": False,
            "provider": "azure_openai",
            "status": "error",
            "message": "Azure AI summary returned no text. Rule-based results are still available.",
        }

    return {
        "enabled": True,
        "provider": "azure_openai",
        "status": "success",
        "message": "Azure AI summary generated from sanitized log text only.",
        "summary": summary,
    }


def optional_ai_summary(
    sanitized_text: str,
    findings: list[dict[str, Any]] | None = None,
    opted_in: bool = False,
    client_factory: Any | None = None,
) -> dict[str, Any]:
    """Return optional Azure AI summary state without direct OpenAI support."""
    if not optional_ai_configured():
        return {
            "enabled": False,
            "provider": None,
            "status": "unavailable",
            "message": "No Azure AI settings configured. Rule-based analysis only.",
        }
    if not opted_in:
        return {
            "enabled": False,
            "provider": "azure_openai",
            "status": "skipped",
            "message": "Azure AI summary skipped. Check the opt-in box to send sanitized logs for this submission.",
        }
    return summarize_logs_with_azure(sanitized_text, findings=findings, client_factory=client_factory)


def _finding(issue: str, cause: str, commands: list[str], steps: list[str], severity: str = "Warning") -> dict[str, Any]:
    return {
        "severity": severity,
        "likely_issue": issue,
        "possible_cause": cause,
        "commands_to_check": commands,
        "safe_next_steps": steps,
    }


def analyze_logs_rule_based(text: str) -> dict[str, Any]:
    """Detect common operational failure patterns without external calls."""
    ok, error = validate_length(text, MAX_LOG_LENGTH, "Log text")
    if not ok:
        return {"ok": False, "error": error, "findings": [], "sanitized": ""}

    sanitized = sanitize_text(text)
    haystack = sanitized.lower()
    findings: list[dict[str, Any]] = []

    checks: list[tuple[bool, dict[str, Any]]] = [
        (
            any(term in haystack for term in ["certificate verify failed", "ssl certificate", "x509", "certificate has expired"]),
            _finding(
                "SSL certificate error",
                "The certificate may be expired, untrusted, self-signed, or issued for a different hostname.",
                ["openssl s_client -connect example.com:443 -servername example.com", "curl -Iv https://example.com"],
                ["Check certificate validity dates, SAN names, and intermediate chain.", "Renew or replace the certificate if needed."],
                "Critical",
            ),
        ),
        (
            any(term in haystack for term in ["nxdomain", "temporary failure in name resolution", "could not resolve host", "name or service not known"]),
            _finding(
                "DNS resolution failure",
                "The hostname may not exist, nameservers may be failing, or the runtime DNS resolver may be unavailable.",
                ["dig example.com", "nslookup example.com", "resolvectl status"],
                ["Confirm the hostname is correct.", "Check authoritative DNS records and local resolver health."],
                "Critical",
            ),
        ),
        (
            "connection refused" in haystack or "errno 111" in haystack,
            _finding(
                "Connection refused",
                "The host is reachable, but nothing is listening on the target port or a firewall rejected the connection.",
                ["ss -tulpn", "curl -v http://host:port", "systemctl status service-name"],
                ["Verify the service is running.", "Confirm listener port, container port mapping, and firewall rules."],
                "Critical",
            ),
        ),
        (
            "timed out" in haystack or "timeout" in haystack or "etimedout" in haystack,
            _finding(
                "Timeout",
                "The request exceeded its time limit because of network path, firewall, DNS, upstream, or application latency.",
                ["curl -v --max-time 10 https://example.com", "traceroute example.com", "mtr example.com"],
                ["Check recent latency, firewall changes, and upstream service health.", "Increase timeout only after confirming the service is healthy."],
            ),
        ),
        (
            any(code in haystack for code in [" 502 ", "http 502", "status 502", "bad gateway"]),
            _finding(
                "HTTP 502 Bad Gateway",
                "A proxy or gateway could not get a valid response from the upstream service.",
                ["curl -Iv https://example.com", "systemctl status nginx", "docker ps"],
                ["Check upstream service health.", "Review proxy upstream configuration and recent deploys."],
                "Critical",
            ),
        ),
        (
            any(code in haystack for code in [" 503 ", "http 503", "status 503", "service unavailable"]),
            _finding(
                "HTTP 503 Service Unavailable",
                "The service may be overloaded, down for maintenance, or failing health checks.",
                ["curl -Iv https://example.com", "kubectl get pods", "systemctl status service-name"],
                ["Check service capacity and health checks.", "Review recent deploys and autoscaling events."],
                "Critical",
            ),
        ),
        (
            any(code in haystack for code in [" 504 ", "http 504", "status 504", "gateway timeout"]),
            _finding(
                "HTTP 504 Gateway Timeout",
                "A gateway waited too long for an upstream response.",
                ["curl -v https://example.com", "kubectl logs deployment/name", "systemctl status service-name"],
                ["Check slow upstream dependencies.", "Review database, queue, or API latency."],
                "Critical",
            ),
        ),
        (
            "no such container" in haystack or "container not found" in haystack,
            _finding(
                "Docker container not found",
                "The command references a container name or ID that does not exist on this host.",
                ["docker ps -a", "docker compose ps"],
                ["Confirm the container name.", "Check whether the compose project or deployment recreated the container."],
            ),
        ),
        (
            "host not found in upstream" in haystack or "nginx" in haystack and "upstream" in haystack and "not found" in haystack,
            _finding(
                "NGINX upstream host not found",
                "NGINX could not resolve an upstream hostname at startup or reload time.",
                ["nginx -t", "docker compose ps", "getent hosts upstream-name"],
                ["Confirm the upstream hostname exists in DNS or Docker network DNS.", "Reload NGINX after fixing name resolution."],
                "Critical",
            ),
        ),
        (
            "aadsts50011" in haystack or "redirect uri" in haystack and "mismatch" in haystack,
            _finding(
                "Azure AD redirect URI mismatch",
                "The application sent a redirect URI that is not registered for the Azure app registration.",
                ["az ad app show --id <app-id>", "Check the app registration Authentication blade"],
                ["Add the exact redirect URI to the app registration.", "Confirm scheme, host, path, and trailing slash match exactly."],
            ),
        ),
        (
            "accessdenied" in haystack or "access denied" in haystack and ("aws" in haystack or "s3" in haystack or "iam" in haystack),
            _finding(
                "AWS access denied",
                "The current IAM identity does not have permission for the attempted AWS action or resource.",
                ["aws sts get-caller-identity", "aws iam simulate-principal-policy --help"],
                ["Identify the caller identity.", "Review IAM policy, resource policy, permission boundary, and SCP restrictions."],
                "Critical",
            ),
        ),
        (
            "jsondecodeerror" in haystack or "unexpected token" in haystack or "invalid json" in haystack,
            _finding(
                "JSON parse error",
                "The input is not valid JSON or the service returned non-JSON content where JSON was expected.",
                ["python -m json.tool file.json", "curl -i https://example.com/api"],
                ["Validate the JSON syntax.", "Check whether the upstream returned HTML, an error page, or an empty response."],
            ),
        ),
    ]

    for matched, finding in checks:
        if matched:
            findings.append(finding)

    if not findings:
        findings.append(
            _finding(
                "No known pattern detected",
                "The log text did not match the built-in troubleshooting rules.",
                ["Check service-specific logs", "Review recent deploys or config changes"],
                ["Search for the first error in the stack trace.", "Correlate timestamps with deployments, restarts, and dependency incidents."],
                "Unknown",
            )
        )

    return {"ok": True, "error": None, "findings": findings, "sanitized": sanitized}
