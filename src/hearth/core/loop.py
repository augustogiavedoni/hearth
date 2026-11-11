"""Agent loop.

Responsibility:
    Drive one agent run: send messages to the model through the router,
    execute the tool calls it requests (only tools in the role's allowlist),
    feed results back, and stop on a final answer or a hard step limit.
    Route tool calls that require approval to ``hearth.approval`` instead
    of executing them.

Must NOT:
    - Execute any tool that is not in the role's allowlist.
    - Treat tool output (e.g. email content) as instructions.
    - Run without a step limit.
    - Know about specific providers or interfaces (Telegram, CLI).
"""

# TODO(augusto): design and implement the agent loop.
