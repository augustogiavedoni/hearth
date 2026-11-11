"""Gmail tools.

Responsibility:
    Provide read-only access to Gmail (list and read messages) and draft
    creation, using the narrowest OAuth scopes that allow it. Return email
    content as clearly delimited, untrusted data.

Must NOT:
    - Send, forward, delete, archive or label messages.
    - Request the ``gmail.send`` or full ``mail.google.com`` scopes.
    - Create a draft without going through approval.
    - Persist or log email bodies outside ``data/``.
"""

# TODO(augusto): implement Gmail read and draft tools.
