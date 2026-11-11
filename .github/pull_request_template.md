<!--
PR title must follow Conventional Commits; it becomes the squash commit on main.
Example: feat(providers): add provider interface and fake
-->

## What and why

<!-- One or two sentences. What changes and why it is needed. -->

- Milestone: <!-- e.g. M1, or "none" -->
- ADR: <!-- e.g. docs/decisions/0002-provider-interface.md, or "none" -->

## How it was tested

<!-- Commands run locally and anything checked by hand. -->

- [ ] `uv run pytest`
- [ ] `uv run mypy`
- [ ] `uv run pre-commit run --all-files`

## Security checklist

- [ ] No secrets, tokens or credentials in code, tests, docs or examples.
- [ ] No personal data (emails, hostnames, IPs, machine names).
- [ ] The mail agent still cannot send, delete or forward; risky actions
      still go through approval.
- [ ] Components that process email content gained no shell or send tools.
- [ ] If this PR closes a milestone: `docs/threat-model.md` was reviewed.

## Notes for reviewers

<!-- Trade-offs, open questions, follow-ups. Delete if empty. -->
