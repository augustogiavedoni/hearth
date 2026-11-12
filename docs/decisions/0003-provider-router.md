# ADR 0003: Provider router — composite provider, pure policy, injected sleep

- Status: accepted
- Date: 2026-11-12

## Context

ADR 0002 defines the provider interface and the error policy (rate limit →
fall back; timeout/unavailable → retry with backoff, then fall back;
authentication/invalid request → fail). It leaves open how the router is
shaped, what happens with errors outside that table, how backoff is
configured and tested, and what the router raises when every provider
fails. The M1 criterion "falls back on HTTP 429" must be provable with fakes
and without real waiting.

## Decision

1. **The router is itself a `Provider`.** `Router.complete` has the same
   signature as the Protocol, so the REPL (and the agent loop in M2) receive
   "a provider" and do not know whether one or several are behind it. The
   router receives its providers already built and stores them as a tuple,
   so the list cannot change after construction. An empty list is rejected.
2. **The policy is a pure function.** `action_for(exception)` maps an error
   to a `ProviderAction` (`RETRY_THEN_FALLBACK`, `FALLBACK`, `FAIL`). The
   loop asks it what to do after every failed call, including retries, so a
   429 during a retry falls back and an authentication error during a retry
   fails. `router.py` imports only from `base.py`.
3. **Unknown errors fail closed.** Any error not in the ADR 0002 table
   (a bare `ProviderError`, or a non-provider exception such as a bug in an
   adapter) is raised immediately. Falling back would hide bugs and send the
   request to another provider for a reason nobody understood.
4. **Backoff is exponential with a cap, configured by a frozen
   `RetryConfig`.** `delay(n) = min(base_delay × factor^(n-1), max_delay)`,
   where retry 1 waits `base_delay`. Defaults: 1 s base, factor 2, 10 s cap,
   3 retries (4 calls per provider). `__post_init__` rejects invalid values
   (non-finite or non-positive base, cap below base, factor below 1,
   negative retries), so an invalid configuration cannot exist.
   `max_retries=0` is valid and disables retries. Overflow on large retry
   numbers returns the cap. No jitter: hearth has a single user, so there is
   no thundering herd to spread out.
5. **Waits only happen before a retry.** A fallback (after a 429 or after
   the last retry) never waits.
6. **The wait function is injected.** The router receives
   `sleep: Callable[[float], Awaitable[None]]` (`asyncio.sleep` in
   production). Tests pass a `FakeSleep` that records the delays, so they run
   instantly and can assert the exact sequence.
7. **When every provider fails, the router raises
   `AllProvidersFailedError`** (in `base.py`, subclass of `ProviderError`).
   It keeps one error per provider, in order (the one that made the router
   move on), and is chained from the last one. We rejected re-raising the
   last error (it hides what happened to the other providers) and
   `ExceptionGroup` (it is not a `ProviderError`, so callers that catch
   `ProviderError` would miss it and the router would stop being
   interchangeable with a single provider).

## Consequences

- Positive: the policy, the backoff and the loop are tested separately; the
  M1 fallback criterion is proved by a test with fakes and no real waiting;
  callers handle one error family whatever the number of providers.
- Negative: worst-case latency is dominated by provider timeouts, not by
  backoff (4 calls × the HTTP timeout per provider with the defaults);
  callers that want a specific error type after a full failure must look
  inside `AllProvidersFailedError.errors`.
- Revisit if: a provider sends `Retry-After` and we want to honour it; more
  than one user shares the providers (add jitter); the loop in M2 needs to
  know which provider answered (`Response` has no field for it).
