import pytest

from fakes import FakeProvider
from hearth.providers.base import Message, ProviderTimeoutError, Response


async def test_fake_provider_completes() -> None:
    provider = FakeProvider(
        [
            Response(content="Hi! How can I help you?", finish_reason="stop"),
            Response(content="I'm doing great, thank you!", finish_reason="stop"),
        ]
    )

    response = await provider.complete([Message(role="user", content="Hello, world!")])

    assert response.content == "Hi! How can I help you?"

    response = await provider.complete([Message(role="user", content="How are you?")])

    assert response.content == "I'm doing great, thank you!"


async def test_fake_provider_throws() -> None:
    provider = FakeProvider([ProviderTimeoutError()])

    with pytest.raises(ProviderTimeoutError):
        await provider.complete([])


async def test_fake_provider_calls() -> None:
    provider = FakeProvider([Response(content="Hi! How can I help you?", finish_reason="stop")])
    messages = [Message(role="user", content="Hello, world!")]

    await provider.complete(messages)

    # We modify the messages list, but the provider sees the original list.
    messages.append(Message(role="system", content="You're a helpful assistant."))

    assert provider.calls == [[Message(role="user", content="Hello, world!")]]


async def test_fake_empty_provider() -> None:
    provider = FakeProvider([])

    with pytest.raises(ValueError):
        await provider.complete([])
