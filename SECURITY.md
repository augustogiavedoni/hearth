# Security policy

hearth handles personal email and API credentials, so security reports are
taken seriously, even though this is a personal project.

## Reporting a vulnerability

**Do not open a public issue.** Report it privately through
[GitHub private vulnerability reporting](https://github.com/augustogiavedoni/hearth/security/advisories/new).

Please include what you found, how to reproduce it, and its impact. Use
placeholders instead of real emails, tokens, hostnames or IP addresses.

## Supported versions

There are no releases yet. Only the `main` branch is supported.

## Scope

In scope: code and configuration in this repository, for example:

- prompt injection (e.g. through an email) that triggers an action without
  human approval, or that lets the mail agent send, delete or forward;
- a tool reachable by an agent role that does not allow it;
- leakage of credentials, tokens or email content (logs, errors, the
  container image, the repository);
- weaknesses in the deployment files (`deploy/`).

Out of scope: vulnerabilities in third-party services and libraries
(model providers, Google APIs, Telegram) unless hearth uses them in an
unsafe way. Report those to their maintainers.

The threats this project is designed against are described in
[docs/threat-model.md](docs/threat-model.md).

## What to expect

This is maintained by one person in their spare time, so there is no
guaranteed response time. Reports will be acknowledged, and fixes will be
credited in the advisory if you wish.
