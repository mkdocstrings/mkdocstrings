"""Tests for the syntax in the extension module."""

import re
from textwrap import dedent

from markdown import Markdown
from markupsafe import Markup
from mkdocs_autorefs.plugin import AutorefsPlugin

from mkdocstrings.extension import MkdocstringsExtension
from mkdocstrings.handlers.base import BaseHandler
from mkdocstrings.plugin import Handlers


class FakeHandler(BaseHandler):
    def __init__(self, with_heading=False, with_options=False):
        self.with_heading = with_heading
        self.with_options = with_options
        super().__init__(handler="fake", theme="material")

    def collect(self, identifier, config):
        return identifier

    def render(self, data, config):
        heading_level = config.get("heading_level", 2)
        html_id = data
        doc = self.do_convert_markdown(f"Documentation for {data}", heading_level, html_id)
        if self.with_heading:
            doc = self.do_heading(data, heading_level, id=html_id) + doc
        if self.with_options:
            doc += " " + ",".join(f"{k}:{v}" for k, v in config.items())
        return Markup('<div class="doc-object">{}</div>').format(doc)

    def get_templates_dir(self, handler):
        return super().get_templates_dir("python")


def fake_ext_markdown(handler, config={}, markdown_extensions={}):
    extension_config = {
        "site_name": "foo",
        "mdx": ["toc", *markdown_extensions],
        "mdx_configs": markdown_extensions,
        "mkdocstrings": {"default_handler": "fake"},
        **config,
    }
    handlers = Handlers(extension_config)
    handlers._handlers["fake"] = handler
    autorefs = AutorefsPlugin()
    extension = MkdocstringsExtension(extension_config, handlers, autorefs)
    return Markdown(
        extensions=["toc", extension, *markdown_extensions],
        extension_configs=markdown_extensions,
    )


def test_options_and_text_around():
    source = dedent(
        """
            hi
            ::: foo.Bar
                options:
                    hi: 1
             *after*
            """
    )
    md = fake_ext_markdown(FakeHandler(with_options=True))
    expected = dedent(
        """
        <p>hi</p>
        <div class="doc-object">
            <p>Documentation for foo.Bar</p> hi:1
        </div>
        <p><em>after</em></p>
        """
    ).strip()

    assert md.convert(source).replace("\n", "") == re.sub("\n *", "", expected)
