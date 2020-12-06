"""Cross-references module."""

import html
import re
from typing import Callable, Dict, List, Match, Tuple
from xml.etree.ElementTree import Element

from markdown.inlinepatterns import REFERENCE_RE, ReferenceInlineProcessor

AUTO_REF_RE = re.compile(r'<span data-mkdocstrings-identifier="(?P<identifier>[^"<>]*)">(?P<title>.*?)</span>')
"""
A regular expression to match mkdocstrings' special reference markers
in the [`on_post_page` hook][mkdocstrings.plugin.MkdocstringsPlugin.on_post_page].
"""


class AutoRefInlineProcessor(ReferenceInlineProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(REFERENCE_RE, *args, **kwargs)

    # Code based on https://github.com/Python-Markdown/markdown/blob/8e7528fa5c98bf4652deb13206d6e6241d61630b/markdown/inlinepatterns.py#L780

    def handleMatch(self, m, data):
        text, index, handled = self.getText(data, m.end(0))
        if not handled:
            return None, None, None

        identifier, end, handled = self.evalId(data, index, text)
        if not handled:
            return None, None, None

        if re.search(r"[/ \x00-\x1f]", identifier):
            # Do nothing if the matched reference contains:
            # - a space, slash or control character (considered unintended);
            # - specifically \x01 is used by Python-Markdown HTML stash when there's inline formatting,
            #   but references with Markdown formatting are not possible anyway.
            return None, m.start(0), end

        return self.makeTag(identifier, text), m.start(0), end

    def evalId(self, data, index, text):
        m = self.RE_LINK.match(data, pos=index)
        if not m:
            return None, index, False
        identifier = m.group(1) or text
        end = m.end(0)
        return identifier, end, True

    def makeTag(self, identifier, text):
        """
        Creates a tag that can be matched by `AUTO_REF_RE`.
        """
        el = Element("span")
        el.set("data-mkdocstrings-identifier", identifier)
        el.text = text
        return el


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
        identifier = match["identifier"]
        title = match["title"]

        try:
            url = relative_url(from_url, url_map[html.unescape(identifier)])
        except KeyError:
            unmapped.append(identifier)
            if title == identifier:
                return f"[{identifier}][]"
            return f"[{title}][{identifier}]"

        return f'<a href="{html.escape(url)}">{title}</a>'

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
    html = AUTO_REF_RE.sub(fix_ref(url_map, from_url, unmapped), html)
    return html, unmapped
