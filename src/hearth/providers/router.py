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
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from enum import Enum, auto

from hearth.providers.base import (
    Message,
    Provider,
    ProviderAuthenticationError,
    ProviderInvalidRequestError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    Response,
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


class Router:
    def __init__(
        self,
        providers: Sequence[Provider],
        retry_config: RetryConfig,
        sleep: Callable[[float], Awaitable[None]],
    ) -> None:
        if not providers:
            raise ValueError("providers cannot be empty")

        self._providers = tuple(providers)
        self._retry_config = retry_config
        self._sleep = sleep

    async def complete(self, messages: Sequence[Message]) -> Response:
        last_exception: Exception | None = None

        for provider in self._providers:
            try:
                return await provider.complete(messages)
            except Exception as exception:
                last_exception = exception
                action = action_for(exception)

                match action:
                    case ProviderAction.FALLBACK:
                        continue
                    case ProviderAction.FAIL | ProviderAction.RETRY_THEN_FALLBACK:
                        raise exception

        if last_exception is not None:
            raise last_exception
        else:
            raise RuntimeError(
                "Router has no providers; the constructor should have rejected this."
            )
