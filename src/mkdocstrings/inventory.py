"""Module responsible for the objects inventory."""

# Credits to Brian Skinn and the sphobjinv project:
# https://github.com/bskinn/sphobjinv

from __future__ import annotations

import re
import zlib
from textwrap import dedent
from typing import BinaryIO, Collection


class InventoryItem:
    """Inventory item."""

    def __init__(
        self,
        name: str,
        domain: str,
        role: str,
        uri: str,
        priority: int = 1,
        dispname: str | None = None,
    ):
        """Initialize the object.

        Arguments:
            name: The item name.
            domain: The item domain, like 'python' or 'crystal'.
            role: The item role, like 'class' or 'method'.
            uri: The item URI.
            priority: The item priority. Only used internally by mkdocstrings and Sphinx.
            dispname: The item display name.
        """
        self.name: str = name
        self.domain: str = domain
        self.role: str = role
        self.uri: str = uri
        self.priority: int = priority
        self.dispname: str = dispname or name

    def format_sphinx(self) -> str:
        """Format this item as a Sphinx inventory line.

        Returns:
            A line formatted for an `objects.inv` file.
        """
        dispname = self.dispname
        if dispname == self.name:
            dispname = "-"
        uri = self.uri
        if uri.endswith(self.name):
            uri = uri[: -len(self.name)] + "$"
        return f"{self.name} {self.domain}:{self.role} {self.priority} {uri} {dispname}"

    sphinx_item_regex = re.compile(r"^(.+?)\s+(\S+):(\S+)\s+(-?\d+)\s+(\S+)\s*(.*)$")

    @classmethod
    def parse_sphinx(cls, line: str) -> InventoryItem:
        """Parse a line from a Sphinx v2 inventory file and return an `InventoryItem` from it."""
        match = cls.sphinx_item_regex.search(line)
        if not match:
            raise ValueError(line)
        name, domain, role, priority, uri, dispname = match.groups()
        if uri.endswith("$"):
            uri = uri[:-1] + name
        if dispname == "-":
            dispname = name
        return cls(name, domain, role, uri, int(priority), dispname)


class Inventory(dict):
    """Inventory of collected and rendered objects."""

    def __init__(self, items: list[InventoryItem] | None = None, project: str = "project", version: str = "0.0.0"):
        """Initialize the object.

        Arguments:
            items: A list of items.
            project: The project name.
            version: The project version.
        """
        super().__init__()
        items = items or []
        for item in items:
            self[item.name] = item
        self.project = project
        self.version = version

    def register(
        self,
        name: str,
        domain: str,
        role: str,
        uri: str,
        priority: int = 1,
        dispname: str | None = None,
    ) -> None:
        """Create and register an item.

        Arguments:
            name: The item name.
            domain: The item domain, like 'python' or 'crystal'.
            role: The item role, like 'class' or 'method'.
            uri: The item URI.
            priority: The item priority. Only used internally by mkdocstrings and Sphinx.
            dispname: The item display name.
        """
        self[name] = InventoryItem(
            name=name,
            domain=domain,
            role=role,
            uri=uri,
            priority=priority,
            dispname=dispname,
        )

    def format_sphinx(self) -> bytes:
        """Format this inventory as a Sphinx `objects.inv` file.

        Returns:
            The inventory as bytes.
        """
        header = (
            dedent(
                f"""
                # Sphinx inventory version 2
                # Project: {self.project}
                # Version: {self.version}
                # The remainder of this file is compressed using zlib.
                """,
            )
            .lstrip()
            .encode("utf8")
        )

        lines = [
            item.format_sphinx().encode("utf8")
            for item in sorted(self.values(), key=lambda item: (item.domain, item.name))
        ]
        return header + zlib.compress(b"\n".join(lines) + b"\n", 9)

    @classmethod
    def parse_sphinx(cls, in_file: BinaryIO, *, domain_filter: Collection[str] = ()) -> Inventory:
        """Parse a Sphinx v2 inventory file and return an `Inventory` from it.

        Arguments:
            in_file: The binary file-like object to read from.
            domain_filter: A collection of domain values to allow (and filter out all other ones).

        Returns:
            An inventory containing the collected items.
        """
        for _ in range(4):
            in_file.readline()
        lines = zlib.decompress(in_file.read()).splitlines()
        items = [InventoryItem.parse_sphinx(line.decode("utf8")) for line in lines]
        if domain_filter:
            items = [item for item in items if item.domain in domain_filter]
        return cls(items)
