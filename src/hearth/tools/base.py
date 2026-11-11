"""Tool interface.

Responsibility:
    Define the contract every tool implements: a stable name, an argument
    schema the model sees, a risk level (whether it needs human approval),
    and how it is executed.

Must NOT:
    - Decide on its own whether it is allowed to run; the agent loop and
      the role allowlist decide that.
    - Expose shell execution or arbitrary network access.
"""

# TODO(augusto): define the tool interface.
