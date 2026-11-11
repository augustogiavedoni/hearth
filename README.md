# hearth

A self-hosted, agent-based personal assistant written in Python.

> **Status: early.** This repository is a scaffold. Most modules are
> intentionally empty and will be written by hand as a learning project.
> Nothing here is usable yet.

## Goal

Run a small set of LLM-powered agents on a home server, each with a narrow
role and the minimum permissions it needs. The first agent reads Gmail
(read-only) and prepares **draft** replies. It never sends anything.

## Architecture

```
   Telegram (you)
        |
        v
+---------------+     +-----------------+     +--------------------+
|  interfaces/  |---->|   core/loop     |---->|  providers/router  |
|  telegram     |     |  (agent loop)   |     |  primary -> 429 -> |
+---------------+     +-----------------+     |  fallback          |
        ^                |         ^          +--------------------+
        |                v         |                   |
        |         +-------------+  |                   v
        +---------|  approval/  |  |          OpenAI-compatible API
     approve /    +-------------+  |
     reject              |         |
                         v         |
                  +--------------------+
                  | tools/ (allowlist  |
                  | per agent role)    |---> Gmail API (read + drafts)
                  +--------------------+
```

Each agent role is described in `agents/*.yaml`: system prompt, allowed
tools, which actions need human approval, and which model to use.
See [docs/architecture.md](docs/architecture.md).

## Security notice

This project handles personal email and API credentials. By design:

- The mail agent has **read-only** Gmail access plus draft creation. It
  cannot send, delete, or run shell commands.
- Email content is treated as **untrusted input** (prompt injection).
- Risky actions require explicit human approval.
- Secrets live only in a local `.env` (git-ignored); see `.env.example`.
- The container runs as a non-root user and publishes no ports.

Read [docs/threat-model.md](docs/threat-model.md) before deploying.
**Use at your own risk.** If you find a security issue, please open a
private security advisory instead of a public issue.

## Development

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pre-commit install
uv run pytest
```

## License

MIT. See [LICENSE](LICENSE).
