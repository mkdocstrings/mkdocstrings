"""This module holds the code of the Markdown extension responsible for matching "autodoc" instructions.

The extension is composed of a Markdown [block processor](https://python-markdown.github.io/extensions/api/#blockparser)
that matches indented blocks starting with a line like '::: identifier'.

For each of these blocks, it uses a [handler][mkdocstrings.handlers.base.BaseHandler] to collect documentation about
the given identifier and render it with Jinja templates.

Both the collection and rendering process can be configured by adding YAML configuration under the "autodoc"
instruction:

```yaml
::: some.identifier
    handler: python
    selection:
      option1: value1
      option2:
        - value2a
        - value2b
    rendering:
      option_x: etc
```
"""
import re
from collections import ChainMap
from typing import Mapping, MutableSequence, Sequence, Tuple
from xml.etree.ElementTree import Element

import yaml
from jinja2.exceptions import TemplateNotFound
from markdown import Markdown
from markdown.blockparser import BlockParser
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from mkdocs_autorefs.plugin import AutorefsPlugin

from mkdocstrings.handlers.base import CollectionError, CollectorItem, Handlers
from mkdocstrings.loggers import get_logger

try:
    from mkdocs.exceptions import PluginError  # New in MkDocs 1.2
except ImportError:
    PluginError = SystemExit


log = get_logger(__name__)


class AutoDocProcessor(BlockProcessor):
    """Our "autodoc" Markdown block processor.

    It has a [`test` method][mkdocstrings.extension.AutoDocProcessor.test] that tells if a block matches a criterion,
    and a [`run` method][mkdocstrings.extension.AutoDocProcessor.run] that processes it.

    It also has utility methods allowing to get handlers and their configuration easily, useful when processing
    a matched block.
    """

    regex = re.compile(r"^(?P<heading>#{1,6} *|)::: ?(?P<name>.+?) *$", flags=re.MULTILINE)

    def __init__(
        self, parser: BlockParser, md: Markdown, config: dict, handlers: Handlers, autorefs: AutorefsPlugin
    ) -> None:
        """Initialize the object.

        Arguments:
            parser: A `markdown.blockparser.BlockParser` instance.
            md: A `markdown.Markdown` instance.
            config: The [configuration][mkdocstrings.plugin.MkdocstringsPlugin.config_scheme]
                of the `mkdocstrings` plugin.
            handlers: A [mkdocstrings.handlers.base.Handlers][] instance.
            autorefs: A [mkdocs_autorefs.plugin.AutorefsPlugin][] instance.
        """
        super().__init__(parser=parser)
        self.md = md
        self._config = config
        self._handlers = handlers
        self._autorefs = autorefs
        self._updated_env = False

    def test(self, parent: Element, block: str) -> bool:
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
            block = block[match.end() :]  # type: ignore

        block, the_rest = self.detab(block)

        if match:
            identifier = match["name"]
            heading_level = match["heading"].count("#")
            log.debug(f"Matched '::: {identifier}'")

            html, headings = self._process_block(identifier, block, heading_level)
            el = Element("div", {"class": "mkdocstrings"})
            # The final HTML is inserted as opaque to subsequent processing, and only revealed at the end.
            el.text = self.md.htmlStash.store(html)
            # So we need to duplicate the headings directly (and delete later), just so 'toc' can pick them up.
            el.extend(headings)

            for heading in headings:
                self._autorefs.register_anchor(self._autorefs.current_page, heading.attrib["id"])

            parent.append(el)

        if the_rest:
            # This block contained unindented line(s) after the first indented
            # line. Insert these lines as the first block of the master blocks
            # list for future processing.
            blocks.insert(0, the_rest)

    def _process_block(self, identifier: str, yaml_block: str, heading_level: int = 0) -> Tuple[str, Sequence[Element]]:
        """Process an autodoc block.

        Arguments:
            identifier: The identifier of the object to collect and render.
            yaml_block: The YAML configuration.
            heading_level: Suggested level of the the heading to insert (0 to ignore).

        Raises:
            PluginError: When something wrong happened during collection.
            TemplateNotFound: When a template used for rendering could not be found.

        Returns:
            Rendered HTML and the list of heading elements encoutered.
        """
        config = yaml.safe_load(yaml_block) or {}
        handler_name = self._handlers.get_handler_name(config)

        log.debug(f"Using handler '{handler_name}'")
        handler_config = self._handlers.get_handler_config(handler_name)
        handler = self._handlers.get_handler(handler_name, handler_config)

        selection, rendering = get_item_configs(handler_config, config)
        if heading_level:
            rendering = ChainMap(rendering, {"heading_level": heading_level})  # like setdefault

        log.debug("Collecting data")
        try:
            data: CollectorItem = handler.collector.collect(identifier, selection)
        except CollectionError as exception:
            log.error(str(exception))
            if PluginError is SystemExit:  # When MkDocs 1.2 is sufficiently common, this can be dropped.
                log.error(f"Error reading page '{self._autorefs.current_page}':")
            raise PluginError(f"Could not collect '{identifier}'") from exception

        if not self._updated_env:
            log.debug("Updating renderer's env")
            handler.renderer._update_env(self.md, self._config)  # noqa: W0212 (protected member OK)
            self._updated_env = True

        log.debug("Rendering templates")
        try:
            rendered = handler.renderer.render(data, rendering)
        except TemplateNotFound as exc:
            theme_name = self._config["theme_name"]
            log.error(
                f"Template '{exc.name}' not found for '{handler_name}' handler and theme '{theme_name}'.",
            )
            raise

        return (rendered, handler.renderer.get_headings())


def get_item_configs(handler_config: dict, config: dict) -> Tuple[Mapping, Mapping]:
    """Get the selection and rendering configuration merged into the global configuration of the given handler.

    Arguments:
        handler_config: The global configuration of a handler. It can be an empty dictionary.
        config: The configuration to merge into the global handler configuration.

    Returns:
        Two dictionaries: selection and rendering. The local configurations are merged into the global ones.
    """
    item_selection_config = ChainMap(config.get("selection", {}), handler_config.get("selection", {}))
    item_rendering_config = ChainMap(config.get("rendering", {}), handler_config.get("rendering", {}))
    return item_selection_config, item_rendering_config


class _PostProcessor(Treeprocessor):
    def run(self, root: Element):
        carry_text = ""
        for el in reversed(root):  # Reversed mainly for the ability to mutate during iteration.
            if el.tag == "div" and el.get("class") == "mkdocstrings":
                # Delete the duplicated headings along with their container, but keep the text (i.e. the actual HTML).
                carry_text = (el.text or "") + carry_text
                root.remove(el)
            elif carry_text:
                el.tail = (el.tail or "") + carry_text
                carry_text = ""
        if carry_text:
            root.text = (root.text or "") + carry_text


class MkdocstringsExtension(Extension):
    """Our Markdown extension.

    It cannot work outside of `mkdocstrings`.
    """

    def __init__(self, config: dict, handlers: Handlers, autorefs: AutorefsPlugin, **kwargs) -> None:
        """Initialize the object.

        Arguments:
            config: The configuration items from `mkdocs` and `mkdocstrings` that must be passed to the block processor
                when instantiated in [`extendMarkdown`][mkdocstrings.extension.MkdocstringsExtension.extendMarkdown].
            handlers: A [mkdocstrings.handlers.base.Handlers][] instance.
            autorefs: A [mkdocs_autorefs.plugin.AutorefsPlugin][] instance.
            kwargs: Keyword arguments used by `markdown.extensions.Extension`.
        """
        super().__init__(**kwargs)
        self._config = config
        self._handlers = handlers
        self._autorefs = autorefs

    def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802 (casing: parent method's name)
        """Register the extension.

        Add an instance of our [`AutoDocProcessor`][mkdocstrings.extension.AutoDocProcessor] to the Markdown parser.

        Arguments:
            md: A `markdown.Markdown` instance.
        """
        md.parser.blockprocessors.register(
            AutoDocProcessor(md.parser, md, self._config, self._handlers, self._autorefs),
            "mkdocstrings",
            priority=75,  # Right before markdown.blockprocessors.HashHeaderProcessor
        )
        md.treeprocessors.register(
            _PostProcessor(md.parser),
            "mkdocstrings_post",
            priority=4,  # Right after 'toc'.
        )
