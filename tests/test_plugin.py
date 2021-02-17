"""Tests for the plugin module."""

import sys

import pytest
from mkdocs.commands.build import build
from mkdocs.config.base import load_config


@pytest.mark.xfail(sys.version.startswith("3.9"), reason="pytkdocs is failing on Python 3.9")
def test_plugin(tmp_path):
    """Build our own documentation."""
    config = load_config()
    config["site_dir"] = tmp_path
    build(config)
