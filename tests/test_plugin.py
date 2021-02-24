"""Tests for the plugin module."""

import sys

import pytest
from mkdocs.commands.build import build
from mkdocs.config.base import load_config


@pytest.mark.skipif(sys.version_info < (3, 7), reason="using plugins that require Python 3.7")
@pytest.mark.xfail(sys.version_info >= (3, 9), reason="pytkdocs is failing on Python 3.9")
def test_plugin(tmp_path):
    """Build our own documentation."""
    config = load_config()
    config["site_dir"] = tmp_path
    build(config)
