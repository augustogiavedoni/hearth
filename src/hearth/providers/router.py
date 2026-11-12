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

import math
from dataclasses import dataclass
from enum import Enum, auto

from hearth.providers.base import (
    ProviderAuthenticationError,
    ProviderInvalidRequestError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)

# TODO(augusto): implement routing and fallback on 429


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


@dataclass(frozen=True)
class RetryConfig:
    base_delay: float = 1.0
    max_delay: float = 10.0
    factor: float = 2.0

    def __post_init__(self) -> None:
        if self.base_delay <= 0 or not math.isfinite(self.base_delay):
            raise ValueError(f"base_delay must be a finite positive number (got {self.base_delay})")
        if self.max_delay < self.base_delay or not math.isfinite(self.max_delay):
            raise ValueError(
                "max_delay must be a finite positive number greater than "
                f"or equal to base_delay (got {self.max_delay}, base_delay={self.base_delay})"
            )
        if self.factor < 1 or not math.isfinite(self.factor):
            raise ValueError(
                f"factor must be a finite positive number at least 1 (got {self.factor})"
            )


def calculate_retry_delay(config: RetryConfig, retry_attempt: int) -> float:
    """Return the delay before a retry; retry 1 waits base_delay."""
    if retry_attempt < 1:
        raise ValueError(f"retry_attempt must be at least 1 (got {retry_attempt})")

    try:
        delay = config.base_delay * (config.factor ** (retry_attempt - 1))
    except OverflowError:
        delay = config.max_delay

    return min(delay, config.max_delay)
