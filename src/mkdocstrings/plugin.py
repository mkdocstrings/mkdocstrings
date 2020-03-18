"""
This is the plugin module.

Trying auto references:

- [mkdocstrings.plugin.MkdocstringsPlugin][]
- [`get_instructions`][mkdocstrings.plugin.get_instructions]

Done.
"""
import re
from typing import Generator, Tuple

import yaml
from mkdocs.config.config_options import Type as MkType
from mkdocs.plugins import BasePlugin
from mkdocs.utils import log
from bs4 import BeautifulSoup

from .handlers import teardown
from .extension import MkdocstringsExtension


# TODO: make this configurable
DEFAULT_HANDLER = "python"

SELECTION_OPTS_KEY = "selection"
RENDERING_OPTS_KEY = "rendering"
"""This is the name of the rendering parameter."""

DIRECT_REF = re.compile(r"\[(?P<identifier>.*?)\]\[\]")
TITLED_REF = re.compile(r"\[(?P<title>.*?)\]\[(?P<identifier>.+?)\]")


class MkdocstringsPlugin(BasePlugin):
    """This is the plugin class."""

    config_scheme = (
        ("watch", MkType(list, default=[])),
        ("handlers", MkType(dict, default={})),
        ("default_handler", MkType(str, default="python")),
    )

    def __init__(self, *args, **kwargs) -> None:
        super(MkdocstringsPlugin, self).__init__()
        self.mkdocstrings_extension = None
        self.url_map = {}

    def on_serve(self, server, config, **kwargs):
        """On serve hook."""
        builder = list(server.watcher._tasks.values())[0]["func"]
        for element in self.config["watch"]:
            log.info(f"mkdocstrings: Adding directory '{element}' to watcher")
            server.watch(element, builder)
        return server

    def on_config(self, config, **kwargs):
        """
        On config hook.

        What about references in docstrings and code blocks?

        - [`my ref`][mkdocstrings.plugin]
        - [mkdocstrings.plugin][]
        """
        log.info("mkdocstrings: Adding extension to the list")
        self.mkdocstrings_extension = MkdocstringsExtension(plugin_config=self.config)
        config["markdown_extensions"].append(self.mkdocstrings_extension)
        return config

    def on_page_content(self, html, page, config, files, **kwargs):
        log.info(f"mkdocstrings: Mapping identifiers to URLs for page {page.abs_url}")
        for item in page.toc.items:
            self.map_urls(page.abs_url, item)
        return html

    def map_urls(self, base_url, anchor):
        self.url_map[anchor.id] = base_url + anchor.url
        for child in anchor.children:
            self.map_urls(base_url, child)

    def on_post_page(self, output, page, config, **kwargs):
        log.info(f"mkdocstrings: Fixing broken references in page {page.abs_url}")
        soup = BeautifulSoup(output, "html.parser")
        tags = soup.find_all(refs)
        for tag in tags:
            tag_str = str(tag)
            new_str = TITLED_REF.sub(self.fix_ref, tag_str)
            new_str = DIRECT_REF.sub(self.fix_ref, new_str)
            if new_str != tag_str:
                tag.replace_with(BeautifulSoup(new_str, "html.parser"))
        return soup.prettify()

    def fix_ref(self, match):
        groups = match.groupdict()
        identifier = groups["identifier"]
        title = groups.get("title")
        try:
            url = self.url_map[identifier]
        except KeyError:
            if title:
                return f"[{title}][{identifier}]"
            return f"[{identifier}][]"
        else:
            return f'<a href="{url}">{title or identifier}</a>'

    def on_post_build(self, config, **kwargs):
        log.info("mkdocstrings: Tearing handlers down")
        teardown()


def refs(tag):
    if not tag.find_parent("code") and not tag.name == "code" and (DIRECT_REF.match(tag.text) or TITLED_REF.match(tag.text)):
        return True
    return False
