# Adapter reliability contract

Network-backed tools return public-safe results. They do not expose upstream
exception text, request payloads, credentials, or response bodies unless the
tool explicitly documents that preview as safe.

The shared diagnostic fields are additive and may be absent in older cached
results:

| Field | Meaning |
| --- | --- |
| `error_code` | Stable, low-cardinality classification such as `timeout`, `rate_limited`, or `http_503`. |
| `failure_mode` | `healthy`, `transient`, or `persistent`. |
| `attempts` | Number of network attempts made, including the final attempt. |
| `retryable` | Whether a caller can reasonably retry the operation. |

Adapters use bounded retries for timeouts, connection failures, rate limits,
and common upstream 5xx responses. Every response object is closed after it is
consumed or abandoned. A provider outage produces a readable fallback or
error state instead of a raw traceback.

When extending an adapter:

1. Preserve existing result keys and add diagnostics rather than replacing the
   result envelope.
2. Use public-safe, actionable error text.
3. Keep retry counts bounded and close responses on every path.
4. Add a contract test for success, retryable failure, permanent failure, and
   response cleanup.
