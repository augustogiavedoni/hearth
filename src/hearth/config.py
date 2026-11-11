"""Configuration loading and validation.

Responsibility:
    Read settings from environment variables (optionally a local ``.env``)
    and agent role files (``agents/*.yaml``), and validate them into typed
    objects.

Must NOT:
    - Log, print or return raw secret values.
    - Fall back to hard-coded credentials or defaults for secrets.
    - Read files outside the configured paths.
"""

# TODO(augusto): design and implement configuration loading.
