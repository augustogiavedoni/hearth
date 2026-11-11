"""Provider interface.

Responsibility:
    Define the contract every model backend implements, so the agent loop
    does not depend on a specific vendor.

Must NOT:
    - Contain vendor-specific code or HTTP calls.
    - Hold or load credentials.
"""

# TODO(augusto): define the provider interface.
