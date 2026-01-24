# This module holds the code of the Markdown extension responsible for matching "autodoc" instructions.
#
# The extension is composed of a Markdown [block processor](https://python-markdown.github.io/extensions/api/#blockparser)
# that matches indented blocks starting with a line like `::: identifier`.
#
# For each of these blocks, it uses a [handler][mkdocstrings.BaseHandler] to collect documentation about
# the given identifier and render it with Jinja templates.
#
# Both the collection and rendering process can be configured by adding YAML configuration under the "autodoc"
# instruction:
#
# ```yaml
# ::: some.identifier
#     handler: python
#     options:
#       option1: value1
#       option2:
#       - value2a
#       - value2b
#       option_x: etc
# ```

from __future__ import annotations

import re
from functools import partial
from inspect import signature
from typing import TYPE_CHECKING, Any
from xml.etree.ElementTree import Element

import yaml
from jinja2.exceptions import TemplateNotFound
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from mkdocs.exceptions import PluginError
from mkdocs_autorefs import AutorefsConfig, AutorefsExtension, AutorefsPlugin

from mkdocstrings._internal.handlers.base import BaseHandler, CollectionError, CollectorItem, Handlers
from mkdocstrings._internal.loggers import get_logger

if TYPE_CHECKING:
    from collections.abc import MutableSequence

    from markdown import Markdown


_logger = get_logger("mkdocstrings")


class AutoDocProcessor(BlockProcessor):
    """Our "autodoc" Markdown block processor.

    It has a [`test` method][mkdocstrings.AutoDocProcessor.test] that tells if a block matches a criterion,
    and a [`run` method][mkdocstrings.AutoDocProcessor.run] that processes it.

    It also has utility methods allowing to get handlers and their configuration easily, useful when processing
    a matched block.
    """

    regex = re.compile(r"^(?P<heading>#{1,6} *|)::: ?(?P<name>.+?) *$", flags=re.MULTILINE)
    """The regular expression to match our autodoc instructions."""

    def __init__(
        self,
        md: Markdown,
        *,
        handlers: Handlers,
        autorefs: AutorefsPlugin,
    ) -> None:
        """Initialize the object.

        Arguments:
            md: A `markdown.Markdown` instance.
            handlers: The handlers container.
            autorefs: The autorefs plugin instance.
        """
        super().__init__(parser=md.parser)
        self.md = md
        """The Markdown instance."""
        self._handlers = handlers
        self._autorefs = autorefs
        self._updated_envs: set = set()

    def test(self, parent: Element, block: str) -> bool:  # noqa: ARG002
        """Match our autodoc instructions.

        Arguments:
            parent: The parent element in the XML tree.
            block: The block to be tested.

        Returns:
            Whether this block should be processed or not.
        """
        return bool(self.regex.search(block))

    def run(self, parent: Element, blocks: MutableSequence[str]) -> None:
        """Run code on the matched blocks.

        The identifier and configuration lines are retrieved from a matched block
        and used to collect and render an object.

        Arguments:
            parent: The parent element in the XML tree.
            blocks: The rest of the blocks to be processed.
        """
        block = blocks.pop(0)
        match = self.regex.search(block)

        if match:
            if match.start() > 0:
                self.parser.parseBlocks(parent, [block[: match.start()]])
            # removes the first line
            block = block[match.end() :]

        block, the_rest = self.detab(block)

        if not block and blocks and blocks[0].startswith(("    handler:", "    options:")):
            # YAML options were separated from the `:::` line by a blank line.
            block = blocks.pop(0)

        if match:
            identifier = match["name"]
            heading_level = match["heading"].count("#")
            _logger.debug("Matched '::: %s'", identifier)

            html, handler, _ = self._process_block(identifier, block, heading_level)
            el = Element("div", {"class": "mkdocstrings"})
            # The final HTML is inserted as opaque to subsequent processing, and only revealed at the end.
            el.text = self.md.htmlStash.store(html)

            if handler.outer_layer:
                self._process_headings(handler, el)

            parent.append(el)

        if the_rest:
            # This block contained unindented line(s) after the first indented
            # line. Insert these lines as the first block of the master blocks
            # list for future processing.
            blocks.insert(0, the_rest)

    def _process_block(
        self,
        identifier: str,
        yaml_block: str,
        heading_level: int = 0,
    ) -> tuple[str, BaseHandler, CollectorItem]:
        """Process an autodoc block.

        Arguments:
            identifier: The identifier of the object to collect and render.
            yaml_block: The YAML configuration.
            heading_level: Suggested level of the heading to insert (0 to ignore).

        Raises:
            PluginError: When something wrong happened during collection.
            TemplateNotFound: When a template used for rendering could not be found.

        Returns:
            Rendered HTML, the handler that was used, and the collected item.
        """
        local_config = yaml.safe_load(yaml_block) or {}
        handler_name = self._handlers.get_handler_name(local_config)

        _logger.debug("Using handler '%s'", handler_name)
        handler = self._handlers.get_handler(handler_name)

        local_options = local_config.get("options", {})
        if heading_level:
            # Heading level obtained from Markdown (`##`) takes precedence.
            local_options["heading_level"] = heading_level

        options = handler.get_options(local_options)

        _logger.debug("Collecting data")
        try:
            data: CollectorItem = handler.collect(identifier, options)
        except CollectionError as exception:
            _logger.error("%s", exception)  # noqa: TRY400
            raise PluginError(f"Could not collect '{identifier}'") from exception

        if handler_name not in self._updated_envs:  # We haven't seen this handler before on this document.
            _logger.debug("Updating handler's rendering env")
            handler._update_env(self.md, config=self._handlers._tool_config)
            self._updated_envs.add(handler_name)

        _logger.debug("Rendering templates")
        if "locale" in signature(handler.render).parameters:
            render = partial(handler.render, locale=self._handlers._locale)
        else:
            render = handler.render  # type: ignore[assignment]
        try:
            rendered = render(data, options)
        except TemplateNotFound as exc:
            _logger.error(  # noqa: TRY400
                "Template '%s' not found for '%s' handler and theme '%s'.",
                exc.name,
                handler_name,
                self._handlers._theme,
            )
            raise

        return rendered, handler, data

    def _process_headings(self, handler: BaseHandler, element: Element) -> None:
        # We're in the outer handler layer, as well as the outer extension layer.
        #
        # The "handler layer" tracks the nesting of the autodoc blocks, which can appear in docstrings.
        #
        # - Render ::: Object1                  # Outer handler layer
        #   - Render Object1's docstring        # Outer handler layer
        #     - Docstring renders ::: Object2   # Inner handler layers
        #       - etc.                          # Inner handler layers
        #
        # The "extension layer" tracks whether we're converting an autodoc instruction
        # or nested content within it, like docstrings. Markdown conversion within Markdown conversion.
        #
        # - Render ::: Object1                  # Outer extension layer
        #   - Render Object1's docstring        # Inner extension layer
        #
        # The generated HTML was just stashed, and the `toc` extension won't be able to see headings.
        # We need to duplicate the headings directly, just so `toc` can pick them up,
        # otherwise they wouldn't appear in the final table of contents.
        #
        # These headings are generated by the `BaseHandler.do_heading` method (Jinja filter),
        # which runs in the inner extension layer, and not in the outer one where we are now.
        headings = handler.get_headings()
        element.extend(headings)
        # These duplicated headings will later be removed by our `_HeadingsPostProcessor` processor,
        # which runs right after `toc` (see `MkdocstringsExtension.extendMarkdown`).
        #
        # If we were in an inner handler layer, we wouldn't do any of this
        # and would just let headings bubble up to the outer handler layer.

        if (page := self._autorefs.current_page) is None:
            return

        for heading in headings:
            rendered_id = heading.attrib["id"]

            skip_inventory = "data-skip-inventory" in heading.attrib
            if skip_inventory:
                _logger.debug(
                    "Skipping heading with id %r because data-skip-inventory is present",
                    rendered_id,
                )
                continue

            # The title is registered to be used as tooltip by autorefs.
            self._autorefs.register_anchor(page, rendered_id, title=heading.text, primary=True)

            # Register all identifiers for this object
            # both in the autorefs plugin and in the inventory.
            aliases: tuple[str, ...]
            aliases = handler.get_aliases(rendered_id)

            for alias in aliases:
                if alias != rendered_id:
                    self._autorefs.register_anchor(page, alias, rendered_id, primary=False)

            if "data-role" in heading.attrib:
                self._handlers.inventory.register(
                    name=rendered_id,
                    domain=handler.domain,
                    role=heading.attrib["data-role"],
                    priority=1,  # Register with standard priority.
                    uri=f"{page.url}#{rendered_id}",
                )
                for alias in aliases:
                    if alias not in self._handlers.inventory:
                        self._handlers.inventory.register(
                            name=alias,
                            domain=handler.domain,
                            role=heading.attrib["data-role"],
                            priority=2,  # Register with lower priority.
                            uri=f"{page.url}#{rendered_id}",
                        )


class _HeadingsPostProcessor(Treeprocessor):
    def run(self, root: Element) -> None:
        self._remove_duplicated_headings(root)

    def _remove_duplicated_headings(self, parent: Element) -> None:
        carry_text = ""
        for el in reversed(parent):  # Reversed mainly for the ability to mutate during iteration.
            if el.tag == "div" and el.get("class") == "mkdocstrings":
                # Delete the duplicated headings along with their container, but keep the text (i.e. the actual HTML).
                carry_text = (el.text or "") + carry_text
                parent.remove(el)
            else:
                if carry_text:
                    el.tail = (el.tail or "") + carry_text
                    carry_text = ""
                self._remove_duplicated_headings(el)

        if carry_text:
            parent.text = (parent.text or "") + carry_text


class _TocLabelsTreeProcessor(Treeprocessor):
    def run(self, root: Element) -> None:  # noqa: ARG002
        self._override_toc_labels(self.md.toc_tokens)  # type: ignore[attr-defined]

    def _override_toc_labels(self, tokens: list[dict[str, Any]]) -> None:
        for token in tokens:
            if (label := token.get("data-toc-label")) and token["name"] != label:
                token["name"] = label
            self._override_toc_labels(token["children"])


class MkdocstringsExtension(Extension):
    """Our Markdown extension.

    It cannot work outside of `mkdocstrings`.
    """

    def __init__(
        self,
        handlers: Handlers,
        autorefs: AutorefsPlugin,
        *,
        autorefs_extension: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize the object.

        Arguments:
            handlers: The handlers container.
            autorefs: The autorefs plugin instance.
            autorefs_extension: Whether the autorefs extension must be registered.
            **kwargs: Keyword arguments used by `markdown.extensions.Extension`.
        """
        super().__init__(**kwargs)
        self._handlers = handlers
        self._autorefs = autorefs
        self._autorefs_extension = autorefs_extension

    def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802 (casing: parent method's name)
        """Register the extension.

        Add an instance of our [`AutoDocProcessor`][mkdocstrings.AutoDocProcessor] to the Markdown parser.

        Arguments:
            md: A `markdown.Markdown` instance.
        """
        md.registerExtension(self)

        # Zensical integration: get the current page from the Zensical-specific preprocessor.
        if "zensical_current_page" in md.preprocessors:
            self._autorefs.current_page = md.preprocessors["zensical_current_page"]  # type: ignore[assignment]

        md.parser.blockprocessors.register(
            AutoDocProcessor(md, handlers=self._handlers, autorefs=self._autorefs),
            "mkdocstrings",
            priority=75,  # Right before markdown.blockprocessors.HashHeaderProcessor
        )
        md.treeprocessors.register(
            _HeadingsPostProcessor(md),
            "mkdocstrings_post_headings",
            priority=4,  # Right after 'toc'.
        )
        md.treeprocessors.register(
            _TocLabelsTreeProcessor(md),
            "mkdocstrings_post_toc_labels",
            priority=4,  # Right after 'toc'.
        )

        if self._autorefs_extension:
            AutorefsExtension(self._autorefs).extendMarkdown(md)


# -----------------------------------------------------------------------------
# The following is only used by Zensical. The goal is to provide temporary
# compatibility for users migrating from MkDocs (and Material for MkDocs)
# to Zensical. When detecting the use of the mkdocstrings plugin in mkdocs.yml,
# Zensical will add the mkdocstrings extension to its Markdown extensions.

_default_config: dict[str, Any] = {
    "default_handler": "python",
    "handlers": {},
    "custom_templates": None,
    "locale": "en",
    "enable_inventory": True,
    "enabled": True,
}


def _split_configs(markdown_extensions: list[str | dict]) -> tuple[list[str | Extension], dict[str, Any]]:
    # Split markdown extensions and their configs from mkdocs.yml
    mdx: list[str] = []
    mdx_config: dict[str, Any] = {}
    for item in markdown_extensions:
        if isinstance(item, str):
            mdx.append(item)
        elif isinstance(item, dict):
            for key, value in item.items():
                mdx.append(key)
                mdx_config[key] = value
                break  # Only one item per dict
    return mdx, mdx_config  # type: ignore[return-value]


class _ToolConfig:
    def __init__(self, config_file_path: str | None = None) -> None:
        self.config_file_path = config_file_path


_AUTOREFS = None
_HANDLERS = None


def makeExtension(  # noqa: N802
    *,
    default_handler: str | None = None,
    inventory_project: str | None = None,
    inventory_version: str | None = None,
    handlers: dict[str, dict] | None = None,
    custom_templates: str | None = None,
    markdown_extensions: list[str | dict] | None = None,
    locale: str | None = None,
    config_file_path: str | None = None,
) -> MkdocstringsExtension:
    """Create the extension instance.

    We only support this function being used by Zensical.
    Consider this function private API.
    """
    global _AUTOREFS  # noqa: PLW0603
    if _AUTOREFS is None:
        _AUTOREFS = AutorefsPlugin()
        _AUTOREFS.config = AutorefsConfig()
        _AUTOREFS.config.resolve_closest = True
        _AUTOREFS.config.link_titles = "auto"
        _AUTOREFS.config.strip_title_tags = "auto"
        _AUTOREFS.scan_toc = True
        _AUTOREFS._link_titles = "external"
        _AUTOREFS._strip_title_tags = False

    global _HANDLERS  # noqa: PLW0603
    if _HANDLERS is None:
        mdx, mdx_config = _split_configs(markdown_extensions or [])
        tool_config = _ToolConfig(config_file_path=config_file_path)
        mdx.append(AutorefsExtension(_AUTOREFS))
        _HANDLERS = Handlers(
            theme="material",
            default=default_handler or _default_config["default_handler"],
            inventory_project=inventory_project or "Project",
            inventory_version=inventory_version or "0.0.0",
            handlers_config=handlers or _default_config["handlers"],
            custom_templates=custom_templates or _default_config["custom_templates"],
            mdx=mdx,
            mdx_config=mdx_config,
            locale=locale or _default_config["locale"],
            tool_config=tool_config,
        )

        _HANDLERS._download_inventories()
        register = _AUTOREFS.register_url
        for identifier, url in _HANDLERS._yield_inventory_items():
            register(identifier, url)

    return MkdocstringsExtension(
        handlers=_HANDLERS,
        autorefs=_AUTOREFS,
        autorefs_extension=True,
    )


def _reset() -> None:
    global _AUTOREFS, _HANDLERS  # noqa: PLW0603
    _AUTOREFS = None
    _HANDLERS = None


def _get_autorefs() -> dict[str, Any]:
    if _AUTOREFS:
        return {
            "primary": _AUTOREFS._primary_url_map,
            "secondary": _AUTOREFS._secondary_url_map,
            "inventory": _AUTOREFS._abs_url_map,
            "titles": _AUTOREFS._title_map,
        }
    return {}


def _get_inventory() -> bytes:
    if _HANDLERS:
        return _HANDLERS.inventory.format_sphinx()
    return b""
