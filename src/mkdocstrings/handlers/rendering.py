"""This module holds helpers responsible for augmentations to the Markdown sub-documents produced by handlers."""

from __future__ import annotations

import copy
import re
import textwrap
from typing import TYPE_CHECKING, Any

from markdown.extensions import Extension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.treeprocessors import Treeprocessor
from markupsafe import Markup
from pymdownx.highlight import Highlight, HighlightExtension

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element

    from markdown import Markdown


class Highlighter(Highlight):
    """Code highlighter that tries to match the Markdown configuration.

    Picking up the global config and defaults works only if you use the `codehilite` or
    `pymdownx.highlight` (recommended) Markdown extension.

    -   If you use `pymdownx.highlight`, highlighting settings are picked up from it, and the
        default CSS class is `.highlight`. This also means the default of `guess_lang: false`.

    -   Otherwise, if you use the `codehilite` extension, settings are picked up from it, and the
        default CSS class is `.codehilite`. Also consider setting `guess_lang: false`.

    -   If neither are added to `markdown_extensions`, highlighting is enabled anyway. This is for
        backwards compatibility. If you really want to disable highlighting even in *mkdocstrings*,
        add one of these extensions anyway and set `use_pygments: false`.

    The underlying implementation is `pymdownx.highlight` regardless.
    """

    # https://raw.githubusercontent.com/facelessuser/pymdown-extensions/main/docs/src/markdown/extensions/highlight.md
    _highlight_config_keys = frozenset(
        (
            "css_class",
            "guess_lang",
            "default_lang",
            "pygments_style",
            "noclasses",
            "use_pygments",
            "linenums",
            "linenums_special",
            "linenums_style",
            "linenums_class",
            "extend_pygments_lang",
            "language_prefix",
            "code_attr_on_pre",
            "auto_title",
            "auto_title_map",
            "line_spans",
            "anchor_linenums",
            "line_anchors",
            "pygments_lang_class",
            "stripnl",
        ),
    )

    def __init__(self, md: Markdown):
        """Configure to match a `markdown.Markdown` instance.

        Arguments:
            md: The Markdown instance to read configs from.
        """
        config: dict[str, Any] = {}
        self._highlighter: str | None = None
        for ext in md.registeredExtensions:
            if isinstance(ext, HighlightExtension) and (ext.enabled or not config):
                self._highlighter = "highlight"
                config = ext.getConfigs()
                break  # This one takes priority, no need to continue looking
            if isinstance(ext, CodeHiliteExtension) and not config:
                self._highlighter = "codehilite"
                config = ext.getConfigs()
                config["language_prefix"] = config["lang_prefix"]
        self._css_class = config.pop("css_class", "highlight")
        super().__init__(**{name: opt for name, opt in config.items() if name in self._highlight_config_keys})

    def highlight(
        self,
        src: str,
        language: str | None = None,
        *,
        inline: bool = False,
        dedent: bool = True,
        linenums: bool | None = None,
        **kwargs: Any,
    ) -> str:
        """Highlight a code-snippet.

        Arguments:
            src: The code to highlight.
            language: Explicitly tell what language to use for highlighting.
            inline: Whether to highlight as inline.
            dedent: Whether to dedent the code before highlighting it or not.
            linenums: Whether to add line numbers in the result.
            **kwargs: Pass on to `pymdownx.highlight.Highlight.highlight`.

        Returns:
            The highlighted code as HTML text, marked safe (not escaped for HTML).
        """
        if isinstance(src, Markup):
            src = src.unescape()
        if dedent:
            src = textwrap.dedent(src)

        kwargs.setdefault("css_class", self._css_class)
        old_linenums = self.linenums  # type: ignore[has-type]
        if linenums is not None:
            self.linenums = linenums
        try:
            result = super().highlight(src, language, inline=inline, **kwargs)
        finally:
            self.linenums = old_linenums

        if inline:
            # From the maintainer of codehilite, the codehilite CSS class, as defined by the user,
            # should never be added to inline code, because codehilite does not support inline code.
            # See https://github.com/Python-Markdown/markdown/issues/1220#issuecomment-1692160297.
            css_class = "" if self._highlighter == "codehilite" else kwargs["css_class"]
            return Markup(f'<code class="{css_class} language-{language}">{result.text}</code>')
        return Markup(result)


class IdPrependingTreeprocessor(Treeprocessor):
    """Prepend the configured prefix to IDs of all HTML elements."""

    name = "mkdocstrings_ids"

    id_prefix: str
    """The prefix to add to every ID. It is prepended without any separator; specify your own separator if needed."""

    def __init__(self, md: Markdown, id_prefix: str):
        """Initialize the object.

        Arguments:
            md: A `markdown.Markdown` instance.
            id_prefix: The prefix to add to every ID. It is prepended without any separator.
        """
        super().__init__(md)
        self.id_prefix = id_prefix

    def run(self, root: Element) -> None:  # noqa: D102 (ignore missing docstring)
        if self.id_prefix:
            self._prefix_ids(root)

    def _prefix_ids(self, root: Element) -> None:
        index = len(root)
        for el in reversed(root):  # Reversed mainly for the ability to mutate during iteration.
            index -= 1

            self._prefix_ids(el)
            href_attr = el.get("href")

            if id_attr := el.get("id"):
                if el.tag == "a" and not href_attr:
                    # An anchor with id and no href is used by autorefs:
                    # leave it untouched and insert a copy with updated id after it.
                    new_el = copy.deepcopy(el)
                    new_el.set("id", self.id_prefix + id_attr)
                    root.insert(index + 1, new_el)
                else:
                    # Anchors with id and href are not used by autorefs:
                    # update in place.
                    el.set("id", self.id_prefix + id_attr)

            # Always update hrefs, names and labels-for:
            # there will always be a corresponding id.
            if href_attr and href_attr.startswith("#"):
                el.set("href", "#" + self.id_prefix + href_attr[1:])

            if name_attr := el.get("name"):
                el.set("name", self.id_prefix + name_attr)

            if el.tag == "label":
                for_attr = el.get("for")
                if for_attr:
                    el.set("for", self.id_prefix + for_attr)


class HeadingShiftingTreeprocessor(Treeprocessor):
    """Shift levels of all Markdown headings according to the configured base level."""

    name = "mkdocstrings_headings"
    regex = re.compile(r"([Hh])([1-6])")

    shift_by: int
    """The number of heading "levels" to add to every heading. `<h2>` with `shift_by = 3` becomes `<h5>`."""

    def __init__(self, md: Markdown, shift_by: int):
        """Initialize the object.

        Arguments:
            md: A `markdown.Markdown` instance.
            shift_by: The number of heading "levels" to add to every heading.
        """
        super().__init__(md)
        self.shift_by = shift_by

    def run(self, root: Element) -> None:  # noqa: D102 (ignore missing docstring)
        if not self.shift_by:
            return
        for el in root.iter():
            match = self.regex.fullmatch(el.tag)
            if match:
                level = int(match[2]) + self.shift_by
                level = max(1, min(level, 6))
                el.tag = f"{match[1]}{level}"


class _HeadingReportingTreeprocessor(Treeprocessor):
    """Records the heading elements encountered in the document."""

    name = "mkdocstrings_headings_list"
    regex = re.compile(r"[Hh][1-6]")

    headings: list[Element]
    """The list (the one passed in the initializer) that is used to record the heading elements (by appending to it)."""

    def __init__(self, md: Markdown, headings: list[Element]):
        super().__init__(md)
        self.headings = headings

    def run(self, root: Element) -> None:
        permalink_class = self.md.treeprocessors["toc"].permalink_class  # type: ignore[attr-defined]
        for el in root.iter():
            if self.regex.fullmatch(el.tag):
                el = copy.copy(el)  # noqa: PLW2901
                # 'toc' extension's first pass (which we require to build heading stubs/ids) also edits the HTML.
                # Undo the permalink edit so we can pass this heading to the outer pass of the 'toc' extension.
                if len(el) > 0 and el[-1].get("class") == permalink_class:
                    del el[-1]
                self.headings.append(el)


class ParagraphStrippingTreeprocessor(Treeprocessor):
    """Unwraps the <p> element around the whole output."""

    name = "mkdocstrings_strip_paragraph"
    strip = False

    def run(self, root: Element) -> Element | None:  # noqa: D102 (ignore missing docstring)
        if self.strip and len(root) == 1 and root[0].tag == "p":
            # Turn the single <p> element into the root element and inherit its tag name (it's significant!)
            root[0].tag = root.tag
            return root[0]
        return None


class MkdocstringsInnerExtension(Extension):
    """Extension that should always be added to Markdown sub-documents that handlers request (and *only* them)."""

    def __init__(self, headings: list[Element]):
        """Initialize the object.

        Arguments:
            headings: A list that will be populated with all HTML heading elements encountered in the document.
        """
        super().__init__()
        self.headings = headings

    def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802 (casing: parent method's name)
        """Register the extension.

        Arguments:
            md: A `markdown.Markdown` instance.
        """
        md.registerExtension(self)
        md.treeprocessors.register(
            HeadingShiftingTreeprocessor(md, 0),
            HeadingShiftingTreeprocessor.name,
            priority=12,
        )
        md.treeprocessors.register(
            IdPrependingTreeprocessor(md, ""),
            IdPrependingTreeprocessor.name,
            priority=4,  # Right after 'toc' (needed because that extension adds ids to headers).
        )
        md.treeprocessors.register(
            _HeadingReportingTreeprocessor(md, self.headings),
            _HeadingReportingTreeprocessor.name,
            priority=1,  # Close to the end.
        )
        md.treeprocessors.register(
            ParagraphStrippingTreeprocessor(md),
            ParagraphStrippingTreeprocessor.name,
            priority=0.99,  # Close to the end.
        )
