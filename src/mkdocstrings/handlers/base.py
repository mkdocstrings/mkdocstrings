"""
Base module for handlers.

This module contains the base classes for implementing collectors, renderers, and the combination of the two: handlers.

It also provides two methods:

- `get_handler`, that will cache handlers into the `HANDLERS_CACHE` dictionary.
- `teardown`, that will teardown all the cached handlers, and then clear the cache.
"""

import functools
import importlib
import re
import textwrap
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Sequence
from xml.etree.ElementTree import Element  # noqa: S405 (we choose to trust the XML input)

from jinja2 import Environment, FileSystemLoader
from markdown import Markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markupsafe import Markup
from pymdownx.highlight import Highlight

from mkdocstrings.loggers import get_template_logger

handlers_cache: Dict[str, Any] = {}
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


class CollectionError(Exception):
    """An exception raised when some collection of data failed."""


class ThemeNotSupported(Exception):
    """An exception raised to tell a theme is not supported."""


def do_highlight(
    src: str,
    guess_lang: bool = False,
    language: str = None,
    inline: bool = False,
    dedent: bool = True,
    line_nums: bool = False,
    line_start: int = 1,
) -> str:
    """
    Highlight a code-snippet.

    This function is used as a filter in Jinja templates.

    Arguments:
        src: The code to highlight.
        guess_lang: Whether to guess the language or not.
        language: Explicitly tell what language to use for highlighting.
        inline: Whether to do inline highlighting.
        dedent: Whether to dedent the code before highlighting it or not.
        line_nums: Whether to add line numbers in the result.
        line_start: The line number to start with.

    Returns:
        The highlighted code as HTML text, marked safe (not escaped for HTML).
    """
    if dedent:
        src = textwrap.dedent(src)

    highlighter = Highlight(use_pygments=True, guess_lang=guess_lang, linenums=line_nums)
    result = highlighter.highlight(src=src, language=language, linestart=line_start, inline=inline)

    if inline:
        return Markup(f'<code class="highlight language-{language}">{result.text}</code>')
    return Markup(result)


def do_js_highlight(
    src: str,
    guess_lang: bool = False,  # noqa: W0613 (we must accept the same parameters as do_highlight)
    language: str = None,
    inline: bool = False,
    dedent: bool = True,
    line_nums: bool = False,  # noqa: W0613
    line_start: int = 1,  # noqa: W0613
) -> str:
    """
    Prepare a code-snippet for JS highlighting.

    This function is used as a filter in Jinja templates.

    Arguments:
        src: The code to highlight.
        guess_lang: Whether to guess the language or not.
        language: Explicitly tell what language to use for highlighting.
        inline: Whether to do inline highlighting.
        dedent: Whether to dedent the code before highlighting it or not.
        line_nums: Whether to add line numbers in the result.
        line_start: The line number to start with.

    Returns:
        The code properly wrapped for later highlighting by JavaScript.
    """
    if dedent:
        src = textwrap.dedent(src)
    if inline:
        src = re.sub(r"\n\s*", "", src)
        return Markup(f'<code class="highlight">{src}</code>')
    return Markup(f'<div class="highlight {language or ""}"><pre><code>\n{src}\n</code></pre></div>')


def do_any(seq: Sequence, attribute: str = None) -> bool:
    """
    Check if at least one of the item in the sequence evaluates to true.

    The `any` builtin as a filter for Jinja templates.

    Arguments:
        seq: An iterable object.
        attribute: The attribute name to use on each object of the iterable.

    Returns:
        A boolean telling if any object of the iterable evaluated to True.
    """
    if attribute is None:
        return any(seq)
    return any(_[attribute] for _ in seq)


def do_convert_markdown(md: Markdown, text: str, heading_level: int, html_id: str = "") -> Markup:
    """
    Render Markdown text; for use inside templates.

    Arguments:
        md: A `markdown.Markdown` instance.
        text: The text to convert.
        heading_level: The base heading level to start all Markdown headings from.
        html_id: The HTML id of the element that's considered the parent of this element.

    Returns:
        An HTML string.
    """
    md.treeprocessors["mkdocstrings_headings"].shift_by = heading_level
    md.treeprocessors["mkdocstrings_ids"].id_prefix = html_id and html_id + "--"
    try:
        return Markup(md.convert(text))
    finally:
        md.treeprocessors["mkdocstrings_headings"].shift_by = 0
        md.treeprocessors["mkdocstrings_ids"].id_prefix = ""
        md.reset()


class BaseRenderer(ABC):
    """
    The base renderer class.

    Inherit from this class to implement a renderer.

    You will have to implement the `render` method.
    You can also override the `update_env` method, to add more filters to the Jinja environment,
    making them available in your Jinja templates.

    To define a fallback theme, add a `FALLBACK_THEME` class-variable.
    """

    fallback_theme: str = ""

    def __init__(self, directory: str, theme: str, custom_templates: Optional[str] = None) -> None:
        """
        Initialize the object.

        If the given theme is not supported (it does not exist), it will look for a `fallback_theme` attribute
        in `self` to use as a fallback theme.

        Arguments:
            directory: The name of the directory containing the themes for this renderer.
            theme: The name of theme to use.
            custom_templates: Directory containing custom templates.
        """
        paths = []

        if custom_templates is not None:
            paths.append(Path(custom_templates) / directory / theme)

        themes_dir = TEMPLATES_DIR / directory

        paths.append(themes_dir / theme)

        if self.fallback_theme != "":
            paths.append(themes_dir / self.fallback_theme)

        self.env = Environment(
            autoescape=True,
            loader=FileSystemLoader(paths),
            auto_reload=False,  # Editing a template in the middle of a build is not useful.
        )  # type: ignore
        self.env.filters["any"] = do_any
        self.env.globals["log"] = get_template_logger()

        if theme == "readthedocs":
            highlight_function = do_js_highlight
        else:
            highlight_function = do_highlight

        self.env.filters["highlight"] = highlight_function

    @abstractmethod
    def render(self, data: Any, config: dict) -> str:
        """
        Render a template using provided data and configuration options.

        Arguments:
            data: The collected data to render.
            config: The rendering options.

        Returns:
            The rendered template as HTML.
        """  # noqa: DAR202 (excess return section)

    def update_env(self, md: Markdown, config: dict) -> None:
        """
        Update the Jinja environment.

        Arguments:
            md: The Markdown instance. Useful to add functions able to convert Markdown into the environment filters.
            config: Configuration options for `mkdocs` and `mkdocstrings`, read from `mkdocs.yml`. See the source code
                of [mkdocstrings.plugin.MkdocstringsPlugin.on_config][] to see what's in this dictionary.
        """
        extensions = config["mdx"] + [ShiftHeadingsExtension(), PrefixIdsExtension()]
        configs = dict(config["mdx_configs"])
        # Prevent a bug that happens due to treeprocessors running on the same fragment both as the inner doc and as
        # part of the re-integrated doc. Namely, the permalink '¶' would be appended twice. This is the only known
        # non-idempotent effect of an extension, so specifically prevent it on the inner doc.
        try:
            configs["toc"] = dict(configs["toc"], permalink=False)
        except KeyError:
            pass

        md = Markdown(extensions=extensions, extension_configs=configs)

        self.env.filters["convert_markdown"] = functools.partial(do_convert_markdown, md)


class BaseCollector(ABC):
    """
    The base collector class.

    Inherit from this class to implement a collector.

    You will have to implement the `collect` method.
    You can also implement the `teardown` method.
    """

    @abstractmethod
    def collect(self, identifier: str, config: dict) -> Any:
        """
        Collect data given an identifier and selection configuration.

        In the implementation, you typically call a subprocess that returns JSON, and load that JSON again into
        a Python dictionary for example, though the implementation is completely free.

        Arguments:
            identifier: An identifier for which to collect data. For example, in Python,
                it would be 'mkdocstrings.handlers' to collect documentation about the handlers module.
                It can be anything that you can feed to the tool of your choice.
            config: Configuration options for the tool you use to collect data. Typically called "selection" because
                these options modify how the objects or documentation are "selected" in the source code.

        Returns:
            Anything you want, as long as you can feed it to the renderer's `render` method.
        """  # noqa: DAR202 (excess return section)

    def teardown(self) -> None:
        """
        Teardown the collector.

        This method should be implemented to, for example, terminate a subprocess
        that was started when creating the collector instance.
        """


class BaseHandler:
    """
    The base handler class.

    Inherit from this class to implement a handler.

    It's usually just a combination of a collector and a renderer, but you can make it as complex as you need.
    """

    def __init__(self, collector: BaseCollector, renderer: BaseRenderer) -> None:
        """
        Initialize the object.

        Arguments:
            collector: A collector instance.
            renderer: A renderer instance.
        """
        self.collector = collector
        self.renderer = renderer


class Handlers:
    """
    A collection of handlers.

    Do not instantiate this directly. [The plugin][mkdocstrings.plugin.MkdocstringsPlugin] will keep one instance of
    this for the purpose of caching. Use [mkdocstrings.plugin.MkdocstringsPlugin.get_handler][] for convenient access.
    """

    def __init__(self, config: dict) -> None:
        """
        Initialize the object.

        Arguments:
            config: Configuration options for `mkdocs` and `mkdocstrings`, read from `mkdocs.yml`. See the source code
                of [mkdocstrings.plugin.MkdocstringsPlugin.on_config][] to see what's in this dictionary.
        """
        self._config = config
        self._handlers: Dict[str, BaseHandler] = {}

    def get_handler_name(self, config: dict) -> str:
        """
        Return the handler name defined in an "autodoc" instruction YAML configuration, or the global default handler.

        Arguments:
            config: A configuration dictionary, obtained from YAML below the "autodoc" instruction.

        Returns:
            The name of the handler to use.
        """
        config = self._config["mkdocstrings"]
        if "handler" in config:
            return config["handler"]
        return config["default_handler"]

    def get_handler_config(self, name: str) -> dict:
        """
        Return the global configuration of the given handler.

        Arguments:
            name: The name of the handler to get the global configuration of.

        Returns:
            The global configuration of the given handler. It can be an empty dictionary.
        """
        handlers = self._config["mkdocstrings"].get("handlers", {})
        if handlers:
            return handlers.get(name, {})
        return {}

    def get_handler(self, name: str, handler_config: Optional[dict] = None) -> BaseHandler:
        """
        Get a handler thanks to its name.

        This function dynamically imports a module named "mkdocstrings.handlers.NAME", calls its
        `get_handler` method to get an instance of a handler, and caches it in dictionary.
        It means that during one run (for each reload when serving, or once when building),
        a handler is instantiated only once, and reused for each "autodoc" instruction asking for it.

        Arguments:
            name: The name of the handler. Really, it's the name of the Python module holding it.
            handler_config: Configuration passed to the handler.

        Returns:
            An instance of a subclass of [`BaseHandler`][mkdocstrings.handlers.base.BaseHandler],
            as instantiated by the `get_handler` method of the handler's module.
        """
        if name not in self._handlers:
            if handler_config is None:
                handler_config = self.get_handler_config(name)
            module = importlib.import_module(f"mkdocstrings.handlers.{name}")
            self._handlers[name] = module.get_handler(
                self._config["theme_name"],
                self._config["mkdocstrings"]["custom_templates"],
                **handler_config,
            )  # type: ignore
        return self._handlers[name]

    def teardown(self):
        """Teardown all cached handlers and clear the cache."""
        for handler in self._handlers.values():
            handler.collector.teardown()
        self._handlers.clear()


class _IdPrependingTreeprocessor(Treeprocessor):
    def __init__(self, md, id_prefix: str):
        super().__init__(md)
        self.id_prefix = id_prefix

    def run(self, root: Element):
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


class PrefixIdsExtension(Extension):
    """Prepend the configured prefix to IDs of all HTML elements."""

    treeprocessor_priority = 4  # Right after 'toc' (needed because that extension adds ids to headers).

    def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802 (casing: parent method's name)
        """
        Register the extension, with a treeprocessor under the name 'mkdocstrings_ids'.

        Arguments:
            md: A `markdown.Markdown` instance.
        """
        md.registerExtension(self)
        md.treeprocessors.register(
            _IdPrependingTreeprocessor(md, ""),
            "mkdocstrings_ids",
            self.treeprocessor_priority,
        )


class _HeadingShiftingTreeprocessor(Treeprocessor):
    def __init__(self, md, shift_by: int):
        super().__init__(md)
        self.shift_by = shift_by

    def run(self, root: Element):
        if not self.shift_by:
            return
        for el in root.iter():
            match = re.fullmatch(r"([Hh])([1-6])", el.tag)
            if match:
                level = int(match[2]) + self.shift_by
                level = max(1, min(level, 6))
                el.tag = f"{match[1]}{level}"


class ShiftHeadingsExtension(Extension):
    """Shift levels of all Markdown headings according to the configured base level."""

    treeprocessor_priority = 12

    def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802 (casing: parent method's name)
        """
        Register the extension, with a treeprocessor under the name 'mkdocstrings_headings'.

        Arguments:
            md: A `markdown.Markdown` instance.
        """
        md.registerExtension(self)
        md.treeprocessors.register(
            _HeadingShiftingTreeprocessor(md, 0),
            "mkdocstrings_headings",
            self.treeprocessor_priority,
        )
