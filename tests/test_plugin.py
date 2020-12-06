"""Tests for the plugin module."""

import sys

import pytest
from mkdocs.commands.build import build
from mkdocs.config.base import load_config


@pytest.mark.xfail(sys.version.startswith("3.9"), reason="pytkdocs is failing on Python 3.9")
def test_plugin():
    """Build our own documentation."""
    build(load_config())
