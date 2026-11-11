# ADR 0001: Python, swappable OpenAI-compatible provider, read-only + drafts

- Status: accepted
- Date: 2026-11-10

## Context

hearth is a personal, self-hosted assistant built partly as a learning
project. It will process private email on a home server, and the repository
is public. We need to choose a language, a way to talk to LLMs, and the
permission level of the first agent.

## Decision

1. **Python 3.12+**, managed with `uv`. Mature LLM and Google API
   libraries, fast iteration, and strong typing via mypy strict.
2. **One provider interface, OpenAI-compatible API as the wire format.**
   Most hosted and local model servers expose it, so switching provider is
   a configuration change (base URL, key, model). A router adds fallback on
   HTTP 429. No agent framework for now: the loop is written by hand to
   learn how it works.
3. **The mail agent is read-only plus drafts.** It can list and read
   messages and create drafts. It cannot send, delete or forward, and drafts
   require human approval.

## Consequences

- Positive: small dependency surface; provider lock-in avoided; the worst
  outcome of a prompt injection is an unwanted draft that a human rejects.
- Negative: features specific to one provider (e.g. non-standard tool
  formats) are not used; replies must be sent manually from Gmail; the
  hand-written loop will lack features a framework would provide.
- Revisit if: a needed provider stops supporting the OpenAI-compatible API,
  or the loop grows enough that a framework becomes cheaper than our own.
