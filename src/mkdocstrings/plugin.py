"""
This module contains the `mkdocs` plugin.

The plugin instantiates a Markdown extension ([`MkdocstringsExtension`][mkdocstrings.extension.MkdocstringsExtension]),
and adds it to the list of Markdown extensions used by `mkdocs`
during the [`on_config` event hook](https://www.mkdocs.org/user-guide/plugins/#on_config).

After each page is processed by the Markdown converter, this plugin stores absolute URLs of every HTML anchors
it finds to later be able to fix unresolved references.
It stores them during the [`on_page_contents` event hook](https://www.mkdocs.org/user-guide/plugins/#on_page_contents).

Just before writing the final HTML to the disc, during the
[`on_post_page` event hook](https://www.mkdocs.org/user-guide/plugins/#on_post_page),
this plugin searches for references of the form `[identifier][]` or `[title][identifier]` that were not resolved,
and fixes them using the previously stored identifier-URL mapping.

Once the documentation is built, the [`on_post_build` event hook](https://www.mkdocs.org/user-guide/plugins/#on_post_build)
is triggered and calls the [`handlers.teardown()` method][mkdocstrings.handlers.teardown]. This method is used
to teardown the [handlers][mkdocstrings.handlers] that were instantiated during documentation buildup.

Finally, when serving the documentation, it can add directories to watch
during the [`on_serve` event hook](https://www.mkdocs.org/user-guide/plugins/#on_serve).
"""

import logging
import random
import re
import string
from typing import Callable, List, Match, Pattern, Tuple

from bs4 import BeautifulSoup
from bs4.element import NavigableString
from livereload import Server
from mkdocs.config import Config
from mkdocs.config.config_options import Type as MkType
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page
from mkdocs.structure.toc import AnchorLink
from mkdocs.utils import log

from .extension import MkdocstringsExtension
from .handlers import teardown

SELECTION_OPTS_KEY: str = "selection"
"""The name of the selection parameter in YAML configuration blocks."""
RENDERING_OPTS_KEY: str = "rendering"
"""The name of the rendering parameter in YAML configuration blocks."""

AUTO_REF: Pattern = re.compile(r"\[(?P<title>.+?)\]\[(?P<identifier>.*?)\]")
"""
A regular expression to match unresolved Markdown references
in the [`on_post_page` hook][mkdocstrings.plugin.MkdocstringsPlugin.on_post_page].
"""


class MkdocstringsPlugin(BasePlugin):
    """
    An `mkdocs` plugin.

    This plugin defines the following event hooks:

    - `on_config`
    - `on_page_contents`
    - `on_post_page`
    - `on_post_build`
    - `on_serve`

    Check the [Developing Plugins](https://www.mkdocs.org/user-guide/plugins/#developing-plugins) page of `mkdocs`
    for more information about its plugin system..
    """

    config_scheme: Tuple[Tuple[str, MkType]] = (
        ("watch", MkType(list, default=[])),
        ("handlers", MkType(dict, default={})),
        ("default_handler", MkType(str, default="python")),
    )
    """
    The configuration options of `mkdocstrings`, written in `mkdocs.yml`.

    Available options are:

    - __`watch`__: A list of directories to watch. Only used when serving the documentation with mkdocs.
       Whenever a file changes in one of directories, the whole documentation is built again, and the browser refreshed.
    - __`default_handler`__: The default handler to use. The value is the name of the handler module. Default is "python".
    - __`handlers`__: Global configuration of handlers. You can set global configuration per handler, applied everywhere,
      but overridable in each "autodoc" instruction. Example:

    ```yaml
    plugins:
      - mkdocstrings:
          handlers:
            python:
              selection:
                selection_opt: true
              rendering:
                 rendering_opt: "value"
            rust:
              selection:
                selection_opt: 2
    ```
    """

    def __init__(self) -> None:
        super(MkdocstringsPlugin, self).__init__()
        self.mkdocstrings_extension = None
        self.url_map = {}

    def on_serve(self, server: Server, config: Config, **kwargs) -> Server:
        """
        Hook for the [`on_serve` event](https://www.mkdocs.org/user-guide/plugins/#on_serve).

        In this hook, we add the directories specified in the plugin's configuration to the list of directories
        watched by `mkdocs`. Whenever a change occurs in one of these directories, the documentation is built again
        and the site reloaded.

        Note:
            The implementation is a hack. We are retrieving the watch function from a protected attribute.
            See issue [mkdocs/mkdocs#1952](https://github.com/mkdocs/mkdocs/issues/1952) for more information.
        """
        builder = list(server.watcher._tasks.values())[0]["func"]
        for element in self.config["watch"]:
            log.debug(f"mkdocstrings.plugin: Adding directory '{element}' to watcher")
            server.watch(element, builder)
        return server

    def on_config(self, config: Config, **kwargs) -> Config:
        """
        Hook for the [`on_config` event](https://www.mkdocs.org/user-guide/plugins/#on_config).

        In this hook, we instantiate our [`MkdocstringsExtension`][mkdocstrings.extension.MkdocstringsExtension]
        and add it to the list of Markdown extensions used by `mkdocs`.

        We pass this plugin's configuration dictionary to the extension when instantiating it (it will need it
        later when processing markdown to get handlers and their global configurations).
        """
        log.debug("mkdocstrings.plugin: Adding extension to the list")

        extension_config = dict(
            theme_name=config["theme"].name,
            mdx=config["markdown_extensions"],
            mdx_configs=config["mdx_configs"],
            mkdocstrings=self.config,
        )

        self.mkdocstrings_extension = MkdocstringsExtension(config=extension_config)
        config["markdown_extensions"].append(self.mkdocstrings_extension)
        return config

    def on_page_content(self, html: str, page: Page, config: Config, files: Files, **kwargs) -> str:
        """
        Hook for the [`on_page_contents` event](https://www.mkdocs.org/user-guide/plugins/#on_page_contents).

        In this hook, we map the IDs of every anchor found in the table of contents to the anchors absolute URLs.
        This mapping will be used later to fix unresolved reference of the form `[title][identifier]` or
        `[identifier][]`.
        """
        log.debug(f"mkdocstrings.plugin: Mapping identifiers to URLs for page {page.file.src_path}")
        for item in page.toc.items:
            self.map_urls(page.abs_url, item)
        return html

    def map_urls(self, base_url: str, anchor: AnchorLink) -> None:
        """
        Recurse on every anchor to map its ID to its absolute URL.

        This method populates `self.url_map` by side-effect.

        Arguments:
            base_url: The base URL to use as a prefix for each anchor's relative URL.
            anchor: The anchor to process and to recurse on.
        """
        self.url_map[anchor.id] = base_url + anchor.url
        for child in anchor.children:
            self.map_urls(base_url, child)

    def on_post_page(self, output: str, page: Page, config: Config, **kwargs) -> str:
        """
        Hook for the [`on_post_page` event](https://www.mkdocs.org/user-guide/plugins/#on_post_page).

        In this hook, we try to fix unresolved references of the form `[title][identifier]` or `[identifier][]`.
        Doing that allows the user of `mkdocstrings` to cross-reference objects in their documentation strings.
        It uses the native Markdown syntax so it's easy to remember and use.

        We log a warning for each reference that we couldn't map to an URL, but try to be smart and ignore identifiers
        that do not look legitimate (sometimes documentation can contain strings matching
        our [`AUTO_REF`][mkdocstrings.plugin.AUTO_REF] regular expression that did not intend to reference anything).
        We currently ignore references when their identifier contains a space or a slash.
        """
        log.debug(f"mkdocstrings.plugin: Fixing references in page {page.file.src_path}")

        placeholder = Placeholder()
        while re.search(placeholder.seed, output) or any(placeholder.seed in url for url in self.url_map.values()):
            placeholder.set_seed()

        unmapped, unintended = [], []
        soup = BeautifulSoup(output, "html.parser")
        placeholder.replace_code_tags(soup)
        fixed_soup = AUTO_REF.sub(self.fix_ref(unmapped, unintended), str(soup))

        if unmapped or unintended:
            # We do nothing with unintended refs
            if unmapped and log.isEnabledFor(logging.WARNING):
                for ref in unmapped:
                    log.warning(
                        f"mkdocstrings.plugin: {page.file.src_path}: Could not fix ref '[{ref}]'.\n    "
                        f"The referenced object was not both collected and rendered."
                    )

        return placeholder.restore_code_tags(fixed_soup)

    def fix_ref(self, unmapped: List[str], unintended: List[str]) -> Callable:
        """
        Return a `repl` function for [`re.sub`](https://docs.python.org/3/library/re.html#re.sub).

        In our context, we match Markdown references and replace them with HTML links.

        When the matched reference's identifier contains a space or slash, we append the identifier to the outer
        `unintended` list to tell the caller that this unresolved reference should be ignored as it's probably
        not intended as a reference.

        When the matched reference's identifier was not mapped to an URL, we append the identifier to the outer
        `unmapped` list. It generally means the user is trying to cross-reference an object that was not collected
        and rendered, making it impossible to link to it. We catch this exception in the caller to issue a warning.

        Arguments:
            unmapped: A list to store unmapped identifiers.
            unintended: A list to store identifiers of unintended references.

        Returns:
            The actual function accepting a [`Match` object](https://docs.python.org/3/library/re.html#match-objects)
            and returning the replacement strings.
        """

        def inner(match: Match):
            groups = match.groupdict()
            identifier = groups["identifier"]
            title = groups["title"]

            if title and not identifier:
                identifier, title = title, identifier

            try:
                url = self.url_map[identifier]
            except KeyError:
                if " " in identifier or "/" in identifier:
                    # invalid identifier, must not be a intended reference
                    unintended.append(identifier)
                else:
                    unmapped.append(identifier)

                if not title:
                    return f"[{identifier}][]"
                return f"[{title}][{identifier}]"

            # TODO: we could also use a config option to ignore some identifiers
            # and to map others to URLs, something like:
            # references:
            #   ignore:
            #     - "USERNAME:PASSWORD@"
            #   map:
            #     some-id: https://example.com

            return f'<a href="{url}">{title or identifier}</a>'

        return inner

    def on_post_build(self, config: Config, **kwargs) -> None:
        """
        Hook for the [`on_post_build` event](https://www.mkdocs.org/user-guide/plugins/#on_post_build).

        This hook is used to teardown all the handlers that were instantiated and cached during documentation buildup.

        For example, the [Python handler's collector][mkdocstrings.handlers.python.PythonCollector] opens a subprocess
        in the background and keeps it open to feed it the "autodoc" instructions and get back JSON data. Therefore,
        it must close it at some point, and it does it in its
        [`teardown()` method][mkdocstrings.handlers.python.PythonCollector.teardown] which is indirectly called by
        this hook.
        """
        log.debug("mkdocstrings.plugin: Tearing handlers down")
        teardown()


class Placeholder:
    """
    This class is used as a placeholder store.

    Placeholders are random, unique strings that temporarily replace `<code>` nodes in an HTML tree.

    Why do we replace these nodes with such strings? Because we want to fix cross-references that were not
    resolved during Markdown conversion, and we must never touch to what's inside of a code block.
    To ease the process, instead of selecting nodes in the HTML tree with complex filters (I tried, believe me),
    we simply "hide" the code nodes, and bulk-replace unresolved cross-references in the whole HTML text at once,
    with a regular expression substitution. Once it's done, we bulk-replace code nodes back, with a regular expression
    substitution again.
    """

    def __init__(self) -> None:
        self.ids = {}
        self.seed = None
        self.set_seed()

    def store(self, value: str) -> str:
        """
        Store a text under a unique ID, return that ID.

        Arguments:
            value: The text to store.

        Returns:
            The ID under which the text is stored.
        """
        i = self.get_id()
        while i in self.ids:
            i = self.get_id()
        self.ids[i] = value
        return i

    def get_id(self) -> str:
        """Return a random, unique string."""
        return f"{self.seed}{random.randint(0, 1000000)}"  # nosec: it's not for security/cryptographic purposes

    def set_seed(self) -> None:
        """Reset the seed in `self.seed` with a random string."""
        self.seed = "".join(random.choices(string.ascii_letters + string.digits, k=16))

    def replace_code_tags(self, soup: str) -> None:
        """
        Recursively replace code nodes with navigable strings whose values are unique IDs.

        Arguments:
            soup: The root tag of a BeautifulSoup HTML tree.
        """

        def recursive_replace(tag):
            if hasattr(tag, "contents"):
                for i in range(len(tag.contents)):
                    child = tag.contents[i]
                    if child.name == "code":
                        tag.contents[i] = NavigableString(self.store(str(child)))
                    else:
                        recursive_replace(child)

        recursive_replace(soup)

    def restore_code_tags(self, soup_str: str) -> str:
        """
        Restore code nodes previously replaced by unique placeholders.

        Args:
            soup_str: HTML text.

        Returns:
            The same HTML text with placeholders replaced by their respective original code nodes.
        """

        def replace_placeholder(match):
            placeholder = match.groups()[0]
            return self.ids[placeholder]

        return re.sub(rf"({self.seed}\d+)", replace_placeholder, soup_str)
