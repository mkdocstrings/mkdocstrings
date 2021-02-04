"""
This module contains the "mkdocs-autorefs" plugin.

After each page is processed by the Markdown converter, this plugin stores absolute URLs of every HTML anchors
it finds to later be able to fix unresolved references.
It stores them during the [`on_page_content` event hook](https://www.mkdocs.org/user-guide/plugins/#on_page_content).

Just before writing the final HTML to the disc, during the
[`on_post_page` event hook](https://www.mkdocs.org/user-guide/plugins/#on_post_page),
this plugin searches for references of the form `[identifier][]` or `[title][identifier]` that were not resolved,
and fixes them using the previously stored identifier-URL mapping.
"""

import logging
from typing import Callable, Dict, Optional

from mkdocs.config import Config
from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page
from mkdocs.structure.toc import AnchorLink
from mkdocs.utils import warning_filter

from mkdocs_autorefs.references import AutorefsExtension, fix_refs

log = logging.getLogger(f"mkdocs.plugins.{__name__}")
log.addFilter(warning_filter)


class AutorefsPlugin(BasePlugin):
    """
    An `mkdocs` plugin.

    This plugin defines the following event hooks:

    - `on_config`
    - `on_page_content`
    - `on_post_page`

    Check the [Developing Plugins](https://www.mkdocs.org/user-guide/plugins/#developing-plugins) page of `mkdocs`
    for more information about its plugin system.
    """

    scan_toc: bool = True
    current_page: Optional[str] = None

    def __init__(self) -> None:
        """Initialize the object."""
        super().__init__()
        self._url_map: Dict[str, str] = {}
        self.get_fallback_anchor: Callable[[str], Optional[str]] = lambda identifier: None

    def register_anchor(self, page: str, anchor: str):
        """
        Register that an anchor corresponding to an identifier was encountered when rendering the page.

        Arguments:
            page: The relative URL of the current page. Examples: `'foo/bar/'`, `'foo/index.html'`
            anchor: The HTML anchor (without '#') as a string.
        """
        self._url_map[anchor] = f"{page}#{anchor}"

    def get_item_url(self, anchor: str) -> str:
        """
        Return a site-relative URL with anchor to the identifier, if it's present anywhere.

        Arguments:
            anchor: The identifier (one that [collect][mkdocstrings.handlers.base.BaseCollector.collect] can accept).

        Returns:
            A site-relative URL.

        Raises:
            KeyError: If there isn't an item by this identifier anywhere on the site.
        """
        try:
            return self._url_map[anchor]
        except KeyError:
            new_anchor = self.get_fallback_anchor(anchor)
            if new_anchor and new_anchor in self._url_map:
                return self._url_map[new_anchor]
            raise

    def on_config(self, config: Config, **kwargs) -> Config:  # noqa: W0613,R0201 (unused arguments, cannot be static)
        """
        Instantiate our Markdown extension.

        Hook for the [`on_config` event](https://www.mkdocs.org/user-guide/plugins/#on_config).
        In this hook, we instantiate our [`AutorefsExtension`][mkdocs_autorefs.references.AutorefsExtension]
        and add it to the list of Markdown extensions used by `mkdocs`.

        Arguments:
            config: The MkDocs config object.
            kwargs: Additional arguments passed by MkDocs.

        Returns:
            The modified config.
        """
        log.debug("Adding AutorefsExtension to the list")
        config["markdown_extensions"].append(AutorefsExtension())
        return config

    def on_page_markdown(self, markdown: str, page: Page, **kwargs) -> str:  # noqa: W0613 (unused arguments)
        """
        Remember which page is the current one.

        Arguments:
            markdown: Input Markdown.
            page: The related MkDocs page instance.
            kwargs: Additional arguments passed by MkDocs.

        Returns:
            The same Markdown. We only use this hook to map anchors to URLs.
        """
        self.current_page = page.url
        return markdown

    def on_page_content(self, html: str, page: Page, **kwargs) -> str:  # noqa: W0613 (unused arguments)
        """
        Map anchors to URLs.

        Hook for the [`on_page_content` event](https://www.mkdocs.org/user-guide/plugins/#on_page_content).
        In this hook, we map the IDs of every anchor found in the table of contents to the anchors absolute URLs.
        This mapping will be used later to fix unresolved reference of the form `[title][identifier]` or
        `[identifier][]`.

        Arguments:
            html: HTML converted from Markdown.
            page: The related MkDocs page instance.
            kwargs: Additional arguments passed by MkDocs.

        Returns:
            The same HTML. We only use this hook to map anchors to URLs.
        """
        if self.scan_toc:
            log.debug(f"Mapping identifiers to URLs for page {page.file.src_path}")
            for item in page.toc.items:
                self.map_urls(page.url, item)
        return html

    def map_urls(self, base_url: str, anchor: AnchorLink) -> None:
        """
        Recurse on every anchor to map its ID to its absolute URL.

        This method populates `self.url_map` by side-effect.

        Arguments:
            base_url: The base URL to use as a prefix for each anchor's relative URL.
            anchor: The anchor to process and to recurse on.
        """
        self.register_anchor(base_url, anchor.id)
        for child in anchor.children:
            self.map_urls(base_url, child)

    def on_post_page(self, output: str, page: Page, **kwargs) -> str:  # noqa: W0613 (unused arguments)
        """
        Fix cross-references.

        Hook for the [`on_post_page` event](https://www.mkdocs.org/user-guide/plugins/#on_post_page).
        In this hook, we try to fix unresolved references of the form `[title][identifier]` or `[identifier][]`.
        Doing that allows the user of `mkdocstrings` to cross-reference objects in their documentation strings.
        It uses the native Markdown syntax so it's easy to remember and use.

        We log a warning for each reference that we couldn't map to an URL, but try to be smart and ignore identifiers
        that do not look legitimate (sometimes documentation can contain strings matching
        our [`AUTO_REF_RE`][mkdocs_autorefs.references.AUTO_REF_RE] regular expression that did not intend to reference anything).
        We currently ignore references when their identifier contains a space or a slash.

        Arguments:
            output: HTML converted from Markdown.
            page: The related MkDocs page instance.
            kwargs: Additional arguments passed by MkDocs.

        Returns:
            Modified HTML.
        """
        log.debug(f"Fixing references in page {page.file.src_path}")

        fixed_output, unmapped = fix_refs(output, page.url, self.get_item_url)

        if unmapped and log.isEnabledFor(logging.WARNING):
            for ref in unmapped:
                log.warning(
                    f"{page.file.src_path}: Could not find cross-reference target '[{ref}]'",
                )

        return fixed_output
