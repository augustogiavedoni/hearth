# ADR 0002: Provider interface — own types, Protocol, async, typed errors

- Status: accepted
- Date: 2026-11-11

## Context

M1 needs a provider interface (`src/hearth/providers/base.py`) so the agent
loop and the router do not depend on a specific vendor (ADR 0001). The
router must fall back to another provider on HTTP 429, and that behaviour
must be testable without network access. M5 (Telegram) will need the bot to
keep handling messages while a model call is in flight.

## Decision

1. **Own message and response types, as frozen dataclasses.** `Message`
   (`role`, `content`) and `Response` (`content`, `finish_reason`) are
   defined in `base.py`. We do not expose the `openai` SDK types, which
   would tie the loop to one vendor and make fakes hard to build. We do not
   use pydantic here: these objects are built by our own code and checked by
   mypy, so runtime validation adds nothing. Pydantic stays at the
   boundaries where untrusted input enters (env, YAML). `frozen=True` keeps
   sent messages from being changed after the fact.
2. **`finish_reason` is `Literal["stop", "length", "other"]`.** The adapter
   (`openai_compat.py`) maps any value it does not know to `"other"`. A new
   value is added only when the loop has to react differently to it (e.g.
   tool calls in M2).
3. **The interface is a `typing.Protocol`, not an ABC.** Implementations
   match by shape, not by inheritance, so test fakes need no base class.
   There is no shared implementation that would justify an ABC. The single
   method takes `Sequence[Message]` (read-only) so a provider cannot change
   the caller's history.
4. **Async from M1.** `complete` is `async def`. Async spreads to every
   caller (router, loop, REPL), so switching later would touch all of them
   and their tests. Tests run with `pytest-asyncio` in `auto` mode.
5. **Errors are our own exception hierarchy, named by cause.**
   `ProviderError` with `ProviderRateLimitError`, `ProviderTimeoutError`,
   `ProviderUnavailableError` (5xx or network unreachable),
   `ProviderAuthenticationError` and `ProviderInvalidRequestError`. Adapters
   translate SDK exceptions into these; the router never imports a vendor
   SDK. Policy lives in the router, not in the error types or the provider:
   - rate limit → fall back to the next provider;
   - timeout, unavailable → a few retries with increasing backoff, then fall
     back;
   - authentication, invalid request → fail immediately, no retry, no
     fallback (configuration or request problems must surface, not be
     hidden).

   Providers never retry on their own, so retries do not multiply.

Out of scope for M1: streaming and tool calls (M2).

## Consequences

- Positive: the loop and router are vendor-neutral; a scripted
  `FakeProvider` (`tests/fakes.py`) can simulate any response or error, so
  the 429 fallback is testable without network; immutability and read-only
  parameters rule out a class of history-corruption bugs.
- Negative: each adapter must map SDK responses and exceptions by hand;
  async adds a test plugin and some learning cost now; `"other"` hides which
  unexpected `finish_reason` arrived unless the adapter logs it.
- Note: the fallback policy goes beyond the M1 roadmap item (429 only) by
  also falling back after retries on timeout and unavailability.
- Revisit if: tool calls in M2 need a message shape that a single
  `Message` class cannot express cleanly (consider one class per role), or
  a 429 for exhausted quota needs to be told apart from a transient rate
  limit.
