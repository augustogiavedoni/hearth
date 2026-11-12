"""Provider interface.

Responsibility:
    Define the contract every model backend implements, so the agent loop
    does not depend on a specific vendor.

Must NOT:
    - Contain vendor-specific code or HTTP calls.
    - Hold or load credentials.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Protocol


@dataclass(frozen=True)
class Message:
    role: Literal["user", "assistant", "system"]
    content: str


@dataclass(frozen=True)
class Response:
    content: str
    finish_reason: Literal["stop", "length", "other"]


class Provider(Protocol):
    async def complete(self, messages: Sequence[Message]) -> Response: ...


class ProviderError(Exception):
    """Base class for provider errors."""


class ProviderTimeoutError(ProviderError):
    """The request timed out."""


class ProviderAuthenticationError(ProviderError):
    """The request is not authenticated."""


class ProviderRateLimitError(ProviderError):
    """The request is limited by the provider."""


class ProviderInvalidRequestError(ProviderError):
    """The request is malformed or the provider does not support the request."""


class ProviderUnavailableError(ProviderError):
    """Either the provider is down or the network is unreachable."""


class AllProvidersFailedError(ProviderError):
    """All providers failed to complete the request."""

    def __init__(self, errors: Sequence[Exception]) -> None:
        self.errors = tuple(errors)

        super().__init__(
            f"All providers failed: {', '.join(type(error).__name__ for error in errors)}"
        )
