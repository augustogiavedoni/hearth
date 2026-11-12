import pytest

from hearth.providers.base import (
    ProviderAuthenticationError,
    ProviderError,
    ProviderInvalidRequestError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from hearth.providers.router import ProviderAction, action_for


@pytest.mark.parametrize(
    "exception, expected_action",
    [
        pytest.param(
            ProviderTimeoutError(), ProviderAction.RETRY_THEN_FALLBACK, id="timeout-retry-fallback"
        ),
        pytest.param(
            ProviderUnavailableError(),
            ProviderAction.RETRY_THEN_FALLBACK,
            id="unavailable-retry-fallback",
        ),
        pytest.param(ProviderRateLimitError(), ProviderAction.FALLBACK, id="rate_limit-fallback"),
        pytest.param(ProviderAuthenticationError(), ProviderAction.FAIL, id="authentication-fail"),
        pytest.param(ProviderInvalidRequestError(), ProviderAction.FAIL, id="invalid_request-fail"),
        pytest.param(ValueError(), ProviderAction.FAIL, id="non_provider_error-fail"),
        pytest.param(ProviderError(), ProviderAction.FAIL, id="generic_provider_error-fail"),
    ],
)
def test_action_for(exception: Exception, expected_action: ProviderAction) -> None:
    assert action_for(exception) is expected_action
