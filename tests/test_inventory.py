"""Tests for the inventory module."""

from __future__ import annotations

import sys
from io import BytesIO
from os.path import join
from typing import TYPE_CHECKING

import pytest
from mkdocs.commands.build import build
from mkdocs.config import load_config

from mkdocstrings.inventory import Inventory, InventoryItem

if TYPE_CHECKING:
    from mkdocstrings.plugin import MkdocstringsPlugin
sphinx = pytest.importorskip("sphinx.util.inventory", reason="Sphinx is not installed")


@pytest.mark.parametrize(
    "our_inv",
    [
        Inventory(),
        Inventory([InventoryItem(name="object_path", domain="py", role="obj", uri="page_url")]),
        Inventory([InventoryItem(name="object_path", domain="py", role="obj", uri="page_url#object_path")]),
        Inventory([InventoryItem(name="object_path", domain="py", role="obj", uri="page_url#other_anchor")]),
    ],
)
def test_sphinx_load_inventory_file(our_inv: Inventory) -> None:
    """Perform the 'live' inventory load test."""
    buffer = BytesIO(our_inv.format_sphinx())
    sphinx_inv = sphinx.InventoryFile.load(buffer, "", join)

    sphinx_inv_length = sum(len(sphinx_inv[key]) for key in sphinx_inv)
    assert sphinx_inv_length == len(our_inv.values())

    for item in our_inv.values():
        assert item.name in sphinx_inv[f"{item.domain}:{item.role}"]


@pytest.mark.skipif(sys.version_info < (3, 7), reason="using plugins that require Python 3.7")
def test_sphinx_load_mkdocstrings_inventory_file() -> None:
    """Perform the 'live' inventory load test on mkdocstrings own inventory."""
    mkdocs_config = load_config()
    mkdocs_config["plugins"].run_event("startup", command="build", dirty=False)
    try:
        build(mkdocs_config)
    finally:
        mkdocs_config["plugins"].run_event("shutdown")
    own_inv = mkdocs_config["plugins"]["mkdocstrings"].handlers.inventory

    with open("site/objects.inv", "rb") as fp:
        sphinx_inv = sphinx.InventoryFile.load(fp, "", join)

    sphinx_inv_length = sum(len(sphinx_inv[key]) for key in sphinx_inv)
    assert sphinx_inv_length == len(own_inv.values())

    for item in own_inv.values():
        assert item.name in sphinx_inv[f"{item.domain}:{item.role}"]


def test_load_inventory(plugin: MkdocstringsPlugin) -> None:
    """Test the plugin inventory loading method.

    Parameters:
        plugin: A mkdocstrings plugin instance.
    """
    plugin._load_inventory(loader=lambda *args, **kwargs: (), url="https://example.com", domains=["a", "b"])  # type: ignore[misc,arg-type]
