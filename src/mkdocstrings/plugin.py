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
is triggered and calls the [`handlers.teardown()` method][mkdocstrings.handlers.base.Handlers.teardown]. This method is
used to teardown the handlers that were instantiated during documentation buildup.

Finally, when serving the documentation, it can add directories to watch
during the [`on_serve` event hook](https://www.mkdocs.org/user-guide/plugins/#on_serve).
"""

import logging
import os
from typing import Any, Callable, Dict, Optional, Tuple

from livereload import Server
from mkdocs.config import Config
from mkdocs.config.config_options import Type as MkType
from mkdocs.plugins import BasePlugin
from mkdocs.structure.pages import Page
from mkdocs.structure.toc import AnchorLink

from mkdocstrings.extension import MkdocstringsExtension
from mkdocstrings.handlers.base import BaseHandler, Handlers
from mkdocstrings.loggers import get_logger
from mkdocstrings.references import fix_refs

log = get_logger(__name__)

SELECTION_OPTS_KEY: str = "selection"
"""The name of the selection parameter in YAML configuration blocks."""
RENDERING_OPTS_KEY: str = "rendering"
"""The name of the rendering parameter in YAML configuration blocks."""


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
        ("watch", MkType(list, default=[])),  # type: ignore
        ("handlers", MkType(dict, default={})),
        ("default_handler", MkType(str, default="python")),
        ("custom_templates", MkType(str, default=None)),
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
              setup_commands:
                - "import os"
                - "import django"
                - "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_djang_app.settings')"
                - "django.setup()"
            rust:
              selection:
                selection_opt: 2
    ```
    """

    def __init__(self) -> None:
        """Initialize the object."""
        super().__init__()
        self.url_map: Dict[Any, str] = {}
        self.handlers: Optional[Handlers] = None

    def on_serve(self, server: Server, builder: Callable = None, **kwargs) -> Server:  # noqa: W0613 (unused arguments)
        """
        Watch directories.

        Hook for the [`on_serve` event](https://www.mkdocs.org/user-guide/plugins/#on_serve).
        In this hook, we add the directories specified in the plugin's configuration to the list of directories
        watched by `mkdocs`. Whenever a change occurs in one of these directories, the documentation is built again
        and the site reloaded.

        Arguments:
            server: The `livereload` server instance.
            builder: The function to build the site.
            kwargs: Additional arguments passed by MkDocs.

        Returns:
            The server instance.
        """
        if builder is None:
            # The builder parameter was added in mkdocs v1.1.1.
            # See issue https://github.com/mkdocs/mkdocs/issues/1952.
            builder = list(server.watcher._tasks.values())[0]["func"]  # noqa: W0212 (protected member)
        for element in self.config["watch"]:
            log.debug(f"Adding directory '{element}' to watcher")
            server.watch(element, builder)
        return server

    def on_config(self, config: Config, **kwargs) -> Config:  # noqa: W0613 (unused arguments)
        """
        Instantiate our Markdown extension.

        Hook for the [`on_config` event](https://www.mkdocs.org/user-guide/plugins/#on_config).
        In this hook, we instantiate our [`MkdocstringsExtension`][mkdocstrings.extension.MkdocstringsExtension]
        and add it to the list of Markdown extensions used by `mkdocs`.

        We pass this plugin's configuration dictionary to the extension when instantiating it (it will need it
        later when processing markdown to get handlers and their global configurations).

        Arguments:
            config: The MkDocs config object.
            kwargs: Additional arguments passed by MkDocs.

        Returns:
            The modified config.
        """
        log.debug("Adding extension to the list")

        theme_name = None
        if config["theme"].name is None:
            theme_name = os.path.dirname(config["theme"].dirs[0])
        else:
            theme_name = config["theme"].name

        extension_config = {
            "theme_name": theme_name,
            "mdx": config["markdown_extensions"],
            "mdx_configs": config["mdx_configs"],
            "mkdocstrings": self.config,
        }

        self.handlers = Handlers(extension_config)
        mkdocstrings_extension = MkdocstringsExtension(extension_config, self.handlers)
        config["markdown_extensions"].append(mkdocstrings_extension)
        return config

    def on_page_content(self, html: str, page: Page, **kwargs) -> str:  # noqa: W0613 (unused arguments)
        """
        Map anchors to URLs.

        Hook for the [`on_page_contents` event](https://www.mkdocs.org/user-guide/plugins/#on_page_contents).
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
        self.url_map[anchor.id] = base_url + anchor.url
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
        our [`AUTO_REF_RE`][mkdocstrings.references.AUTO_REF_RE] regular expression that did not intend to reference anything).
        We currently ignore references when their identifier contains a space or a slash.

        Arguments:
            output: HTML converted from Markdown.
            page: The related MkDocs page instance.
            kwargs: Additional arguments passed by MkDocs.

        Returns:
            Modified HTML.
        """
        log.debug(f"Fixing references in page {page.file.src_path}")

        fixed_output, unmapped = fix_refs(output, page.url, self.url_map)

        if unmapped and log.isEnabledFor(logging.WARNING):
            for ref in unmapped:
                log.warning(
                    f"{page.file.src_path}: Could not find cross-reference target '[{ref}]'",
                )

        return fixed_output

    def on_post_build(self, **kwargs) -> None:  # noqa: W0613,R0201 (unused arguments, cannot be static)
        """
        Teardown the handlers.

        Hook for the [`on_post_build` event](https://www.mkdocs.org/user-guide/plugins/#on_post_build).
        This hook is used to teardown all the handlers that were instantiated and cached during documentation buildup.

        For example, the [Python handler's collector][mkdocstrings.handlers.python.PythonCollector] opens a subprocess
        in the background and keeps it open to feed it the "autodoc" instructions and get back JSON data. Therefore,
        it must close it at some point, and it does it in its
        [`teardown()` method][mkdocstrings.handlers.python.PythonCollector.teardown] which is indirectly called by
        this hook.

        Arguments:
            kwargs: Additional arguments passed by MkDocs.
        """
        if self.handlers:
            log.debug("Tearing handlers down")
            self.handlers.teardown()

    def get_handler(self, handler_name: str) -> BaseHandler:
        """
        Get a handler by its name. See [mkdocstrings.handlers.base.Handlers.get_handler][].

        Arguments:
            handler_name: The name of the handler.

        Raises:
            RuntimeError: If the plugin hasn't been initialized with a config.

        Returns:
            An instance of a subclass of [`BaseHandler`][mkdocstrings.handlers.base.BaseHandler].
        """
        if not self.handlers:
            raise RuntimeError("The plugin hasn't been initialized with a config yet")
        return self.handlers.get_handler(handler_name)
