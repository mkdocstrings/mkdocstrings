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

    def __init__(self, seed_length: int = 16) -> None:
        """
        Initialize the object.

        Arguments:
            seed_length: Length of the seed.
        """
        self._store: List[str] = []
        self.seed = ""
        self.seed_length = seed_length
        self.set_seed()

    def store(self, value: str) -> str:
        """
        Store a text under a unique ID, return that ID.

        Arguments:
            value: The text to store.

        Returns:
            The ID under which the text is stored.
        """
        new_id = f"{self.seed}{len(self._store)}"
        self._store.append(value)
        return new_id

    def set_seed(self) -> None:
        """Reset the seed in `self.seed` with a random string."""
        alphabet = string.ascii_letters + string.digits
        self.seed = "".join(random.choices(alphabet, k=self.seed_length))

    def replace_code_tags(self, soup: BeautifulSoup) -> None:
        """
        Recursively replace code nodes with navigable strings whose values are unique IDs.

        Arguments:
            soup: The root tag of a BeautifulSoup HTML tree.
        """
        self._recursive_replace(soup)

    def restore_code_tags(self, soup_str: str) -> str:
        """
        Restore code nodes previously replaced by unique placeholders.

        Arguments:
            soup_str: HTML text.

        Returns:
            The same HTML text with placeholders replaced by their respective original code nodes.
        """
        return re.sub(rf"{self.seed}(\d+)", self._replace_id_with_value, soup_str)

    def _replace_id_with_value(self, match):
        return self._store[int(match.group(1))]

    def _recursive_replace(self, tag):
        if hasattr(tag, "contents"):  # noqa: WPS421 (builtin function call, special cases only)
            for index, child in enumerate(tag.contents):
                if child.name == "code":
                    tag.contents[index] = NavigableString(self.store(str(child)))
                else:
                    self._recursive_replace(child)


def relative_url(url_a: str, url_b: str) -> str:
    """
    Compute the relative path from URL A to URL B.

    Arguments:
        url_a: URL A.
        url_b: URL B.

    Returns:
        The relative URL to go from A to B.
    """
    directory_url = False
    if url_a[-1] == "/":
        url_a = url_a.rstrip("/")
        directory_url = True
    parts_a = url_a.split("/")
    url_b, anchor = url_b.split("#", 1)
    parts_b = url_b.split("/")

    # remove common left parts
    while parts_a and parts_b and parts_a[0] == parts_b[0]:
        parts_a.pop(0)
        parts_b.pop(0)

    # go up as many times as remaining a parts' depth
    levels = len(parts_a)
    if not directory_url:
        levels -= 1
    parts_relative = [".."] * levels + parts_b  # noqa: WPS435 (list multiply ok)
    relative = "/".join(parts_relative)
    return f"{relative}#{anchor}"


def fix_ref(url_map: Dict[str, str], from_url: str, unmapped: List[str]) -> Callable:  # noqa: WPS231 (not that complex)
    """
    Return a `repl` function for [`re.sub`](https://docs.python.org/3/library/re.html#re.sub).

    In our context, we match Markdown references and replace them with HTML links.

    When the matched reference's identifier contains a space or slash, we do nothing as we consider it
    to be unintended.

    When the matched reference's identifier was not mapped to an URL, we append the identifier to the outer
    `unmapped` list. It generally means the user is trying to cross-reference an object that was not collected
    and rendered, making it impossible to link to it. We catch this exception in the caller to issue a warning.

    Arguments:
        url_map: The mapping of objects and their URLs.
        from_url: The URL of the base page, from which we link towards the targeted pages.
        unmapped: A list to store unmapped identifiers.

    Returns:
        The actual function accepting a [`Match` object](https://docs.python.org/3/library/re.html#match-objects)
        and returning the replacement strings.
    """

    def inner(match: Match):  # noqa: WPS430 (nested function, no other way than side-effecting the warnings)
        groups = match.groupdict()
        identifier = groups["identifier"]
        title = groups["title"]

        if title and not identifier:
            identifier, title = title, identifier

        try:
            url = relative_url(from_url, url_map[identifier])
        except KeyError:
            if " " not in identifier and "/" not in identifier:
                unmapped.append(identifier)

            if not title:
                return f"[{identifier}][]"
            return f"[{title}][{identifier}]"

        return f'<a href="{url}">{title or identifier}</a>'

    return inner


def fix_refs(
    html: str,
    from_url: str,
    url_map: Dict[str, str],
) -> Tuple[str, List[str]]:
    """
    Fix all references in the given HTML text.

    Arguments:
        html: The text to fix.
        from_url: The URL at which this HTML is served.
        url_map: The mapping of objects and their URLs.

    Returns:
        The fixed HTML.
    """
    unmapped = []  # type: ignore
    if not AUTO_REF.search(html):
        return html, unmapped

    urls = "\n".join(set(url_map.values()))
    placeholder = Placeholder()
    while re.search(placeholder.seed, html) or placeholder.seed in urls:
        placeholder.set_seed()

    soup = BeautifulSoup(html, "html.parser")
    placeholder.replace_code_tags(soup)
    fixed_soup = AUTO_REF.sub(fix_ref(url_map, from_url, unmapped), str(soup))

    return placeholder.restore_code_tags(fixed_soup), unmapped
