"""Cross-references module."""

import random
import re
import string
from typing import Callable, Dict, List, Match, Pattern, Tuple

from bs4 import BeautifulSoup, NavigableString

AUTO_REF: Pattern = re.compile(r"\[(?P<title>.+?)\]\[(?P<identifier>.*?)\]")
"""
A regular expression to match unresolved Markdown references
in the [`on_post_page` hook][mkdocstrings.plugin.MkdocstringsPlugin.on_post_page].
"""


class Placeholder:
    """
    This class is used as a placeholder store.

    Placeholders are random, unique strings that temporarily replace `<code>` nodes in an HTML tree.

    Why do we replace these nodes with such strings? Because we want to fix cross-references that were not
    resolved during Markdown conversion, and we must never touch to what's inside of a code block.
    To ease the process, instead of selecting nodes in the HTML tree with complex filters (I tried, believe me),
    we simply "hide" the code nodes, and bulk-replace unresolved cross-references in the whole HTML text at once,
    with a regular expression substitution. Once it's done, we bulk-replace code nodes back, with a regular expression
    substitution again.
    """

    def __init__(self) -> None:
        """Initialization method."""
        self.ids: Dict[str, str] = {}
        self.seed = ""
        self.set_seed()

    def store(self, value: str) -> str:
        """
        Store a text under a unique ID, return that ID.

        Arguments:
            value: The text to store.

        Returns:
            The ID under which the text is stored.
        """
        i = self.get_id()
        while i in self.ids:
            i = self.get_id()
        self.ids[i] = value
        return i

    def get_id(self) -> str:
        """Return a random, unique string."""
        return f"{self.seed}{random.randint(0, 1000000)}"  # noqa: S311 (it's not for security/cryptographic purposes)

    def set_seed(self) -> None:
        """Reset the seed in `self.seed` with a random string."""
        self.seed = "".join(random.choices(string.ascii_letters + string.digits, k=16))

    def replace_code_tags(self, soup: BeautifulSoup) -> None:
        """
        Recursively replace code nodes with navigable strings whose values are unique IDs.

        Arguments:
            soup: The root tag of a BeautifulSoup HTML tree.
        """

        def recursive_replace(tag):
            if hasattr(tag, "contents"):
                for i in range(len(tag.contents)):
                    child = tag.contents[i]
                    if child.name == "code":
                        tag.contents[i] = NavigableString(self.store(str(child)))
                    else:
                        recursive_replace(child)

        recursive_replace(soup)

    def restore_code_tags(self, soup_str: str) -> str:
        """
        Restore code nodes previously replaced by unique placeholders.

        Args:
            soup_str: HTML text.

        Returns:
            The same HTML text with placeholders replaced by their respective original code nodes.
        """

        def replace_placeholder(match):
            placeholder = match.groups()[0]
            return self.ids[placeholder]

        return re.sub(rf"({self.seed}\d+)", replace_placeholder, soup_str)


def relative_url(url_a: str, url_b: str) -> str:
    """
    Compute the relative path from URL A to URL B.

    Arguments:
        url_a: URL A.
        url_b: URL B.

    Returns:
        The relative URL to go from A to B.
    """
    parts_a = url_a.rstrip("/").split("/")
    url_b, anchor = url_b.split("#", 1)
    parts_b = url_b.split("/")

    # remove common left parts
    while parts_a and parts_b and parts_a[0] == parts_b[0]:
        parts_a.pop(0)
        parts_b.pop(0)

    # go up as many times as remaining a parts' depth
    parts_relative = [".."] * len(parts_a) + parts_b
    relative = "/".join(parts_relative)
    return f"{relative}#{anchor}"


def fix_ref(url_map, from_url, unmapped: List[str], unintended: List[str]) -> Callable:
    """
    Return a `repl` function for [`re.sub`](https://docs.python.org/3/library/re.html#re.sub).

    In our context, we match Markdown references and replace them with HTML links.

    When the matched reference's identifier contains a space or slash, we append the identifier to the outer
    `unintended` list to tell the caller that this unresolved reference should be ignored as it's probably
    not intended as a reference.

    When the matched reference's identifier was not mapped to an URL, we append the identifier to the outer
    `unmapped` list. It generally means the user is trying to cross-reference an object that was not collected
    and rendered, making it impossible to link to it. We catch this exception in the caller to issue a warning.

    Arguments:
        url_map: The mapping of objects and their URLs.
        unmapped: A list to store unmapped identifiers.
        unintended: A list to store identifiers of unintended references.

    Returns:
        The actual function accepting a [`Match` object](https://docs.python.org/3/library/re.html#match-objects)
        and returning the replacement strings.
    """

    def inner(match: Match):
        groups = match.groupdict()
        identifier = groups["identifier"]
        title = groups["title"]

        if title and not identifier:
            identifier, title = title, identifier

        try:
            url = relative_url(from_url, url_map[identifier])
        except KeyError:
            if " " in identifier or "/" in identifier:
                # invalid identifier, must not be a intended reference
                unintended.append(identifier)
            else:
                unmapped.append(identifier)

            if not title:
                return f"[{identifier}][]"
            return f"[{title}][{identifier}]"

        # TODO: we could also use a config option to ignore some identifiers
        # and to map others to URLs, something like:
        # references:
        #   ignore:
        #     - "USERNAME:PASSWORD@"
        #   map:
        #     some-id: https://example.com

        return f'<a href="{url}">{title or identifier}</a>'

    return inner


def fix_refs(html: str, from_url: str, url_map: Dict[str, str]) -> Tuple[str, List[str], List[str]]:
    """
    Fix all references in the given HTML text.

    Arguments:
        html: The text to fix.
        from_url: The URL at which this HTML is served.
        url_map: The mapping of objects and their URLs.

    Returns:
        The fixed HTML.
    """
    placeholder = Placeholder()
    while re.search(placeholder.seed, html) or any(placeholder.seed in url for url in url_map.values()):
        placeholder.set_seed()

    unmapped, unintended = [], []  # type: ignore
    soup = BeautifulSoup(html, "html.parser")
    placeholder.replace_code_tags(soup)
    fixed_soup = AUTO_REF.sub(fix_ref(url_map, from_url, unmapped, unintended), str(soup))

    return placeholder.restore_code_tags(fixed_soup), unmapped, unintended
