"""Smoke test: the package and its subpackages import."""

import importlib

import pytest

MODULES = [
    "hearth",
    "hearth.config",
    "hearth.core.loop",
    "hearth.providers.base",
    "hearth.providers.openai_compat",
    "hearth.providers.router",
    "hearth.tools.base",
    "hearth.tools.gmail",
    "hearth.approval",
    "hearth.interfaces.telegram",
]


@pytest.mark.parametrize("name", MODULES)
def test_module_imports(name: str) -> None:
    assert importlib.import_module(name) is not None
