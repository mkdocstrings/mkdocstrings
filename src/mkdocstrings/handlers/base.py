"""Base module for handlers.

This module contains the base classes for implementing collectors, renderers, and the combination of the two: handlers.

It also provides two methods:

- `get_handler`, that will cache handlers into the `HANDLERS_CACHE` dictionary.
- `teardown`, that will teardown all the cached handlers, and then clear the cache.
"""

import importlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Sequence
from xml.etree.ElementTree import Element, tostring

from jinja2 import Environment, FileSystemLoader
from markdown import Markdown
from markupsafe import Markup

from mkdocstrings.handlers.rendering import (
    HeadingShiftingTreeprocessor,
    Highlighter,
    IdPrependingTreeprocessor,
    MkdocstringsInnerExtension,
)
from mkdocstrings.loggers import get_template_logger

CollectorItem = Any

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


class CollectionError(Exception):
    """An exception raised when some collection of data failed."""


class ThemeNotSupported(Exception):
    """An exception raised to tell a theme is not supported."""


def do_any(seq: Sequence, attribute: str = None) -> bool:
    """Check if at least one of the item in the sequence evaluates to true.

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


class BaseRenderer(ABC):
    """The base renderer class.

    Inherit from this class to implement a renderer.

    You will have to implement the `render` method.
    You can also override the `update_env` method, to add more filters to the Jinja environment,
    making them available in your Jinja templates.

    To define a fallback theme, add a `fallback_theme` class-variable.
    To add custom CSS, add an `extra_css` variable or create an 'style.css' file beside the templates.
    """

    fallback_theme: str = ""
    extra_css = ""

    def __init__(self, directory: str, theme: str, custom_templates: Optional[str] = None) -> None:
        """Initialize the object.

        If the given theme is not supported (it does not exist), it will look for a `fallback_theme` attribute
        in `self` to use as a fallback theme.

        Arguments:
            directory: The name of the directory containing the themes for this renderer.
            theme: The name of theme to use.
            custom_templates: Directory containing custom templates.
        """
        paths = []

        themes_dir = TEMPLATES_DIR / directory

        paths.append(themes_dir / theme)

        if self.fallback_theme:
            paths.append(themes_dir / self.fallback_theme)

        for path in paths:
            css_path = path / "style.css"
            if css_path.is_file():
                self.extra_css += "\n" + css_path.read_text(encoding="utf-8")
                break

        if custom_templates is not None:
            paths.insert(0, Path(custom_templates) / directory / theme)

        self.env = Environment(
            autoescape=True,
            loader=FileSystemLoader(paths),
            auto_reload=False,  # Editing a template in the middle of a build is not useful.
        )  # type: ignore
        self.env.filters["any"] = do_any
        self.env.globals["log"] = get_template_logger()

        self._headings = []
        self._md = None  # To be populated in `update_env`.

    @abstractmethod
    def render(self, data: CollectorItem, config: dict) -> str:
        """Render a template using provided data and configuration options.

        Arguments:
            data: The collected data to render.
            config: The rendering options.

        Returns:
            The rendered template as HTML.
        """  # noqa: DAR202 (excess return section)

    def get_anchor(self, data: CollectorItem) -> Optional[str]:
        """Return the canonical identifier (HTML anchor) for a collected item.

        This must match what the renderer would've actually rendered,
        e.g. if rendering the item contains `<h2 id="foo">...` then the return value should be "foo".

        Arguments:
            data: The collected data.

        Returns:
            The HTML anchor (without '#') as a string, or None if this item doesn't have an anchor.
        """  # noqa: DAR202 (excess return section)

    def do_convert_markdown(self, text: str, heading_level: int, html_id: str = "") -> Markup:
        """Render Markdown text; for use inside templates.

        Arguments:
            text: The text to convert.
            heading_level: The base heading level to start all Markdown headings from.
            html_id: The HTML id of the element that's considered the parent of this element.

        Returns:
            An HTML string.
        """
        treeprocessors = self._md.treeprocessors
        treeprocessors[HeadingShiftingTreeprocessor.name].shift_by = heading_level
        treeprocessors[IdPrependingTreeprocessor.name].id_prefix = html_id and html_id + "--"
        try:
            return Markup(self._md.convert(text))
        finally:
            treeprocessors[HeadingShiftingTreeprocessor.name].shift_by = 0
            treeprocessors[IdPrependingTreeprocessor.name].id_prefix = ""
            self._md.reset()

    def do_heading(
        self,
        content: str,
        heading_level: int,
        *,
        hidden: bool = False,
        toc_label: Optional[str] = None,
        **attributes: str,
    ) -> Markup:
        """Render an HTML heading and register it for the table of contents. For use inside templates.

        Arguments:
            content: The HTML within the heading.
            heading_level: The level of heading (e.g. 3 -> `h3`).
            hidden: If True, only register it for the table of contents, don't render anything.
            toc_label: The title to use in the table of contents ('data-toc-label' attribute).
            attributes: Any extra HTML attributes of the heading.

        Returns:
            An HTML string.
        """
        # First, produce the "fake" heading, for ToC only.
        el = Element(f"h{heading_level}", attributes)
        if toc_label is None:
            toc_label = content.unescape() if isinstance(el, Markup) else content
        el.set("data-toc-label", toc_label)
        self._headings.append(el)

        if hidden:
            return Markup('<a id="{0}"></a>').format(attributes["id"])

        # Now produce the actual HTML to be rendered. The goal is to wrap the HTML content into a heading.
        # Start with a heading that has just attributes (no text), and add a placeholder into it.
        el = Element(f"h{heading_level}", attributes)
        el.append(Element("mkdocstrings-placeholder"))
        # Tell the 'toc' extension to make its additions if configured so.
        toc = self._md.treeprocessors["toc"]
        if toc.use_anchors:
            toc.add_anchor(el, attributes["id"])
        if toc.use_permalinks:
            toc.add_permalink(el, attributes["id"])

        # The content we received is HTML, so it can't just be inserted into the tree. We had marked the middle
        # of the heading with a placeholder that can never occur (text can't directly contain angle brackets).
        # Now this HTML wrapper can be "filled" by replacing the placeholder.
        html_with_placeholder = tostring(el, encoding="unicode")
        assert (
            html_with_placeholder.count("<mkdocstrings-placeholder />") == 1
        ), f"Bug in mkdocstrings: failed to replace in {html_with_placeholder!r}"
        html = html_with_placeholder.replace("<mkdocstrings-placeholder />", content)
        return Markup(html)

    def get_headings(self) -> Sequence[Element]:
        """Return and clear the headings gathered so far.

        Returns:
            A list of HTML elements.
        """
        result = list(self._headings)
        self._headings.clear()
        return result

    def update_env(self, md: Markdown, config: dict) -> None:  # noqa: W0613 (unused argument 'config')
        """Update the Jinja environment.

        Arguments:
            md: The Markdown instance. Useful to add functions able to convert Markdown into the environment filters.
            config: Configuration options for `mkdocs` and `mkdocstrings`, read from `mkdocs.yml`. See the source code
                of [mkdocstrings.plugin.MkdocstringsPlugin.on_config][] to see what's in this dictionary.
        """
        self._md = md
        self.env.filters["highlight"] = Highlighter(md).highlight
        self.env.filters["convert_markdown"] = self.do_convert_markdown
        self.env.filters["heading"] = self.do_heading

    def _update_env(self, md: Markdown, config: dict):
        extensions = config["mdx"] + [MkdocstringsInnerExtension(self._headings)]

        new_md = Markdown(extensions=extensions, extension_configs=config["mdx_configs"])
        # MkDocs adds its own (required) extension that's not part of the config. Propagate it.
        if "relpath" in md.treeprocessors:
            new_md.treeprocessors.register(md.treeprocessors["relpath"], "relpath", priority=0)

        self.update_env(new_md, config)


class BaseCollector(ABC):
    """The base collector class.

    Inherit from this class to implement a collector.

    You will have to implement the `collect` method.
    You can also implement the `teardown` method.
    """

    @abstractmethod
    def collect(self, identifier: str, config: dict) -> CollectorItem:
        """Collect data given an identifier and selection configuration.

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
        """Teardown the collector.

        This method should be implemented to, for example, terminate a subprocess
        that was started when creating the collector instance.
        """


class BaseHandler:
    """The base handler class.

    Inherit from this class to implement a handler.

    It's usually just a combination of a collector and a renderer, but you can make it as complex as you need.
    """

    def __init__(self, collector: BaseCollector, renderer: BaseRenderer) -> None:
        """Initialize the object.

        Arguments:
            collector: A collector instance.
            renderer: A renderer instance.
        """
        self.collector = collector
        self.renderer = renderer


class Handlers:
    """A collection of handlers.

    Do not instantiate this directly. [The plugin][mkdocstrings.plugin.MkdocstringsPlugin] will keep one instance of
    this for the purpose of caching. Use [mkdocstrings.plugin.MkdocstringsPlugin.get_handler][] for convenient access.
    """

    def __init__(self, config: dict) -> None:
        """Initialize the object.

        Arguments:
            config: Configuration options for `mkdocs` and `mkdocstrings`, read from `mkdocs.yml`. See the source code
                of [mkdocstrings.plugin.MkdocstringsPlugin.on_config][] to see what's in this dictionary.
        """
        self._config = config
        self._handlers: Dict[str, BaseHandler] = {}

    def get_anchor(self, identifier: str) -> Optional[str]:
        """Return the canonical HTML anchor for the identifier, if any of the seen handlers can collect it.

        Arguments:
            identifier: The identifier (one that [collect][mkdocstrings.handlers.base.BaseCollector.collect] can accept).

        Returns:
            A string - anchor without '#', or None if there isn't any identifier familiar with it.
        """
        for handler in self._handlers.values():
            try:
                anchor = handler.renderer.get_anchor(handler.collector.collect(identifier, {}))
            except CollectionError:
                continue
            else:
                if anchor is not None:
                    return anchor
        return None

    def get_handler_name(self, config: dict) -> str:
        """Return the handler name defined in an "autodoc" instruction YAML configuration, or the global default handler.

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
        """Return the global configuration of the given handler.

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
        """Get a handler thanks to its name.

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

    @property
    def seen_handlers(self) -> Iterable[BaseHandler]:
        """Get the handlers that were encountered so far throughout the build.

        Returns:
            An iterable of instances of [`BaseHandler`][mkdocstrings.handlers.base.BaseHandler]
            (usable only to loop through it).
        """
        return self._handlers.values()

    def teardown(self) -> None:
        """Teardown all cached handlers and clear the cache."""
        for handler in self.seen_handlers:
            handler.collector.teardown()
        self._handlers.clear()
