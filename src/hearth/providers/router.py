"""Provider router.

Responsibility:
    Choose which provider serves a request and fall back to the next one
    when a provider returns HTTP 429 (rate limit or quota exhausted), with
    bounded retries and backoff.

Must NOT:
    - Retry forever or without backoff.
    - Fall back on errors that are not transient (e.g. auth, bad request).
    - Silently send data to a provider not present in configuration.
"""

# TODO(augusto): implement routing and fallback on 429.
