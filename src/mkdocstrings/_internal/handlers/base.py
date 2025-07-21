# Base module for handlers.
#
# This module contains the base classes for implementing handlers.

from __future__ import annotations

import datetime
import importlib
import inspect
import sys
from concurrent import futures
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, ClassVar, cast
from warnings import warn
from xml.etree.ElementTree import Element, tostring

from jinja2 import Environment, FileSystemLoader
from markdown import Markdown
from markupsafe import Markup
from mkdocs.utils.cache import download_and_cache_url
from mkdocs_autorefs import AutorefsInlineProcessor, BacklinksTreeProcessor

from mkdocstrings._internal.download import _download_url_with_gz
from mkdocstrings._internal.handlers.rendering import (
    HeadingShiftingTreeprocessor,
    Highlighter,
    IdPrependingTreeprocessor,
    MkdocstringsInnerExtension,
    ParagraphStrippingTreeprocessor,
)
from mkdocstrings._internal.inventory import Inventory
from mkdocstrings._internal.loggers import get_logger, get_template_logger

# YORE: EOL 3.9: Replace block with line 4.
if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Mapping, Sequence

    from markdown import Extension
    from markdown.extensions.toc import TocTreeprocessor
    from mkdocs_autorefs import AutorefsHookInterface, Backlink

_logger = get_logger("mkdocstrings")

CollectorItem = Any
"""The type of the item returned by the `collect` method of a handler."""
HandlerConfig = Any
"""The type of the configuration of a handler."""
HandlerOptions = Any
"""The type of the options passed to a handler."""


# Autodoc instructions can appear in nested Markdown,
# so we need to keep track of the Markdown conversion layer we're in.
# Since any handler can be called from any Markdown conversion layer,
# we need to keep track of the layer globally.
# This global variable is incremented/decremented in `do_convert_markdown`,
# and used in `outer_layer`.
_markdown_conversion_layer: int = 0


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

    # YORE: Bump 1: Replace ` = ""` with `` within line.
    name: ClassVar[str] = ""
    """The handler's name, for example "python"."""

    # YORE: Bump 1: Replace ` = ""` with `` within line.
    domain: ClassVar[str] = ""
    """The handler's domain, used to register objects in the inventory, for example "py"."""

    enable_inventory: ClassVar[bool] = False
    """Whether the inventory creation is enabled."""

    # YORE: Bump 1: Remove block.
    fallback_config: ClassVar[dict] = {}
    """Fallback configuration when searching anchors for identifiers."""

    fallback_theme: ClassVar[str] = ""
    """Fallback theme to use when a template isn't found in the configured theme."""

    extra_css: str = ""
    """Extra CSS."""

    def __init__(
        self,
        # YORE: Bump 1: Remove line.
        *args: Any,
        # YORE: Bump 1: Remove line.
        **kwargs: Any,
        # YORE: Bump 1: Replace `# ` with `` within block.
        # *,
        # theme: str,
        # custom_templates: str | None,
        # mdx: Sequence[str | Extension],
        # mdx_config: Mapping[str, Any],
    ) -> None:
        """Initialize the object.

        If the given theme is not supported (it does not exist), it will look for a `fallback_theme` attribute
        in `self` to use as a fallback theme.

        Keyword Arguments:
            theme (str): The theme to use.
            custom_templates (str | None): The path to custom templates.
            mdx (list[str | Extension]): A list of Markdown extensions to use.
            mdx_config (Mapping[str, Mapping[str, Any]]): Configuration for the Markdown extensions.
        """
        # YORE: Bump 1: Remove block.
        handler = ""
        theme = ""
        custom_templates = None
        if args:
            handler, args = args[0], args[1:]
        if args:
            theme, args = args[0], args[1:]
            warn(
                "The `theme` argument must be passed as a keyword argument.",
                DeprecationWarning,
                stacklevel=2,
            )
        if args:
            custom_templates, args = args[0], args[1:]
            warn(
                "The `custom_templates` argument must be passed as a keyword argument.",
                DeprecationWarning,
                stacklevel=2,
            )
        handler = kwargs.pop("handler", handler)
        theme = kwargs.pop("theme", theme)
        custom_templates = kwargs.pop("custom_templates", custom_templates)
        mdx = kwargs.pop("mdx", None)
        mdx_config = kwargs.pop("mdx_config", None)
        if handler:
            if not self.name:
                type(self).name = handler
            warn(
                "The `handler` argument is deprecated. The handler name must be specified as a class attribute.",
                DeprecationWarning,
                stacklevel=2,
            )
        if not self.domain:
            warn(
                "The `domain` attribute must be specified as a class attribute.",
                DeprecationWarning,
                stacklevel=2,
            )
        if mdx is None:
            warn(
                "The `mdx` argument must be provided (as a keyword argument).",
                DeprecationWarning,
                stacklevel=2,
            )
        if mdx_config is None:
            warn(
                "The `mdx_config` argument must be provided (as a keyword argument).",
                DeprecationWarning,
                stacklevel=2,
            )

        self.theme = theme
        """The selected theme."""
        self.custom_templates = custom_templates
        """The path to custom templates."""
        self.mdx = mdx
        """The Markdown extensions to use."""
        self.mdx_config = mdx_config
        """The configuration for the Markdown extensions."""
        self._md: Markdown | None = None
        self._headings: list[Element] = []

        paths = []

        # add selected theme templates
        themes_dir = self.get_templates_dir(self.name)
        paths.append(themes_dir / self.theme)

        # add extended theme templates
        extended_templates_dirs = self.get_extended_templates_dirs(self.name)
        for templates_dir in extended_templates_dirs:
            paths.append(templates_dir / self.theme)

        # add fallback theme templates
        if self.fallback_theme and self.fallback_theme != self.theme:
            paths.append(themes_dir / self.fallback_theme)

            # add fallback theme of extended templates
            for templates_dir in extended_templates_dirs:
                paths.append(templates_dir / self.fallback_theme)

        for path in paths:
            css_path = path / "style.css"
            if css_path.is_file():
                self.extra_css += "\n" + css_path.read_text(encoding="utf-8")
                break

        if self.custom_templates is not None:
            paths.insert(0, Path(self.custom_templates) / self.name / self.theme)

        self.env = Environment(
            autoescape=True,
            loader=FileSystemLoader(paths),
            auto_reload=False,  # Editing a template in the middle of a build is not useful.
        )
        """The Jinja environment."""

        self.env.filters["convert_markdown"] = self.do_convert_markdown
        self.env.filters["heading"] = self.do_heading
        self.env.filters["any"] = do_any
        self.env.globals["log"] = get_template_logger(self.name)

    @property
    def md(self) -> Markdown:
        """The Markdown instance.

        Raises:
            RuntimeError: When the Markdown instance is not set yet.
        """
        if self._md is None:
            raise RuntimeError("Markdown instance not set yet")
        return self._md

    def get_inventory_urls(self) -> list[tuple[str, dict[str, Any]]]:
        """Return the URLs (and configuration options) of the inventory files to download."""
        return []

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

    def get_options(self, local_options: Mapping[str, Any]) -> HandlerOptions:
        """Get combined options.

        Override this method to customize how options are combined,
        for example by merging the global options with the local options.
        By combining options here, you don't have to do it twice in `collect` and `render`.

        Arguments:
            local_options: The local options.

        Returns:
            The combined options.
        """
        return local_options

    def collect(self, identifier: str, options: HandlerOptions) -> CollectorItem:
        """Collect data given an identifier and user configuration.

        In the implementation, you typically call a subprocess that returns JSON, and load that JSON again into
        a Python dictionary for example, though the implementation is completely free.

        Arguments:
            identifier: An identifier for which to collect data. For example, in Python,
                it would be 'mkdocstrings.handlers' to collect documentation about the handlers module.
                It can be anything that you can feed to the tool of your choice.
            options: The final configuration options.

        Returns:
            Anything you want, as long as you can feed it to the handler's `render` method.
        """
        raise NotImplementedError

    def render(self, data: CollectorItem, options: HandlerOptions, *, locale: str | None = None) -> str:
        """Render a template using provided data and configuration options.

        Arguments:
            data: The collected data to render.
            options: The final configuration options.
            locale: The locale to use for translations, if any.

        Returns:
            The rendered template as HTML.
        """
        raise NotImplementedError

    def render_backlinks(self, backlinks: Mapping[str, Iterable[Backlink]], *, locale: str | None = None) -> str:  # noqa: ARG002
        """Render backlinks.

        Parameters:
            backlinks: A mapping of identifiers to backlinks.
            locale: The locale to use for translations, if any.

        Returns:
            The rendered backlinks as HTML.
        """
        return ""

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
            import mkdocstrings_handlers  # noqa: PLC0415
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

    def get_aliases(self, identifier: str) -> tuple[str, ...]:  # noqa: ARG002
        """Return the possible aliases for a given identifier.

        Arguments:
            identifier: The identifier to get the aliases of.

        Returns:
            A tuple of strings - aliases.
        """
        return ()

    @property
    def outer_layer(self) -> bool:
        """Whether we're in the outer Markdown conversion layer."""
        return _markdown_conversion_layer == 0

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
            strip_paragraph: Whether to exclude the `<p>` tag from around the whole output.

        Returns:
            An HTML string.
        """
        global _markdown_conversion_layer  # noqa: PLW0603
        _markdown_conversion_layer += 1
        treeprocessors = self.md.treeprocessors
        treeprocessors[HeadingShiftingTreeprocessor.name].shift_by = heading_level  # type: ignore[attr-defined]
        treeprocessors[IdPrependingTreeprocessor.name].id_prefix = html_id and html_id + "--"  # type: ignore[attr-defined]
        treeprocessors[ParagraphStrippingTreeprocessor.name].strip = strip_paragraph  # type: ignore[attr-defined]
        if BacklinksTreeProcessor.name in treeprocessors:
            treeprocessors[BacklinksTreeProcessor.name].initial_id = html_id  # type: ignore[attr-defined]

        if autoref_hook:
            self.md.inlinePatterns[AutorefsInlineProcessor.name].hook = autoref_hook  # type: ignore[attr-defined]

        try:
            return Markup(self.md.convert(text))
        finally:
            treeprocessors[HeadingShiftingTreeprocessor.name].shift_by = 0  # type: ignore[attr-defined]
            treeprocessors[IdPrependingTreeprocessor.name].id_prefix = ""  # type: ignore[attr-defined]
            treeprocessors[ParagraphStrippingTreeprocessor.name].strip = False  # type: ignore[attr-defined]
            if BacklinksTreeProcessor.name in treeprocessors:
                treeprocessors[BacklinksTreeProcessor.name].initial_id = None  # type: ignore[attr-defined]
            self.md.inlinePatterns[AutorefsInlineProcessor.name].hook = None  # type: ignore[attr-defined]
            self.md.reset()
            _markdown_conversion_layer -= 1

    def do_heading(
        self,
        content: Markup,
        heading_level: int,
        *,
        role: str | None = None,
        hidden: bool = False,
        toc_label: str | None = None,
        skip_inventory: bool = False,
        **attributes: str,
    ) -> Markup:
        """Render an HTML heading and register it for the table of contents. For use inside templates.

        Arguments:
            content: The HTML within the heading.
            heading_level: The level of heading (e.g. 3 -> `h3`).
            role: An optional role for the object bound to this heading.
            hidden: If True, only register it for the table of contents, don't render anything.
            toc_label: The title to use in the table of contents ('data-toc-label' attribute).
            skip_inventory: Flag element to not be registered in the inventory (by setting a `data-skip-inventory` attribute).
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
        if skip_inventory:
            el.set("data-skip-inventory", "true")
        if role:
            el.set("data-role", role)
        if content:
            el.text = str(content).strip()
        self._headings.append(el)

        if hidden:
            return Markup('<a id="{0}"></a>').format(attributes["id"])

        # Now produce the actual HTML to be rendered. The goal is to wrap the HTML content into a heading.
        # Start with a heading that has just attributes (no text), and add a placeholder into it.
        el = Element(f"h{heading_level}", attributes)
        el.append(Element("mkdocstrings-placeholder"))
        # Tell the inner 'toc' extension to make its additions if configured so.
        toc = cast("TocTreeprocessor", self.md.treeprocessors["toc"])
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

    # YORE: Bump 1: Replace `*args: Any, **kwargs: Any` with `config: Any`.
    def update_env(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Update the Jinja environment."""
        # YORE: Bump 1: Remove line.
        warn("No need to call `super().update_env()` anymore.", DeprecationWarning, stacklevel=2)

    def _update_env(self, md: Markdown, *, config: Any | None = None) -> None:
        """Update our handler to point to our configured Markdown instance, grabbing some of the config from `md`."""
        # YORE: Bump 1: Remove block.
        if self.mdx is None and config is not None:
            self.mdx = config.get("mdx", None) or config.get("markdown_extensions", None) or ()
        if self.mdx_config is None and config is not None:
            self.mdx_config = config.get("mdx_config", None) or config.get("mdx_configs", None) or {}

        extensions: list[str | Extension] = [*self.mdx, MkdocstringsInnerExtension(self._headings)]

        new_md = Markdown(extensions=extensions, extension_configs=self.mdx_config)

        # MkDocs adds its own (required) extension that's not part of the config. Propagate it.
        if "relpath" in md.treeprocessors:
            relpath = md.treeprocessors["relpath"]
            new_relpath = type(relpath)(relpath.file, relpath.files, relpath.config)  # type: ignore[attr-defined,call-arg]
            new_md.treeprocessors.register(new_relpath, "relpath", priority=0)

        self._md = new_md

        self.env.filters["highlight"] = Highlighter(new_md).highlight

        # YORE: Bump 1: Replace block with `self.update_env(config)`.
        parameters = inspect.signature(self.update_env).parameters
        if "md" in parameters:
            warn(
                "The `update_env(md)` parameter is deprecated. Use `self.md` instead.",
                DeprecationWarning,
                stacklevel=1,
            )
            self.update_env(new_md, config)
        elif "config" in parameters:
            self.update_env(config)


class Handlers:
    """A collection of handlers.

    Do not instantiate this directly. [The plugin][mkdocstrings.MkdocstringsPlugin] will keep one instance of
    this for the purpose of caching. Use [mkdocstrings.MkdocstringsPlugin.get_handler][] for convenient access.
    """

    def __init__(
        self,
        *,
        theme: str,
        default: str,
        inventory_project: str,
        inventory_version: str = "0.0.0",
        handlers_config: dict[str, HandlerConfig] | None = None,
        custom_templates: str | None = None,
        mdx: Sequence[str | Extension] | None = None,
        mdx_config: Mapping[str, Any] | None = None,
        locale: str = "en",
        tool_config: Any,
    ) -> None:
        """Initialize the object.

        Arguments:
            theme: The theme to use.
            default: The default handler to use.
            inventory_project: The project name to use in the inventory.
            inventory_version: The project version to use in the inventory.
            handlers_config: The handlers configuration.
            custom_templates: The path to custom templates.
            mdx: A list of Markdown extensions to use.
            mdx_config: Configuration for the Markdown extensions.
            locale: The locale to use for translations.
            tool_config: Tool configuration to pass down to handlers.
        """
        self._theme = theme
        self._default = default
        self._handlers_config = handlers_config or {}
        self._custom_templates = custom_templates
        self._mdx = mdx or []
        self._mdx_config = mdx_config or {}
        self._handlers: dict[str, BaseHandler] = {}
        self._locale = locale
        self._tool_config = tool_config

        self.inventory: Inventory = Inventory(project=inventory_project, version=inventory_version)
        """The objects inventory."""

        self._inv_futures: dict[futures.Future, tuple[BaseHandler, str, Any]] = {}

    # YORE: Bump 1: Remove block.
    def get_anchors(self, identifier: str) -> tuple[str, ...]:
        """Return the canonical HTML anchor for the identifier, if any of the seen handlers can collect it.

        Arguments:
            identifier: The identifier (one that [collect][mkdocstrings.BaseHandler.collect] can accept).

        Returns:
            A tuple of strings - anchors without '#', or an empty tuple if there isn't any identifier familiar with it.
        """
        for handler in self._handlers.values():
            try:
                if hasattr(handler, "get_anchors"):
                    warn(
                        "The `get_anchors` method is deprecated. "
                        "Declare a `get_aliases` method instead, accepting a string (identifier) "
                        "instead of a collected object.",
                        DeprecationWarning,
                        stacklevel=1,
                    )
                    aliases = handler.get_anchors(handler.collect(identifier, getattr(handler, "fallback_config", {})))
                else:
                    aliases = handler.get_aliases(identifier)
            except CollectionError:
                continue
            if aliases:
                return aliases
        return ()

    def get_handler_name(self, config: dict) -> str:
        """Return the handler name defined in an "autodoc" instruction YAML configuration, or the global default handler.

        Arguments:
            config: A configuration dictionary, obtained from YAML below the "autodoc" instruction.

        Returns:
            The name of the handler to use.
        """
        return config.get("handler", self._default)

    def get_handler_config(self, name: str) -> dict:
        """Return the global configuration of the given handler.

        Arguments:
            name: The name of the handler to get the global configuration of.

        Returns:
            The global configuration of the given handler. It can be an empty dictionary.
        """
        return self._handlers_config.get(name, None) or {}

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
            An instance of a subclass of [`BaseHandler`][mkdocstrings.BaseHandler],
                as instantiated by the `get_handler` method of the handler's module.
        """
        if name not in self._handlers:
            if handler_config is None:
                handler_config = self._handlers_config.get(name, {})
            module = importlib.import_module(f"mkdocstrings_handlers.{name}")

            # YORE: Bump 1: Remove block.
            kwargs = {
                "theme": self._theme,
                "custom_templates": self._custom_templates,
                "mdx": self._mdx,
                "mdx_config": self._mdx_config,
                "handler_config": handler_config,
                "tool_config": self._tool_config,
            }
            if "config_file_path" in inspect.signature(module.get_handler).parameters:
                kwargs["config_file_path"] = self._tool_config.get("config_file_path")
                warn(
                    "The `config_file_path` argument in `get_handler` functions is deprecated. "
                    "Use `tool_config.get('config_file_path')` instead.",
                    DeprecationWarning,
                    stacklevel=1,
                )
            self._handlers[name] = module.get_handler(**kwargs)

            # YORE: Bump 1: Replace `# ` with `` within block.
            # self._handlers[name] = module.get_handler(
            #     theme=self._theme,
            #     custom_templates=self._custom_templates,
            #     mdx=self._mdx,
            #     mdx_config=self._mdx_config,
            #     handler_config=handler_config,
            #     tool_config=self._tool_config,
            # )
        return self._handlers[name]

    def _download_inventories(self) -> None:
        """Download an inventory file from an URL.

        Arguments:
            url: The URL of the inventory.
        """
        to_download: list[tuple[BaseHandler, str, Any]] = []

        for handler_name, conf in self._handlers_config.items():
            handler = self.get_handler(handler_name)

            if handler.get_inventory_urls.__func__ is BaseHandler.get_inventory_urls:  # type: ignore[attr-defined]
                if inv_configs := conf.pop("import", ()):
                    warn(
                        "mkdocstrings v1 will stop handling 'import' in handlers configuration. "
                        "Instead your handler must define a `get_inventory_urls` method "
                        "that returns a list of URLs to download. ",
                        DeprecationWarning,
                        stacklevel=1,
                    )
                    inv_configs = [{"url": inv} if isinstance(inv, str) else inv for inv in inv_configs]
                    inv_configs = [(inv.pop("url"), inv) for inv in inv_configs]
            else:
                inv_configs = handler.get_inventory_urls()

            to_download.extend((handler, url, conf) for url, conf in inv_configs)

        if to_download:
            thread_pool = futures.ThreadPoolExecutor(4)
            for handler, url, conf in to_download:
                _logger.debug("Downloading inventory from %s", url)
                future = thread_pool.submit(
                    download_and_cache_url,
                    url,
                    datetime.timedelta(days=1),
                    download=_download_url_with_gz,
                )
                self._inv_futures[future] = (handler, url, conf)
            thread_pool.shutdown(wait=False)

    def _yield_inventory_items(self) -> Iterator[tuple[str, str]]:
        if self._inv_futures:
            _logger.debug("Waiting for %s inventory download(s)", len(self._inv_futures))
            futures.wait(self._inv_futures, timeout=30)
            # Reversed order so that pages from first futures take precedence:
            for fut, (handler, url, conf) in reversed(self._inv_futures.items()):
                try:
                    yield from handler.load_inventory(BytesIO(fut.result()), url, **conf)
                except Exception as error:  # noqa: BLE001
                    _logger.error("Couldn't load inventory %s through handler '%s': %s", url, handler.name, error)  # noqa: TRY400
            self._inv_futures = {}

    @property
    def seen_handlers(self) -> Iterable[BaseHandler]:
        """Get the handlers that were encountered so far throughout the build.

        Returns:
            An iterable of instances of [`BaseHandler`][mkdocstrings.BaseHandler]
            (usable only to loop through it).
        """
        return self._handlers.values()

    def teardown(self) -> None:
        """Teardown all cached handlers and clear the cache."""
        for future in self._inv_futures:
            future.cancel()
        for handler in self.seen_handlers:
            handler.teardown()
        self._handlers.clear()
