"""Module responsible for the objects inventory."""

# Credits to Brian Skinn and the sphobjinv project:
# https://github.com/bskinn/sphobjinv

import re
import zlib
from textwrap import dedent
from typing import BinaryIO, List, Optional


class InventoryItem:
    """Inventory item."""

    def __init__(
        self, name: str, domain: str, role: str, uri: str, priority: str = "1", dispname: Optional[str] = None
    ):
        """Initialize the object.

        Arguments:
            name: The item name.
            domain: The item domain, like 'python' or 'crystal'.
            role: The item role, like 'class' or 'method'.
            uri: The item URI.
            priority: The item priority. It can help for inventory suggestions.
            dispname: The item display name.
        """
        self.name: str = name
        self.domain: str = domain
        self.role: str = role
        self.uri: str = uri
        self.priority: str = priority
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

    @classmethod
    def parse_sphinx(cls, line: str) -> "InventoryItem":
        m = re.search(r"^(.+?)\s+(\S+):(\S+)\s+(-?\d+)\s+(\S+)\s+(.*)$", line)
        if not m:
            raise ValueError(line)
        name, domain, role, priority, uri, dispname = m.groups()
        if uri.endswith("$"):
            uri = uri[:-1] + name
        if dispname == "-":
            dispname = name
        return cls(name, domain, role, uri, priority, dispname)


class Inventory(dict):
    """Inventory of collected and rendered objects."""

    def __init__(self, items: Optional[List[InventoryItem]] = None, project: str = "project", version: str = "0.0.0"):
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

    def register(self, *args, **kwargs):
        """Create and register an item.

        Arguments:
            *args: Arguments passed to [InventoryItem][mkdocstrings.inventory.InventoryItem].
            **kwargs: Keyword arguments passed to [InventoryItem][mkdocstrings.inventory.InventoryItem].
        """
        item = InventoryItem(*args, **kwargs)
        self[item.name] = item

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
                """
            )
            .lstrip()
            .encode("utf8")
        )

        lines = [item.format_sphinx().encode("utf8") for item in self.values()]
        return header + zlib.compress(b"\n".join(lines) + b"\n", 9)

    @classmethod
    def parse_sphinx(cls, file: BinaryIO, *, domain_filter: str = "") -> "Inventory":
        for _ in range(4):
            file.readline()
        lines = zlib.decompress(file.read()).splitlines()
        items = (InventoryItem.parse_sphinx(line.decode("utf8")) for line in lines)
        return cls([item for item in items if item.domain.startswith(domain_filter)])
