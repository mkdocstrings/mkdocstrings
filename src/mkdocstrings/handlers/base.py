"""Base module for handlers.

This module contains the base classes for implementing handlers.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, ClassVar, Iterable, Iterator, Mapping, MutableMapping, Sequence, cast
from xml.etree.ElementTree import Element, tostring

from jinja2 import Environment, FileSystemLoader
from markdown import Markdown
from markdown.extensions.toc import TocTreeprocessor
from markupsafe import Markup
from mkdocs_autorefs.references import AutorefsInlineProcessor

from mkdocstrings.handlers.rendering import (
    HeadingShiftingTreeprocessor,
    Highlighter,
    IdPrependingTreeprocessor,
    MkdocstringsInnerExtension,
    ParagraphStrippingTreeprocessor,
)
from mkdocstrings.inventory import Inventory
from mkdocstrings.loggers import get_template_logger

# TODO: remove once support for Python 3.9 is dropped
if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

if TYPE_CHECKING:
    from mkdocs_autorefs.references import AutorefsHookInterface

CollectorItem = Any


class CollectionError(Exception):
    """An exception raised when some collection of data failed."""


class ThemeNotSupported(Exception):  # noqa: N818
    """An exception raised to tell a theme is not supported."""


def do_any(seq: Sequence, attribute: str | None = None) -> bool:
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


class BaseHandler:
    """The base handler class.

    Inherit from this class to implement a handler.

    You will have to implement the `collect` and `render` methods.
    You can also implement the `teardown` method,
    and  override the `update_env` method, to add more filters to the Jinja environment,
    making them available in your Jinja templates.

    To define a fallback theme, add a `fallback_theme` class-variable.
    To add custom CSS, add an `extra_css` variable or create an 'style.css' file beside the templates.
    """

    # TODO: Make name mandatory?
    name: str = ""
    """The handler's name, for example "python"."""
    domain: str = "default"
    """The handler's domain, used to register objects in the inventory, for example "py"."""
    enable_inventory: bool = False
    """Whether the inventory creation is enabled."""
    fallback_config: ClassVar[dict] = {}
    """Fallback configuration when searching anchors for identifiers."""
    fallback_theme: str = ""
    """Fallback theme to use when a template isn't found in the configured theme."""
    extra_css = ""
    """Extra CSS."""

    def __init__(self, handler: str, theme: str, custom_templates: str | None = None) -> None:
        """Initialize the object.

        If the given theme is not supported (it does not exist), it will look for a `fallback_theme` attribute
        in `self` to use as a fallback theme.

        Arguments:
            handler: The name of the handler.
            theme: The name of theme to use.
            custom_templates: Directory containing custom templates.
        """
        paths = []

        # add selected theme templates
        themes_dir = self.get_templates_dir(handler)
        paths.append(themes_dir / theme)

        # add extended theme templates
        extended_templates_dirs = self.get_extended_templates_dirs(handler)
        for templates_dir in extended_templates_dirs:
            paths.append(templates_dir / theme)

        # add fallback theme templates
        if self.fallback_theme and self.fallback_theme != theme:
            paths.append(themes_dir / self.fallback_theme)

            # add fallback theme of extended templates
            for templates_dir in extended_templates_dirs:
                paths.append(templates_dir / self.fallback_theme)

        for path in paths:
            css_path = path / "style.css"
            if css_path.is_file():
                self.extra_css += "\n" + css_path.read_text(encoding="utf-8")
                break

        if custom_templates is not None:
            paths.insert(0, Path(custom_templates) / handler / theme)

        self.env = Environment(
            autoescape=True,
            loader=FileSystemLoader(paths),
            auto_reload=False,  # Editing a template in the middle of a build is not useful.
        )
        self.env.filters["any"] = do_any
        self.env.globals["log"] = get_template_logger(self.name)

        self._headings: list[Element] = []
        self._md: Markdown = None  # type: ignore[assignment]  # To be populated in `update_env`.

    @classmethod
    def load_inventory(
        cls,
        in_file: BinaryIO,  # noqa: ARG003
        url: str,  # noqa: ARG003
        base_url: str | None = None,  # noqa: ARG003
        **kwargs: Any,  # noqa: ARG003
    ) -> Iterator[tuple[str, str]]:
        """Yield items and their URLs from an inventory file streamed from `in_file`.

        Arguments:
            in_file: The binary file-like object to read the inventory from.
            url: The URL that this file is being streamed from (used to guess `base_url`).
            base_url: The URL that this inventory's sub-paths are relative to.
            **kwargs: Ignore additional arguments passed from the config.

        Yields:
            Tuples of (item identifier, item URL).
        """
        yield from ()

    def collect(self, identifier: str, config: MutableMapping[str, Any]) -> CollectorItem:
        """Collect data given an identifier and user configuration.

        In the implementation, you typically call a subprocess that returns JSON, and load that JSON again into
        a Python dictionary for example, though the implementation is completely free.

        Arguments:
            identifier: An identifier for which to collect data. For example, in Python,
                it would be 'mkdocstrings.handlers' to collect documentation about the handlers module.
                It can be anything that you can feed to the tool of your choice.
            config: The handler's configuration options.

        Returns:
            Anything you want, as long as you can feed it to the handler's `render` method.
        """
        raise NotImplementedError

    def render(self, data: CollectorItem, config: Mapping[str, Any]) -> str:
        """Render a template using provided data and configuration options.

        Arguments:
            data: The collected data to render.
            config: The handler's configuration options.

        Returns:
            The rendered template as HTML.
        """
        raise NotImplementedError

    def teardown(self) -> None:
        """Teardown the handler.

        This method should be implemented to, for example, terminate a subprocess
        that was started when creating the handler instance.
        """

    def get_templates_dir(self, handler: str | None = None) -> Path:
        """Return the path to the handler's templates directory.

        Override to customize how the templates directory is found.

        Arguments:
            handler: The name of the handler to get the templates directory of.

        Raises:
            ModuleNotFoundError: When no such handler is installed.
            FileNotFoundError: When the templates directory cannot be found.

        Returns:
            The templates directory path.
        """
        handler = handler or self.name
        try:
            import mkdocstrings_handlers
        except ModuleNotFoundError as error:
            raise ModuleNotFoundError(f"Handler '{handler}' not found, is it installed?") from error

        for path in mkdocstrings_handlers.__path__:
            theme_path = Path(path, handler, "templates")
            if theme_path.exists():
                return theme_path

        raise FileNotFoundError(f"Can't find 'templates' folder for handler '{handler}'")

    def get_extended_templates_dirs(self, handler: str) -> list[Path]:
        """Load template extensions for the given handler, return their templates directories.

        Arguments:
            handler: The name of the handler to get the extended templates directory of.

        Returns:
            The extensions templates directories.
        """
        discovered_extensions = entry_points(group=f"mkdocstrings.{handler}.templates")
        return [extension.load()() for extension in discovered_extensions]

    def get_anchors(self, data: CollectorItem) -> tuple[str, ...]:  # noqa: ARG002
        """Return the possible identifiers (HTML anchors) for a collected item.

        Arguments:
            data: The collected data.

        Returns:
            The HTML anchors (without '#'), or an empty tuple if this item doesn't have an anchor.
        """
        return ()

    def do_convert_markdown(
        self,
        text: str,
        heading_level: int,
        html_id: str = "",
        *,
        strip_paragraph: bool = False,
        autoref_hook: AutorefsHookInterface | None = None,
    ) -> Markup:
        """Render Markdown text; for use inside templates.

        Arguments:
            text: The text to convert.
            heading_level: The base heading level to start all Markdown headings from.
            html_id: The HTML id of the element that's considered the parent of this element.
            strip_paragraph: Whether to exclude the <p> tag from around the whole output.

        Returns:
            An HTML string.
        """
        treeprocessors = self._md.treeprocessors
        treeprocessors[HeadingShiftingTreeprocessor.name].shift_by = heading_level  # type: ignore[attr-defined]
        treeprocessors[IdPrependingTreeprocessor.name].id_prefix = html_id and html_id + "--"  # type: ignore[attr-defined]
        treeprocessors[ParagraphStrippingTreeprocessor.name].strip = strip_paragraph  # type: ignore[attr-defined]

        if autoref_hook:
            self._md.inlinePatterns[AutorefsInlineProcessor.name].hook = autoref_hook  # type: ignore[attr-defined]

        try:
            return Markup(self._md.convert(text))
        finally:
            treeprocessors[HeadingShiftingTreeprocessor.name].shift_by = 0  # type: ignore[attr-defined]
            treeprocessors[IdPrependingTreeprocessor.name].id_prefix = ""  # type: ignore[attr-defined]
            treeprocessors[ParagraphStrippingTreeprocessor.name].strip = False  # type: ignore[attr-defined]
            self._md.inlinePatterns[AutorefsInlineProcessor.name].hook = None  # type: ignore[attr-defined]
            self._md.reset()

    def do_heading(
        self,
        content: Markup,
        heading_level: int,
        *,
        role: str | None = None,
        hidden: bool = False,
        toc_label: str | None = None,
        **attributes: str,
    ) -> Markup:
        """Render an HTML heading and register it for the table of contents. For use inside templates.

        Arguments:
            content: The HTML within the heading.
            heading_level: The level of heading (e.g. 3 -> `h3`).
            role: An optional role for the object bound to this heading.
            hidden: If True, only register it for the table of contents, don't render anything.
            toc_label: The title to use in the table of contents ('data-toc-label' attribute).
            **attributes: Any extra HTML attributes of the heading.

        Returns:
            An HTML string.
        """
        # Produce a heading element that will be used later, in `AutoDocProcessor.run`, to:
        # - register it in the ToC: right now we're in the inner Markdown conversion layer,
        #   so we have to bubble up the information to the outer Markdown conversion layer,
        #   for the ToC extension to pick it up.
        # - register it in autorefs: right now we don't know what page is being rendered,
        #   so we bubble up the information again to where autorefs knows the page,
        #   and can correctly register the heading anchor (id) to its full URL.
        # - register it in the objects inventory: same as for autorefs,
        #   we don't know the page here, or the handler (and its domain),
        #   so we bubble up the information to where the mkdocstrings extension knows that.
        el = Element(f"h{heading_level}", attributes)
        if toc_label is None:
            toc_label = content.unescape() if isinstance(content, Markup) else content
        el.set("data-toc-label", toc_label)
        if role:
            el.set("data-role", role)
        self._headings.append(el)

        if hidden:
            return Markup('<a id="{0}"></a>').format(attributes["id"])

        # Now produce the actual HTML to be rendered. The goal is to wrap the HTML content into a heading.
        # Start with a heading that has just attributes (no text), and add a placeholder into it.
        el = Element(f"h{heading_level}", attributes)
        el.append(Element("mkdocstrings-placeholder"))
        # Tell the inner 'toc' extension to make its additions if configured so.
        toc = cast(TocTreeprocessor, self._md.treeprocessors["toc"])
        if toc.use_anchors:
            toc.add_anchor(el, attributes["id"])
        if toc.use_permalinks:
            toc.add_permalink(el, attributes["id"])

        # The content we received is HTML, so it can't just be inserted into the tree. We had marked the middle
        # of the heading with a placeholder that can never occur (text can't directly contain angle brackets).
        # Now this HTML wrapper can be "filled" by replacing the placeholder.
        html_with_placeholder = tostring(el, encoding="unicode")
        assert (  # noqa: S101
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

    def update_env(self, md: Markdown, config: dict) -> None:  # noqa: ARG002
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

    def _update_env(self, md: Markdown, config: dict) -> None:
        """Update our handler to point to our configured Markdown instance, grabbing some of the config from `md`."""
        extensions = config["mdx"] + [MkdocstringsInnerExtension(self._headings)]

        new_md = Markdown(extensions=extensions, extension_configs=config["mdx_configs"])
        # MkDocs adds its own (required) extension that's not part of the config. Propagate it.
        if "relpath" in md.treeprocessors:
            new_md.treeprocessors.register(md.treeprocessors["relpath"], "relpath", priority=0)

        self.update_env(new_md, config)


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
        self._handlers: dict[str, BaseHandler] = {}
        self.inventory: Inventory = Inventory(project=self._config["mkdocs"]["site_name"])

    def get_anchors(self, identifier: str) -> tuple[str, ...]:
        """Return the canonical HTML anchor for the identifier, if any of the seen handlers can collect it.

        Arguments:
            identifier: The identifier (one that [collect][mkdocstrings.handlers.base.BaseHandler.collect] can accept).

        Returns:
            A tuple of strings - anchors without '#', or an empty tuple if there isn't any identifier familiar with it.
        """
        for handler in self._handlers.values():
            fallback_config = getattr(handler, "fallback_config", {})
            try:
                anchors = handler.get_anchors(handler.collect(identifier, fallback_config))
            except CollectionError:
                continue
            if anchors:
                return anchors
        return ()

    def get_handler_name(self, config: dict) -> str:
        """Return the handler name defined in an "autodoc" instruction YAML configuration, or the global default handler.

        Arguments:
            config: A configuration dictionary, obtained from YAML below the "autodoc" instruction.

        Returns:
            The name of the handler to use.
        """
        global_config = self._config["mkdocstrings"]
        if "handler" in config:
            return config["handler"]
        return global_config["default_handler"]

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

    def get_handler(self, name: str, handler_config: dict | None = None) -> BaseHandler:
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
            handler_config.update(self._config)
            module = importlib.import_module(f"mkdocstrings_handlers.{name}")
            self._handlers[name] = module.get_handler(
                theme=self._config["theme_name"],
                custom_templates=self._config["mkdocstrings"]["custom_templates"],
                config_file_path=self._config["mkdocs"]["config_file_path"],
                **handler_config,
            )
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
            handler.teardown()
        self._handlers.clear()
