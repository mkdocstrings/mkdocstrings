"""This module holds helpers responsible for augmentations to the Markdown sub-documents produced by handlers."""

import copy
import re
import textwrap
from typing import List, Optional
from xml.etree.ElementTree import Element

from markdown import Markdown
from markdown.extensions import Extension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.treeprocessors import Treeprocessor
from markupsafe import Markup
from pymdownx.highlight import Highlight, HighlightExtension


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

    _highlight_config_keys = frozenset(
        "use_pygments guess_lang css_class pygments_style noclasses linenums language_prefix".split(),
    )

    def __init__(self, md: Markdown):
        """Configure to match a `markdown.Markdown` instance.

        Arguments:
            md: The Markdown instance to read configs from.
        """
        config = {}
        for ext in md.registeredExtensions:
            if isinstance(ext, HighlightExtension) and (ext.enabled or not config):
                config = ext.getConfigs()
                break  # This one takes priority, no need to continue looking
            if isinstance(ext, CodeHiliteExtension) and not config:
                config = ext.getConfigs()
                config["language_prefix"] = config["lang_prefix"]
        self._css_class = config.pop("css_class", "highlight")
        super().__init__(**{k: v for k, v in config.items() if k in self._highlight_config_keys})

    def highlight(  # noqa: W0221 (intentionally different params, we're extending the functionality)
        self,
        src: str,
        language: Optional[str] = None,
        *,
        inline: bool = False,
        dedent: bool = True,
        linenums: Optional[bool] = None,
        **kwargs,
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
        old_linenums = self.linenums
        if linenums is not None:
            self.linenums = linenums
        try:
            result = super().highlight(src, language, inline=inline, **kwargs)
        finally:
            self.linenums = old_linenums

        if inline:
            return Markup(f'<code class="{kwargs["css_class"]} language-{language}">{result.text}</code>')
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

    def run(self, root: Element):  # noqa: D102 (ignore missing docstring)
        if not self.id_prefix:
            return
        for el in root.iter():
            id_attr = el.get("id")
            if id_attr:
                el.set("id", self.id_prefix + id_attr)

            href_attr = el.get("href")
            if href_attr and href_attr.startswith("#"):
                el.set("href", "#" + self.id_prefix + href_attr[1:])

            name_attr = el.get("name")
            if name_attr:
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

    def run(self, root: Element):  # noqa: D102 (ignore missing docstring)
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

    headings: List[Element]
    """The list (the one passed in the initializer) that is used to record the heading elements (by appending to it)."""

    def __init__(self, md: Markdown, headings: List[Element]):
        super().__init__(md)
        self.headings = headings

    def run(self, root: Element):
        for el in root.iter():
            if self.regex.fullmatch(el.tag):
                el = copy.copy(el)
                # 'toc' extension's first pass (which we require to build heading stubs/ids) also edits the HTML.
                # Undo the permalink edit so we can pass this heading to the outer pass of the 'toc' extension.
                if len(el) > 0 and el[-1].get("class") == self.md.treeprocessors["toc"].permalink_class:
                    del el[-1]
                self.headings.append(el)


class MkdocstringsInnerExtension(Extension):
    """Extension that should always be added to Markdown sub-documents that handlers request (and *only* them)."""

    def __init__(self, headings: List[Element]):
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
