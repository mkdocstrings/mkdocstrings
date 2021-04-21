"""Tests for the inventory module."""

import sys
from io import BytesIO
from os.path import join

import pytest
from mkdocs.commands.build import build
from mkdocs.config import load_config

from mkdocstrings.inventory import Inventory, InventoryItem

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
def test_sphinx_load_inventory_file(our_inv):
    """Perform the 'live' inventory load test."""
    buffer = BytesIO(our_inv.format_sphinx())
    sphinx_inv = sphinx.InventoryFile.load(buffer, "", join)

    sphinx_inv_length = sum(len(sphinx_inv[key]) for key in sphinx_inv)
    assert sphinx_inv_length == len(our_inv.values())

    for item in our_inv.values():
        assert item.name in sphinx_inv[f"{item.domain}:{item.role}"]


@pytest.mark.skipif(sys.version_info < (3, 7), reason="using plugins that require Python 3.7")
def test_sphinx_load_mkdocstrings_inventory_file():
    """Perform the 'live' inventory load test on mkdocstrings own inventory."""
    mkdocs_config = load_config()
    build(mkdocs_config)
    own_inv = mkdocs_config["plugins"]["mkdocstrings"].handlers.inventory

    with open("site/objects.inv", "rb") as fp:
        sphinx_inv = sphinx.InventoryFile.load(fp, "", join)

    sphinx_inv_length = sum(len(sphinx_inv[key]) for key in sphinx_inv)
    assert sphinx_inv_length == len(own_inv.values())

    for item in own_inv.values():
        assert item.name in sphinx_inv[f"{item.domain}:{item.role}"]
