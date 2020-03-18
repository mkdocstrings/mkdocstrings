"""
This is the plugin module.

Trying auto references:

- [mkdocstrings.plugin.MkdocstringsPlugin][]
- [`get_instructions`][mkdocstrings.plugin.get_instructions]

Done.
"""
import logging
import re

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

AUTO_REF = re.compile(r"\[(?P<title>.*?)\]\[(?P<identifier>.*?)\]")


class MkdocstringsPlugin(BasePlugin):
    """This is the plugin class."""

    config_scheme = (
        ("watch", MkType(list, default=[])),
        ("handlers", MkType(dict, default={})),
        ("default_handler", MkType(str, default="python")),
    )

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialization method.

        Arguments:
            args: Whatever.
            kwargs: As well.
        """
        super(MkdocstringsPlugin, self).__init__()
        self.mkdocstrings_extension = None
        self.url_map = {}

    def on_serve(self, server, config, **kwargs):
        """On serve hook."""
        builder = list(server.watcher._tasks.values())[0]["func"]
        for element in self.config["watch"]:
            log.debug(f"mkdocstrings.plugin: Adding directory '{element}' to watcher")
            server.watch(element, builder)
        return server

    def on_config(self, config, **kwargs):
        """
        On config hook.

        What about references in docstrings and code blocks?

        - [`my ref`][mkdocstrings.plugin]
        - [mkdocstrings.plugin][]
        """
        log.debug("mkdocstrings.plugin: Adding extension to the list")
        self.mkdocstrings_extension = MkdocstringsExtension(plugin_config=self.config)
        config["markdown_extensions"].append(self.mkdocstrings_extension)
        return config

    def on_page_content(self, html, page, config, files, **kwargs):
        log.debug(f"mkdocstrings.plugin: Mapping identifiers to URLs for page {page.file.src_path}")
        for item in page.toc.items:
            self.map_urls(page.abs_url, item)
        return html

    def map_urls(self, base_url, anchor):
        self.url_map[anchor.id] = base_url + anchor.url
        for child in anchor.children:
            self.map_urls(base_url, child)

    def on_post_page(self, output, page, config, **kwargs):
        log.debug(f"mkdocstrings.plugin: Fixing references in page {page.file.src_path}")
        soup = BeautifulSoup(output, "html.parser")
        tags = soup.find_all(refs)
        for tag in tags:
            tag_str = str(tag)
            new_str = AUTO_REF.sub(self.fix_ref, tag_str)
            if new_str != tag_str:
                tag.replace_with(BeautifulSoup(new_str, "html.parser"))
            else:
                if log.isEnabledFor(logging.WARNING):
                    ref_list = [i[1] for i in AUTO_REF.findall(tag_str)]
                    for ref in ref_list:
                        log.warning(f"mkdocstrings.plugin: Reference '{ref}' in page {page.file.src_path} was not mapped: could not fix it")
        return str(soup)

    def fix_ref(self, match):
        groups = match.groupdict()
        identifier = groups["identifier"]
        title = groups["title"]
        if title and not identifier:
            identifier, title = title, identifier
        try:
            url = self.url_map[identifier]
        except KeyError:
            if title:
                return f"[{title}][{identifier}]"
            return f"[{identifier}][]"
        else:
            return f'<a href="{url}">{title or identifier}</a>'

    def on_post_build(self, config, **kwargs):
        log.debug("mkdocstrings.plugin: Tearing handlers down")
        teardown()


def refs(tag):
    return tag.name in ("p", "li", "td") and AUTO_REF.search(tag.text)
