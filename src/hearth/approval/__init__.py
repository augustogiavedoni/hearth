"""Human approval of risky actions.

Responsibility:
    Hold actions marked as requiring approval (e.g. creating a draft),
    present a complete summary to the owner, and execute or discard the
    action based on the owner's explicit answer. Pending approvals have an
    ID and an expiry.

Must NOT:
    - Auto-approve, including on timeout (timeout means reject).
    - Accept answers from anyone other than the configured owner.
    - Execute an action whose content changed after it was shown.
"""

# TODO(augusto): design and implement the approval flow.
