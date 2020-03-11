import json
import re

import yaml
from markdown import Markdown
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.util import etree

from .handlers import get_handler


class AutoDocProcessor(BlockProcessor):
    CLASSNAME = "autodoc"
    RE = re.compile(r"(?:^|\n)::: ?([:a-zA-Z0-9_.]*) *(?:\n|$)")

    def __init__(self, parser, md, plugin_config):
        super().__init__(parser=parser)
        self.md = md
        self._plugin_config = plugin_config

    def test(self, parent: etree.Element, block: etree.Element) -> bool:
        sibling = self.lastChild(parent)
        bool1 = self.RE.search(block)
        bool2 = (
            block.startswith(" " * self.tab_length)
            and sibling is not None
            and sibling.get("class", "").find(self.CLASSNAME) != -1
        )
        return bool(bool1 or bool2)

    def run(self, parent: etree.Element, blocks: etree.Element) -> None:
        block = blocks.pop(0)
        m = self.RE.search(block)

        if m:
            block = block[m.end() :]  # removes the first line

        block, the_rest = self.detab(block)

        if m:
            identifier = m.group(1)
            config = yaml.safe_load(block) or {}

            handler_name = self.get_handler_name(config)
            handler = get_handler(handler_name)
            handler.renderer.update_env(self.md)

            selection, rendering = self.get_item_configs(handler_name, config)

            data = handler.collector.collect(identifier, selection)
            rendered = handler.renderer.render(data, rendering)
            parent.append(etree.XML(rendered))

        if the_rest:
            # This block contained unindented line(s) after the first indented
            # line. Insert these lines as the first block of the master blocks
            # list for future processing.
            blocks.insert(0, the_rest)

    def get_handler_name(self, config):
        if "handler" in config:
            return config["handler"]
        return self._plugin_config["default_handler"]

    def get_handler_config(self, handler_name):
        handlers = self._plugin_config.get("handlers", {})
        if handlers:
            return handlers.get(handler_name, {})
        return {}

    def get_item_configs(self, handler_name, config):
        handler_config = self.get_handler_config(handler_name)
        item_selection_config = dict(handler_config.get("selection"))
        item_selection_config.update(config.get("selection", {}))
        item_rendering_config = dict(handler_config.get("rendering"))
        item_rendering_config.update(config.get("rendering", {}))
        return item_selection_config, item_rendering_config


class MkdocstringsExtension(Extension):
    def __init__(self, plugin_config, **kwargs):
        super().__init__(**kwargs)
        self._plugin_config = plugin_config

    def extendMarkdown(self, md: Markdown) -> None:
        md.registerExtension(self)
        processor = AutoDocProcessor(md.parser, md, self._plugin_config)
        md.parser.blockprocessors.register(processor, "mkdocstrings", 110)
