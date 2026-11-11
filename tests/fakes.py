from collections.abc import Sequence

from hearth.providers.base import Message, Provider, ProviderError, Response


class FakeProvider(Provider):
    def __init__(self, responses: Sequence[Response | ProviderError]):
        self.responses = list(responses)
        self.calls: list[Sequence[Message]] = []

    async def complete(self, messages: Sequence[Message]) -> Response:
        self.calls.append(list(messages))

        if not self.responses:
            raise ValueError("There are no responses to complete.")

        response = self.responses.pop(0)

        if isinstance(response, ProviderError):
            raise response

        return response


_: Provider = FakeProvider([])
