import json
import re

import yaml
from markdown import Markdown
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.util import etree


class AutoDocProcessor(BlockProcessor):
    CLASSNAME = "autodoc"
    RE = re.compile(r"(?:^|\n)::: ?([:a-zA-Z0-9_.]*) *(?:\n|$)")

    def __init__(self, parser, md, store):
        super().__init__(parser=parser)
        self.md = md
        self.store = store

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
            selection_hash = hash(json.dumps({identifier: config.get("collector", {})}, sort_keys=True))

            item = self.store[selection_hash]
            renderer, data = item["renderer"], item["data"]
            renderer.update_env(self.md)

            parent.append(etree.XML(renderer.render(data)))

        if the_rest:
            # This block contained unindented line(s) after the first indented
            # line. Insert these lines as the first block of the master blocks
            # list for future processing.
            blocks.insert(0, the_rest)


class MkdocstringsExtension(Extension):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._store = {}

    def extendMarkdown(self, md: Markdown) -> None:
        md.registerExtension(self)
        processor = AutoDocProcessor(md.parser, md, self._store)
        md.parser.blockprocessors.register(processor, "mkdocstrings", 110)

    def store(self, selection_hash, data, renderer):
        self._store[selection_hash] = {"data": data, "renderer": renderer}
