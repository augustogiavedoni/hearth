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

from enum import Enum, auto

from hearth.providers.base import (
    ProviderAuthenticationError,
    ProviderInvalidRequestError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)


class ProviderAction(Enum):
    RETRY_THEN_FALLBACK = auto()
    FALLBACK = auto()
    FAIL = auto()


def action_for(exception: Exception) -> ProviderAction:
    match exception:
        case ProviderTimeoutError() | ProviderUnavailableError():
            return ProviderAction.RETRY_THEN_FALLBACK
        case ProviderRateLimitError():
            return ProviderAction.FALLBACK
        case ProviderAuthenticationError() | ProviderInvalidRequestError():
            return ProviderAction.FAIL
        # Fail closed: an unknown error is likely a bug; surface it instead of hiding it behind a
        # fallback that sends the request to another provider.
        case _:
            return ProviderAction.FAIL
