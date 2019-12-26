from markdown import Markdown
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree
import re


class AutoDocProcessor(BlockProcessor):
    CLASSNAME = "autodoc"
    RE = re.compile(r"(?:^|\n)::: ?([:a-zA-Z0-9_.]*) *(?:\n|$)")

    def __init__(self, parser, md, plugin):
        super().__init__(parser=parser)
        self.md = md
        self.plugin = plugin

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

        block, theRest = self.detab(block)

        if theRest:
            # This block contained unindented line(s) after the first indented
            # line. Insert these lines as the first block of the master blocks
            # list for future processing.
            blocks.insert(0, theRest)


class MkdocstringsExtension(Extension):
    def __init__(self, plugin, **kwargs):
        super().__init__(**kwargs)
        self.plugin = plugin

    def extendMarkdown(self, md: Markdown) -> None:
        md.registerExtension(self)
        processor = AutoDocProcessor(md.parser, md, self.plugin)
        md.parser.blockprocessors.register(processor, "mkdocstrings", 110)
