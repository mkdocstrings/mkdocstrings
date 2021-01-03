"""
This module holds the code of the Markdown extension responsible for matching "autodoc" instructions.

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
from typing import Any, Mapping, MutableSequence, Tuple
from xml.etree.ElementTree import XML, Element, ParseError  # noqa: S405 (we choose to trust the XML input)

import yaml
from jinja2.exceptions import TemplateNotFound
from markdown import Markdown
from markdown.blockparser import BlockParser
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.util import AtomicString

from mkdocstrings.handlers.base import CollectionError, Handlers
from mkdocstrings.loggers import get_logger
from mkdocstrings.references import AutoRefInlineProcessor

log = get_logger(__name__)

ENTITIES = """
    <!DOCTYPE html [
        <!ENTITY hellip '&amp;hellip;'>
        <!ENTITY laquo '&amp;laquo;'>
        <!ENTITY ldquo '&amp;ldquo;'>
        <!ENTITY lsquo '&amp;lsquo;'>
        <!ENTITY mdash '&amp;mdash;'>
        <!ENTITY nbsp '&amp;nbsp;'>
        <!ENTITY ndash '&amp;ndash;'>
        <!ENTITY para '&amp;para;'>
        <!ENTITY raquo '&amp;raquo;'>
        <!ENTITY rdquo '&amp;rdquo;'>
        <!ENTITY rsquo '&amp;rsquo;'>
    ]>
"""


def atomic_brute_cast(tree: Element) -> Element:
    """
    Cast every node's text into an atomic string to prevent further processing on it.

    Since we generate the final HTML with Jinja templates, we do not want other inline or tree processors
    to keep modifying the data, so this function is used to mark the complete tree as "do not touch".

    Reference: issue [Python-Markdown/markdown#920](https://github.com/Python-Markdown/markdown/issues/920).

    On a side note: isn't `atomic_brute_cast` such a beautiful function name?

    Arguments:
        tree: An XML node, used like the root of an XML tree.

    Returns:
        The same node, recursively modified by side-effect. You can skip re-assigning the return value.
    """
    if tree.text:
        tree.text = AtomicString(tree.text)
    for child in tree:
        atomic_brute_cast(child)
    return tree


class AutoDocProcessor(BlockProcessor):
    """
    Our "autodoc" Markdown block processor.

    It has a [`test` method][mkdocstrings.extension.AutoDocProcessor.test] that tells if a block matches a criterion,
    and a [`run` method][mkdocstrings.extension.AutoDocProcessor.run] that processes it.

    It also has utility methods allowing to get handlers and their configuration easily, useful when processing
    a matched block.
    """

    regex = re.compile(r"^(?P<heading>#{1,6} *|)::: ?(?P<name>.+?) *$", flags=re.MULTILINE)

    def __init__(self, parser: BlockParser, md: Markdown, config: dict, handlers: Handlers) -> None:
        """
        Initialize the object.

        Arguments:
            parser: A `markdown.blockparser.BlockParser` instance.
            md: A `markdown.Markdown` instance.
            config: The [configuration][mkdocstrings.plugin.MkdocstringsPlugin.config_scheme]
                of the `mkdocstrings` plugin.
            handlers: A [mkdocstrings.handlers.base.Handlers][] instance.
        """
        super().__init__(parser=parser)
        self.md = md
        self._config = config
        self._handlers = handlers
        self._updated_env = False

    def test(self, parent: Element, block: str) -> bool:
        """
        Match our autodoc instructions.

        Arguments:
            parent: The parent element in the XML tree.
            block: The block to be tested.

        Returns:
            Whether this block should be processed or not.
        """
        return bool(self.regex.search(block))

    def run(self, parent: Element, blocks: MutableSequence[str]) -> None:
        """
        Run code on the matched blocks.

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
            xml_element = self.process_block(identifier, block, heading_level)
            parent.append(xml_element)

        if the_rest:
            # This block contained unindented line(s) after the first indented
            # line. Insert these lines as the first block of the master blocks
            # list for future processing.
            blocks.insert(0, the_rest)

    def process_block(self, identifier: str, yaml_block: str, heading_level: int = 0) -> Element:
        """
        Process an autodoc block.

        Arguments:
            identifier: The identifier of the object to collect and render.
            yaml_block: The YAML configuration.
            heading_level: Suggested level of the the heading to insert (0 to ignore).

        Raises:
            CollectionError: When something wrong happened during collection.
            ParseError: When the generated HTML could not be parsed as XML.
            TemplateNotFound: When a template used for rendering could not be found.

        Returns:
            A new XML element.
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
            data: Any = handler.collector.collect(identifier, selection)
        except CollectionError:
            log.error(f"Could not collect '{identifier}'")
            raise

        if not self._updated_env:
            log.debug("Updating renderer's env")
            handler.renderer.update_env(self.md, self._config)
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

        log.debug("Loading HTML back into XML tree")
        rendered = ENTITIES + rendered
        try:
            xml_contents = XML(rendered)
        except ParseError as error:
            log_xml_parse_error(str(error), rendered)
            raise

        return atomic_brute_cast(xml_contents)  # type: ignore


def get_item_configs(handler_config: dict, config: dict) -> Tuple[Mapping, Mapping]:
    """
    Get the selection and rendering configuration merged into the global configuration of the given handler.

    Arguments:
        handler_config: The global configuration of a handler. It can be an empty dictionary.
        config: The configuration to merge into the global handler configuration.

    Returns:
        Two dictionaries: selection and rendering. The local configurations are merged into the global ones.
    """
    item_selection_config = ChainMap(config.get("selection", {}), handler_config.get("selection", {}))
    item_rendering_config = ChainMap(config.get("rendering", {}), handler_config.get("rendering", {}))
    return item_selection_config, item_rendering_config


def log_xml_parse_error(error: str, xml_text: str) -> None:
    """
    Log an XML parsing error.

    If the error is a tag mismatch, augment the log message.

    Arguments:
        error: The error message (no traceback).
        xml_text: The XML text that generated the parsing error.
    """
    message = error
    mismatched_tag = "mismatched tag" in error
    undefined_entity = "undefined entity" in error

    if mismatched_tag or undefined_entity:
        line_column = error[error.rfind(":") + 1 :]
        line, column = line_column.split(", ")
        lineno = int(line[line.rfind(" ") + 1 :])
        columnno = int(column[column.rfind(" ") + 1 :])

        line = xml_text.split("\n")[lineno - 1]
        if mismatched_tag:
            character = line[columnno]
            message += (
                f" (character {character}):\n{line}\n"
                "If your Markdown contains angle brackets < >, try to wrap them between backticks `< >`, "
                "or replace them with &lt; and &gt;"
            )
        elif undefined_entity:
            message += f":\n{line}\n"
    log.error(message)


class MkdocstringsExtension(Extension):
    """
    Our Markdown extension.

    It cannot work outside of `mkdocstrings`.
    """

    blockprocessor_priority = 75  # Right before markdown.blockprocessors.HashHeaderProcessor
    inlineprocessor_priority = 168  # Right after markdown.inlinepatterns.ReferenceInlineProcessor

    def __init__(self, config: dict, handlers: Handlers, **kwargs) -> None:
        """
        Initialize the object.

        Arguments:
            config: The configuration items from `mkdocs` and `mkdocstrings` that must be passed to the block processor
                when instantiated in [`extendMarkdown`][mkdocstrings.extension.MkdocstringsExtension.extendMarkdown].
            handlers: A [mkdocstrings.handlers.base.Handlers][] instance.
            kwargs: Keyword arguments used by `markdown.extensions.Extension`.
        """
        super().__init__(**kwargs)
        self._config = config
        self._handlers = handlers

    def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802 (casing: parent method's name)
        """
        Register the extension.

        Add an instance of our [`AutoDocProcessor`][mkdocstrings.extension.AutoDocProcessor] to the Markdown parser.

        Arguments:
            md: A `markdown.Markdown` instance.
        """
        md.registerExtension(self)
        processor = AutoDocProcessor(md.parser, md, self._config, self._handlers)
        md.parser.blockprocessors.register(processor, "mkdocstrings", self.blockprocessor_priority)
        ref_processor = AutoRefInlineProcessor(md)
        md.inlinePatterns.register(ref_processor, "mkdocstrings", self.inlineprocessor_priority)
