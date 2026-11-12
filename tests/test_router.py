import dataclasses
from typing import Any

import pytest

from fakes import FakeProvider, FakeSleep
from hearth.providers.base import (
    Message,
    ProviderAuthenticationError,
    ProviderError,
    ProviderInvalidRequestError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    Response,
)
from hearth.providers.router import (
    ProviderAction,
    RetryConfig,
    Router,
    action_for,
    calculate_retry_delay,
)


async def no_sleep(delay: float) -> None:
    pass


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


@pytest.mark.parametrize(
    "config, retry_attempt, expected_delay",
    [
        pytest.param(RetryConfig(), 1, 1.0, id="first_retry-one_second_delay"),
        pytest.param(RetryConfig(), 2, 2.0, id="second_retry-two_second_delay"),
        pytest.param(RetryConfig(), 3, 4.0, id="third_retry-four_second_delay"),
        pytest.param(RetryConfig(), 4, 8.0, id="fourth_retry-eight_second_delay"),
        pytest.param(RetryConfig(), 5, 10.0, id="power_overflow-capped_at_max_delay"),
        pytest.param(RetryConfig(), 2000, 10.0, id="product_inf-capped_at_max_delay"),
        pytest.param(
            RetryConfig(base_delay=10.0, max_delay=1e308),
            1024,
            1e308,
            id="large_delay-capped_at_max_delay",
        ),
    ],
)
def test_retry_delay_calculation(
    config: RetryConfig, retry_attempt: int, expected_delay: float
) -> None:
    assert calculate_retry_delay(config, retry_attempt) == expected_delay


@pytest.mark.parametrize(
    "retry_attempt",
    [
        pytest.param(0, id="zero_retry_attempt"),
        pytest.param(-1, id="negative_retry_attempt"),
    ],
)
def test_calculate_retry_delay_invalid_retry_attempt(retry_attempt: int) -> None:
    with pytest.raises(ValueError):
        calculate_retry_delay(RetryConfig(), retry_attempt)


def test_retry_config_default_values() -> None:
    config = RetryConfig()

    assert dataclasses.asdict(config) == {
        "base_delay": 1.0,
        "max_delay": 10.0,
        "factor": 2.0,
        "max_retries": 3,
    }


@pytest.mark.parametrize(
    "values",
    [
        pytest.param(
            {"base_delay": 0.5, "max_delay": 0.5, "factor": 2.0, "max_retries": 3},
            id="max_delay_equal_to_base_delay",
        ),
        pytest.param(
            {"base_delay": 1.0, "max_delay": 10.0, "factor": 1.0, "max_retries": 3},
            id="factor_one",
        ),
        pytest.param(
            {"base_delay": 1.0, "max_delay": 10.0, "factor": 2.0, "max_retries": 0},
            id="max_retries_zero",
        ),
    ],
)
def test_retry_config_valid_values(values: dict[str, Any]) -> None:
    config = RetryConfig(**values)

    assert dataclasses.asdict(config) == values


@pytest.mark.parametrize(
    "values, wrong_attribute",
    [
        pytest.param({"base_delay": 0.0}, "base_delay", id="base_delay_zero"),
        pytest.param(
            {"base_delay": 5.0, "max_delay": 2.0}, "max_delay", id="max_delay_less_than_base_delay"
        ),
        pytest.param({"factor": 0.9}, "factor", id="factor_less_than_one"),
        pytest.param({"base_delay": float("nan")}, "base_delay", id="base_delay_nan"),
        pytest.param({"max_retries": -1}, "max_retries", id="max_retries_negative"),
    ],
)
def test_retry_config_invalid_values(values: dict[str, Any], wrong_attribute: str) -> None:
    with pytest.raises(ValueError, match=f"^{wrong_attribute}"):
        RetryConfig(**values)


async def test_router_returns_first_provider_response() -> None:
    expected = Response(content="Hi! How can I help you?", finish_reason="stop")
    provider = FakeProvider([expected])
    router = Router(providers=[provider], retry_config=RetryConfig(), sleep=no_sleep)
    message = Message(role="user", content="Hi there!")

    result = await router.complete([message])

    assert result is expected
    assert provider.calls == [[message]]


async def test_router_fallback_on_rate_limit_without_retry_or_sleep() -> None:
    primary = FakeProvider([ProviderRateLimitError()])
    expected = Response(content="Hi! How can I help you?", finish_reason="stop")
    secondary = FakeProvider([expected])
    sleep = FakeSleep()
    router = Router(providers=[primary, secondary], retry_config=RetryConfig(), sleep=sleep)
    message = Message(role="user", content="Hi there!")

    result = await router.complete([message])

    assert result is expected
    assert primary.calls == [[message]]
    assert secondary.calls == [[message]]
    assert sleep.delays == []


@pytest.mark.parametrize(
    "exception",
    [
        pytest.param(ProviderAuthenticationError(), id="authentication-error"),
        pytest.param(ProviderInvalidRequestError(), id="invalid-request-error"),
        pytest.param(ProviderError(), id="generic-error"),
    ],
)
async def test_router_raises_without_fallback_on_non_transient_error(
    exception: ProviderError,
) -> None:
    primary = FakeProvider([exception])
    secondary = FakeProvider([Response(content="Hi! How can I help you?", finish_reason="stop")])
    sleep = FakeSleep()
    router = Router(providers=[primary, secondary], retry_config=RetryConfig(), sleep=sleep)
    message = Message(role="user", content="Hi there!")

    with pytest.raises(type(exception)) as exception_info:
        await router.complete([message])

    assert exception_info.value is exception
    assert primary.calls == [[message]]
    assert secondary.calls == []
    assert sleep.delays == []


@pytest.mark.parametrize(
    "exception",
    [
        pytest.param(ProviderTimeoutError(), id="timeout-error"),
        pytest.param(ProviderUnavailableError(), id="unavailable-error"),
    ],
)
async def test_router_falls_back_after_exhausting_retries(exception: ProviderError) -> None:
    primary = FakeProvider([exception for _ in range(4)])
    expected = Response(content="Hi! How can I help you?", finish_reason="stop")
    secondary = FakeProvider([expected])
    sleep = FakeSleep()
    router = Router(
        providers=[primary, secondary], retry_config=RetryConfig(max_retries=3), sleep=sleep
    )
    message = Message(role="user", content="Hi there!")

    result = await router.complete([message])

    assert result is expected
    assert len(primary.calls) == 4
    assert secondary.calls == [[message]]
    assert sleep.delays == [1.0, 2.0, 4.0]
