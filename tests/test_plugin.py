"""Tests for the plugin module."""
from mkdocs.commands.build import build
from mkdocs.config.base import load_config


def test_plugin():
    """Build our own documentation."""
    build(load_config())
