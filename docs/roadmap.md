# Roadmap

Each milestone is done only when its acceptance criteria pass and the
threat model has been reviewed for it.

This file is the source of truth. Each milestone has a matching
[GitHub milestone](https://github.com/augustogiavedoni/hearth/milestones),
and the work toward each criterion is tracked as an issue in it.

## M1 — Provider + minimal CLI chat
- [ ] `uv run python -m hearth` (or similar) starts a REPL that sends user
      input to the configured OpenAI-compatible provider and prints replies.
- [ ] Provider settings come from env; no secrets in code.
- [x] Router falls back to the secondary provider on HTTP 429 (proved by a
      test with a fake provider).
- [ ] Unit tests for the provider interface use fakes, no network.

## M2 — Agent loop with a toy tool
- [ ] Loop executes tool calls requested by the model and returns results.
- [ ] A toy tool (e.g. `clock.now`) is callable only if listed in the role
      YAML; an unlisted tool call is refused and reported.
- [ ] Hard step limit stops the loop; covered by a test.

## M3 — Gmail read-only
- [ ] OAuth with read-only scope; token stored outside git.
- [ ] `gmail.list` and `gmail.read` tools work against a real mailbox.
- [ ] Email bodies are delimited as untrusted data in the model context.
- [ ] Tests use recorded/fake responses only, no real mail in the repo.

## M4 — Drafts with approval
- [ ] Scope extended to compose (drafts) only; no send scope.
- [ ] `gmail.create_draft` is never executed without an approval.
- [ ] Approval shows recipient, subject and full body; reject discards it.
- [ ] Prompt-injection test: an email asking to send/forward produces no
      side effect beyond a pending approval.

## M5 — Telegram
- [ ] Bot answers only allowlisted user IDs.
- [ ] Approvals delivered and answered via Telegram.
- [ ] Pending approvals expire.

## M6 — Docker deployment
- [ ] Image builds in CI; runs as non-root with read-only root filesystem.
- [ ] No published ports; works behind Tailscale only.
- [ ] Secrets injected at runtime via env file, not baked into the image.
- [ ] Restart keeps state in `data/` volume.
