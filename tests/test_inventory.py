"""Tests for the inventory module."""

from __future__ import annotations

from io import BytesIO
from os.path import join

import pytest
from mkdocs.commands.build import build
from mkdocs.config import load_config

from mkdocstrings import Inventory, InventoryItem


@pytest.mark.parametrize(
    "our_inv",
    [
        Inventory(),
        Inventory([InventoryItem(name="object_path", domain="py", role="obj", uri="page_url")]),
        Inventory([InventoryItem(name="object_path", domain="py", role="obj", uri="page_url#object_path")]),
        Inventory([InventoryItem(name="object_path", domain="py", role="obj", uri="page_url#other_anchor")]),
        Inventory([InventoryItem(name="o", domain="py", role="obj", uri="u#o", dispname="first line\nsecond line")]),
    ],
)
def test_sphinx_load_inventory_file(our_inv: Inventory) -> None:
    """Perform the 'live' inventory load test."""
    sphinx = pytest.importorskip("sphinx.util.inventory", reason="Sphinx is not installed")

    buffer = BytesIO(our_inv.format_sphinx())
    sphinx_inv = sphinx.InventoryFile.load(buffer, "", join)

    sphinx_inv_length = sum(len(sphinx_inv[key]) for key in sphinx_inv)
    assert sphinx_inv_length == len(our_inv.values())

    for item in our_inv.values():
        assert item.name in sphinx_inv[f"{item.domain}:{item.role}"]


def test_sphinx_load_mkdocstrings_inventory_file() -> None:
    """Perform the 'live' inventory load test on mkdocstrings own inventory."""
    sphinx = pytest.importorskip("sphinx.util.inventory", reason="Sphinx is not installed")

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


@pytest.mark.parametrize(
    "our_inv",
    [
        Inventory(),
        Inventory([InventoryItem(name="object_path", domain="py", role="obj", uri="page_url")]),
        Inventory([InventoryItem(name="object_path", domain="py", role="obj", uri="page_url#object_path")]),
        Inventory([InventoryItem(name="object_path", domain="py", role="obj", uri="page_url#other_anchor")]),
        Inventory([InventoryItem(name="o", domain="py", role="obj", uri="u#o", dispname="first line\nsecond line")]),
    ],
)
def test_mkdocstrings_roundtrip_inventory_file(our_inv: Inventory) -> None:
    """Save some inventory files, then load them in again."""
    buffer = BytesIO(our_inv.format_sphinx())
    round_tripped = Inventory.parse_sphinx(buffer)

    assert our_inv.keys() == round_tripped.keys()
    for key, value in our_inv.items():
        round_tripped_item = round_tripped[key]
        assert round_tripped_item.name == value.name
        assert round_tripped_item.domain == value.domain
        assert round_tripped_item.role == value.role
        assert round_tripped_item.uri == value.uri
        assert round_tripped_item.priority == value.priority
        assert round_tripped_item.dispname == value.dispname.splitlines()[0]
