"""Tests for the mkdocstrings plugin."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mkdocs.commands.build import build
from mkdocs.config import load_config

from mkdocstrings.plugin import MkdocstringsPlugin

if TYPE_CHECKING:
    from pathlib import Path


def test_disabling_plugin(tmp_path: Path) -> None:
    """Test disabling plugin."""
    docs_dir = tmp_path / "docs"
    site_dir = tmp_path / "site"
    docs_dir.mkdir()
    site_dir.mkdir()
    docs_dir.joinpath("index.md").write_text("::: mkdocstrings")

    mkdocs_config = load_config()
    mkdocs_config["docs_dir"] = str(docs_dir)
    mkdocs_config["site_dir"] = str(site_dir)
    mkdocs_config["plugins"]["mkdocstrings"].config["enabled"] = False
    mkdocs_config["plugins"].run_event("startup", command="build", dirty=False)
    try:
        build(mkdocs_config)
    finally:
        mkdocs_config["plugins"].run_event("shutdown")

    # make sure the instruction was not processed
    assert "::: mkdocstrings" in site_dir.joinpath("index.html").read_text()


def test_plugin_default_config(tmp_path: Path) -> None:
    """Test default config options are set for Plugin."""
    config_file_path = tmp_path / "mkdocs.yml"
    plugin = MkdocstringsPlugin()
    errors, warnings = plugin.load_config({}, config_file_path=str(config_file_path))
    assert errors == []
    assert warnings == []
    assert plugin.config == {
        "handlers": {},
        "default_handler": "python",
        "custom_templates": None,
        "enable_inventory": None,
        "enabled": True,
    }


def test_plugin_config_custom_templates(tmp_path: Path) -> None:
    """Test custom_templates option is relative to config file."""
    config_file_path = tmp_path / "mkdocs.yml"
    options = {"custom_templates": "docs/templates"}
    template_dir = tmp_path / options["custom_templates"]
    # Path must exist or config validation will fail.
    template_dir.mkdir(parents=True)
    plugin = MkdocstringsPlugin()
    errors, warnings = plugin.load_config(options, config_file_path=str(config_file_path))
    assert errors == []
    assert warnings == []
    assert plugin.config == {
        "handlers": {},
        "default_handler": "python",
        "custom_templates": str(template_dir),
        "enable_inventory": None,
        "enabled": True,
    }
