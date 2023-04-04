"""Tests for the mkdocstrings plugin."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mkdocs.commands.build import build
from mkdocs.config import load_config

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
