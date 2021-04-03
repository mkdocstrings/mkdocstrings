"""Tests for the inventory module."""

from io import BytesIO
from os.path import join
from pathlib import Path

import pytest

from mkdocstrings.inventory import Inventory, InventoryItem

sphinx_inventory = pytest.importorskip("sphinx.util.inventory", reason="Sphinx is not installed")
MKDOCSTRINGS_OBJECTS_INV = Path("site/objects.inv")


@pytest.mark.parametrize(
    "inventory",
    [
        Inventory(),
        Inventory([InventoryItem(name="object_path", domain="py", role="obj", uri="page_url")]),
        Inventory([InventoryItem(name="object_path", domain="py", role="obj", uri="page_url#object_path")]),
        Inventory([InventoryItem(name="object_path", domain="py", role="obj", uri="page_url#other_anchor")]),
    ],
)
def test_sphinx_load_inventory_file(inventory):
    """Perform the 'live' inventory load test."""
    buffer = BytesIO(inventory.format_sphinx())
    sphinx_inventory.InventoryFile.load(buffer, "", join)


@pytest.mark.skipif(not MKDOCSTRINGS_OBJECTS_INV.exists(), reason="site/objects.inv does not exist")
def test_sphinx_load_mkdocstrings_inventory_file():
    """Perform the 'live' inventory load test on mkdocstrings own inventory."""
    with MKDOCSTRINGS_OBJECTS_INV.open("rb") as fp:
        sphinx_inventory.InventoryFile.load(fp, "", join)
