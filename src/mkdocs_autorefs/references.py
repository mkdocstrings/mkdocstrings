"""Cross-references module."""

import re
from html import escape, unescape
from typing import Any, Callable, List, Match, Tuple, Union
from xml.etree.ElementTree import Element

from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import REFERENCE_RE, ReferenceInlineProcessor

AUTO_REF_RE = re.compile(r'<span data-mkdocstrings-identifier=("?)(?P<identifier>[^"<>]*)\1>(?P<title>.*?)</span>')
"""
A regular expression to match mkdocstrings' special reference markers
in the [`on_post_page` hook][mkdocs_autorefs.plugin.AutorefsPlugin.on_post_page].
"""

EvalIDType = Tuple[Any, Any, Any]


class AutoRefInlineProcessor(ReferenceInlineProcessor):
    """A Markdown extension."""

    def __init__(self, *args, **kwargs):  # noqa: D107
        super().__init__(REFERENCE_RE, *args, **kwargs)

    # Code based on
    # https://github.com/Python-Markdown/markdown/blob/8e7528fa5c98bf4652deb13206d6e6241d61630b/markdown/inlinepatterns.py#L780

    def handleMatch(self, m, data) -> Union[Element, EvalIDType]:  # noqa: N802 (parent's casing)
        """
        Handle an element that matched.

        Arguments:
            m: The match object.
            data: The matched data.

        Returns:
            A new element or a tuple.
        """
        text, index, handled = self.getText(data, m.end(0))
        if not handled:
            return None, None, None

        identifier, end, handled = self.evalId(data, index, text)
        if not handled:
            return None, None, None

        if re.search(r"[/ \x00-\x1f]", identifier):  # type: ignore
            # Do nothing if the matched reference contains:
            # - a space, slash or control character (considered unintended);
            # - specifically \x01 is used by Python-Markdown HTML stash when there's inline formatting,
            #   but references with Markdown formatting are not possible anyway.
            return None, m.start(0), end

        return self.makeTag(identifier, text), m.start(0), end

    def evalId(self, data: str, index: int, text: str) -> EvalIDType:  # noqa: N802 (parent's casing)
        """
        Evaluate the id portion of `[ref][id]`.

        If `[ref][]` use `[ref]`.

        Arguments:
            data: The data to evaluate.
            index: The starting position.
            text: The text to use when no identifier.

        Returns:
            A tuple containing the identifier, its end position, and whether it matched.
        """
        m = self.RE_LINK.match(data, pos=index)
        if not m:
            return None, index, False
        identifier = m.group(1) or text
        end = m.end(0)
        return identifier, end, True

    def makeTag(self, identifier: str, text: str) -> Element:  # noqa: N802,W0221 (parent's casing, different params)
        """
        Create a tag that can be matched by `AUTO_REF_RE`.

        Arguments:
            identifier: The identifier to use in the HTML property.
            text: The text to use in the HTML tag.

        Returns:
            A new element.
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
    parts_a = url_a.split("/")
    url_b, anchor = url_b.split("#", 1)
    parts_b = url_b.split("/")

    # remove common left parts
    while parts_a and parts_b and parts_a[0] == parts_b[0]:
        parts_a.pop(0)
        parts_b.pop(0)

    # go up as many times as remaining a parts' depth
    levels = len(parts_a) - 1
    parts_relative = [".."] * levels + parts_b
    relative = "/".join(parts_relative)
    return f"{relative}#{anchor}"


def fix_ref(url_mapper: Callable[[str], str], from_url: str, unmapped: List[str]) -> Callable:
    """
    Return a `repl` function for [`re.sub`](https://docs.python.org/3/library/re.html#re.sub).

    In our context, we match Markdown references and replace them with HTML links.

    When the matched reference's identifier was not mapped to an URL, we append the identifier to the outer
    `unmapped` list. It generally means the user is trying to cross-reference an object that was not collected
    and rendered, making it impossible to link to it. We catch this exception in the caller to issue a warning.

    Arguments:
        url_mapper: A callable that gets an object's site URL by its identifier,
            such as [mkdocs_autorefs.plugin.AutorefsPlugin.get_item_url][].
        from_url: The URL of the base page, from which we link towards the targeted pages.
        unmapped: A list to store unmapped identifiers.

    Returns:
        The actual function accepting a [`Match` object](https://docs.python.org/3/library/re.html#match-objects)
        and returning the replacement strings.
    """

    def inner(match: Match):
        identifier = match["identifier"]
        title = match["title"]

        try:
            url = relative_url(from_url, url_mapper(unescape(identifier)))
        except KeyError:
            unmapped.append(identifier)
            if title == identifier:
                return f"[{identifier}][]"
            return f"[{title}][{identifier}]"

        return f'<a href="{escape(url)}">{title}</a>'

    return inner


def fix_refs(
    html: str,
    from_url: str,
    url_mapper: Callable[[str], str],
) -> Tuple[str, List[str]]:
    """
    Fix all references in the given HTML text.

    Arguments:
        html: The text to fix.
        from_url: The URL at which this HTML is served.
        url_mapper: A callable that gets an object's site URL by its identifier,
            such as [mkdocs_autorefs.plugin.AutorefsPlugin.get_item_url][].

    Returns:
        The fixed HTML.
    """
    unmapped = []  # type: ignore
    html = AUTO_REF_RE.sub(fix_ref(url_mapper, from_url, unmapped), html)
    return html, unmapped


class AutorefsExtension(Extension):
    """Extension that inserts auto-references in Markdown."""

    def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802 (casing: parent method's name)
        """
        Register the extension.

        Add an instance of our [`AutoRefInlineProcessor`][mkdocs_autorefs.references.AutoRefInlineProcessor] to the Markdown parser.

        Arguments:
            md: A `markdown.Markdown` instance.
        """
        md.inlinePatterns.register(
            AutoRefInlineProcessor(md),
            "mkdocstrings",
            priority=168,  # Right after markdown.inlinepatterns.ReferenceInlineProcessor
        )
