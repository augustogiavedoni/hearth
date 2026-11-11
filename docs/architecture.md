# Architecture

> Draft. Will change as milestones land (see [roadmap](roadmap.md)).

## Components

| Component | Path | Responsibility |
|---|---|---|
| Config | `src/hearth/config.py` | Load settings from env and agent YAML; validate with pydantic. |
| Agent loop | `src/hearth/core/loop.py` | Send messages to the model, execute requested tool calls, feed results back, stop on a final answer or a step limit. |
| Provider interface | `src/hearth/providers/base.py` | The contract every model backend implements. |
| OpenAI-compatible provider | `src/hearth/providers/openai_compat.py` | One implementation for any endpoint that speaks the OpenAI chat API. |
| Router | `src/hearth/providers/router.py` | Pick a provider; fall back to the next one on HTTP 429 (rate limit / quota). |
| Tool interface | `src/hearth/tools/base.py` | The contract every tool implements: name, schema, risk level. |
| Gmail tools | `src/hearth/tools/gmail.py` | List and read messages, create drafts. Never send. |
| Approval | `src/hearth/approval/` | Hold risky actions until a human approves or rejects them. |
| Telegram interface | `src/hearth/interfaces/telegram.py` | Talk to the user, deliver approval requests, accept replies from allowed user IDs only. |
| Agent roles | `agents/*.yaml` | Per-role prompt, tool allowlist, approval policy, model. |

## Flow of one call (mail agent, target design)

1. A trigger (Telegram command or schedule) starts the mail agent.
2. `config` loads `agents/mail.yaml`; only the tools listed there are
   registered for this run.
3. `core/loop` sends the system prompt and the task to the `router`.
4. The `router` calls the primary provider. On 429 it retries with the
   fallback provider.
5. The model asks for a tool call, e.g. `gmail.list`. The loop checks the
   tool is in the allowlist, validates arguments, and executes it.
6. Tool output (email content: **untrusted**) is returned to the model,
   clearly delimited as data.
7. The model asks for `gmail.create_draft`. Because the role marks it as
   requiring approval, the loop hands it to `approval/` instead of running
   it.
8. `approval/` sends a summary to Telegram. The user approves or rejects.
9. On approval, the draft is created in Gmail. The user sends it manually
   from Gmail if they want to.
10. The loop ends on a final answer or when it hits the step limit.
