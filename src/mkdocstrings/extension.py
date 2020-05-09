"""
This module holds the code of the Markdown extension responsible for matching "autodoc" instructions.

The extension is composed of a Markdown [block processor](https://python-markdown.github.io/extensions/api/#blockparser)
that matches indented blocks starting with a line like '::: identifier'.

For each of these blocks, it uses a [handler][mkdocstrings.handlers.BaseHandler] to collect documentation about
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
import logging
import re
from typing import Any, Tuple
from xml.etree.ElementTree import XML, Element, ParseError  # noqa: S405 (we choose to trust the XML input)

import yaml
from jinja2.exceptions import TemplateNotFound
from markdown import Markdown
from markdown.blockparser import BlockParser
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.util import AtomicString
from mkdocs.utils import warning_filter

from mkdocstrings.handlers import CollectionError, get_handler

log = logging.getLogger(f"mkdocs.plugins.{__name__}")
log.addFilter(warning_filter)


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

    CLASSNAME = "autodoc"
    RE = re.compile(r"(?:^|\n)::: ?([:a-zA-Z0-9_.]*) *(?:\n|$)")

    def __init__(self, parser: BlockParser, md: Markdown, config: dict) -> None:
        """
        Initialization method.

        Arguments:
            parser: A `markdown.blockparser.BlockParser` instance.
            md: A `markdown.Markdown` instance.
            config: The [configuration][mkdocstrings.plugin.MkdocstringsPlugin.config_scheme]
                of the `mkdocstrings` plugin.
        """
        super().__init__(parser=parser)
        self.md = md
        self._config = config

    def test(self, parent: Element, block: Element) -> bool:
        """Match our autodoc instructions."""
        sibling = self.lastChild(parent)
        bool1 = self.RE.search(str(block))
        bool2 = (
            str(block).startswith(" " * self.tab_length)
            and sibling is not None
            and sibling.get("class", "").find(self.CLASSNAME) != -1
        )
        return bool(bool1 or bool2)

    def run(self, parent: Element, blocks: Element) -> None:
        """
        The processing of autodoc instructions is done here.

        The identifier and configuration lines are retrieved from a matched block
        and used to collect and render an object.

        Arguments:
            parent: The parent element in the XML tree.
            blocks: The rest of the blocks to be processed.
        """
        block = blocks.pop(0)
        match = self.RE.search(str(block))

        if match:
            # removes the first line
            block = block[match.end() :]  # type: ignore

        block, the_rest = self.detab(block)

        if match:
            identifier = match.group(1)
            log.debug(f"mkdocstrings.extension: Matched '::: {identifier}'")
            config = yaml.safe_load(str(block)) or {}

            handler_name = self.get_handler_name(config)
            log.debug(f"mkdocstrings.extension: Using handler '{handler_name}'")
            handler_config = self.get_handler_config(handler_name)
            handler = get_handler(
                handler_name,
                self._config["theme_name"],
                self._config["mkdocstrings"]["custom_templates"],
                **handler_config,
            )

            selection, rendering = self.get_item_configs(handler_config, config)

            log.debug("mkdocstrings.extension: Collecting data")
            try:
                data: Any = handler.collector.collect(identifier, selection)
            except CollectionError:
                log.error(f"mkdocstrings.extension: Could not collect '{identifier}'")
                raise

            log.debug("mkdocstrings.extension: Updating renderer's env")
            handler.renderer.update_env(self.md, self._config)

            log.debug("mkdocstrings.extension: Rendering templates")
            try:
                rendered = handler.renderer.render(data, rendering)
            except TemplateNotFound as error:
                theme_name = self._config["theme_name"]
                log.error(
                    f"mkdocstrings.extension: Template '{error.name}' not found "
                    f"for '{handler_name}' handler and theme '{theme_name}'."
                )
                raise

            log.debug("mkdocstrings.extension: Loading HTML back into XML tree")
            try:
                as_xml = XML(rendered)
            except ParseError as error:
                message = f"mkdocstrings.extension: {error}"
                if "mismatched tag" in str(error):
                    line, column = str(error).split(":")[-1].split(", ")

                    lineno = int(line.split(" ")[-1])
                    columnno = int(column.split(" ")[-1])

                    line = rendered.split("\n")[lineno - 1]
                    character = line[columnno]
                    message += (
                        f" (character {character}):\n{line}\n"
                        f"If your Markdown contains angle brackets < >, try to wrap them between backticks `< >`, "
                        f"or replace them with &lt; and &gt;"
                    )
                log.error(message)
                raise

            as_xml = atomic_brute_cast(as_xml)  # type: ignore
            parent.append(as_xml)

        if the_rest:
            # This block contained unindented line(s) after the first indented
            # line. Insert these lines as the first block of the master blocks
            # list for future processing.
            blocks.insert(0, the_rest)

    def get_handler_name(self, config: dict) -> str:
        """
        Return the handler name defined in an "autodoc" instruction YAML configuration, or the global default handler.

        Args:
            config: A configuration dictionary, obtained from YAML below the "autodoc" instruction.

        Returns:
            The name of the handler to use.
        """
        if "handler" in config:
            return config["handler"]
        return self._config["mkdocstrings"]["default_handler"]

    def get_handler_config(self, handler_name: str) -> dict:
        """
        Return the global configuration of the given handler.

        Arguments:
            handler_name: The name of the handler to get the global configuration of.

        Returns:
            The global configuration of the given handler. It can be an empty dictionary.
        """
        handlers = self._config["mkdocstrings"].get("handlers", {})
        if handlers:
            return handlers.get(handler_name, {})
        return {}

    @staticmethod
    def get_item_configs(handler_config: dict, config: dict) -> Tuple[dict, dict]:
        """
        Get the selection and rendering configuration merged into the global configuration of the given handler.

        Args:
            handler_config: The global configuration of a handler. It can be an empty dictionary.
            config: The configuration to merge into the global handler configuration.

        Returns:
            Two dictionaries: selection and rendering. The local configurations are merged into the global ones.
        """
        item_selection_config = dict(handler_config.get("selection", {}))
        item_selection_config.update(config.get("selection", {}))
        item_rendering_config = dict(handler_config.get("rendering", {}))
        item_rendering_config.update(config.get("rendering", {}))
        return item_selection_config, item_rendering_config


class MkdocstringsExtension(Extension):
    """
    Our Markdown extension.

    It cannot work outside of `mkdocstrings`.
    """

    def __init__(self, config: dict, **kwargs) -> None:
        """
        Initialization method.

        Arguments:
            config: The configuration items from `mkdocs` and `mkdocstrings` that must be passed to the block processor
                when instantiated in [`extendMarkdown`][mkdocstrings.extension.MkdocstringsExtension.extendMarkdown].
            kwargs: Keyword arguments used by `markdown.extensions.Extension`.
        """
        super().__init__(**kwargs)
        self._config = config

    def extendMarkdown(self, md: Markdown) -> None:
        """
        Register the extension.

        Add an instance of our [`AutoDocProcessor`][mkdocstrings.extension.AutoDocProcessor] to the Markdown parser.

        Args:
            md: A `markdown.Markdown` instance.
        """
        md.registerExtension(self)
        processor = AutoDocProcessor(md.parser, md, self._config)
        md.parser.blockprocessors.register(processor, "mkdocstrings", 110)
