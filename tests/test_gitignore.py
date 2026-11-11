"""Guard rails: secret files must stay git-ignored.

Reads only ``.gitignore``; never opens ``.env`` or any credential file.
"""

from pathlib import Path

import pytest

GITIGNORE = Path(__file__).resolve().parent.parent / ".gitignore"

REQUIRED_PATTERNS = [".env", "credentials*.json", "token*.json", "*.pem", "data/"]


def _patterns() -> set[str]:
    lines = GITIGNORE.read_text(encoding="utf-8").splitlines()
    return {line.strip() for line in lines if line.strip() and not line.startswith("#")}


@pytest.mark.parametrize("pattern", REQUIRED_PATTERNS)
def test_secret_pattern_is_ignored(pattern: str) -> None:
    assert pattern in _patterns(), f"{pattern!r} missing from .gitignore"


def test_env_is_not_unignored() -> None:
    assert "!.env" not in _patterns()
