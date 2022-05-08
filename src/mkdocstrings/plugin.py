"""This module contains the "mkdocstrings" plugin for MkDocs.

The plugin instantiates a Markdown extension ([`MkdocstringsExtension`][mkdocstrings.extension.MkdocstringsExtension]),
and adds it to the list of Markdown extensions used by `mkdocs`
during the [`on_config` event hook](https://www.mkdocs.org/user-guide/plugins/#on_config).

Once the documentation is built, the [`on_post_build` event hook](https://www.mkdocs.org/user-guide/plugins/#on_post_build)
is triggered and calls the [`handlers.teardown()` method][mkdocstrings.handlers.base.Handlers.teardown]. This method is
used to teardown the handlers that were instantiated during documentation buildup.

Finally, when serving the documentation, it can add directories to watch
during the [`on_serve` event hook](https://www.mkdocs.org/user-guide/plugins/#on_serve).
"""

import collections
import functools
import gzip
import os
from concurrent import futures
from typing import Any, BinaryIO, Callable, Iterable, List, Mapping, Optional, Tuple
from urllib import request
from warnings import warn

from mkdocs.config import Config
from mkdocs.config.config_options import Type as MkType
from mkdocs.livereload import LiveReloadServer
from mkdocs.plugins import BasePlugin
from mkdocs.utils import write_file
from mkdocs_autorefs.plugin import AutorefsPlugin

from mkdocstrings.extension import MkdocstringsExtension
from mkdocstrings.handlers.base import BaseHandler, Handlers
from mkdocstrings.loggers import get_logger

log = get_logger(__name__)

SELECTION_OPTS_KEY: str = "selection"
"""The name of the selection parameter in YAML configuration blocks."""
RENDERING_OPTS_KEY: str = "rendering"
"""The name of the rendering parameter in YAML configuration blocks."""

InventoryImportType = List[Tuple[str, Mapping[str, Any]]]
InventoryLoaderType = Callable[..., Iterable[Tuple[str, str]]]


class MkdocstringsPlugin(BasePlugin):
    """An `mkdocs` plugin.

    This plugin defines the following event hooks:

    - `on_config`
    - `on_env`
    - `on_post_build`
    - `on_serve`

    Check the [Developing Plugins](https://www.mkdocs.org/user-guide/plugins/#developing-plugins) page of `mkdocs`
    for more information about its plugin system.
    """

    config_scheme: Tuple[Tuple[str, MkType]] = (
        ("watch", MkType(list, default=[])),  # type: ignore
        ("handlers", MkType(dict, default={})),
        ("default_handler", MkType(str, default="python")),
        ("custom_templates", MkType(str, default=None)),
        ("enable_inventory", MkType(bool, default=None)),
    )
    """
    The configuration options of `mkdocstrings`, written in `mkdocs.yml`.

    Available options are:

    - **`watch` (deprecated)**: A list of directories to watch. Only used when serving the documentation with mkdocs.
       Whenever a file changes in one of directories, the whole documentation is built again, and the browser refreshed.
       Deprecated in favor of the now built-in `watch` feature of MkDocs.
    - **`default_handler`**: The default handler to use. The value is the name of the handler module. Default is "python".
    - **`handlers`**: Global configuration of handlers. You can set global configuration per handler, applied everywhere,
      but overridable in each "autodoc" instruction. Example:

    ```yaml
    plugins:
      - mkdocstrings:
          handlers:
            python:
              options:
                selection_opt: true
                rendering_opt: "value"
            rust:
              options:
                selection_opt: 2
    ```
    """

    css_filename = "assets/_mkdocstrings.css"

    def __init__(self) -> None:
        """Initialize the object."""
        super().__init__()
        self._handlers: Optional[Handlers] = None

    @property
    def handlers(self) -> Handlers:
        """Get the instance of [mkdocstrings.handlers.base.Handlers][] for this plugin/build.

        Raises:
            RuntimeError: If the plugin hasn't been initialized with a config.

        Returns:
            An instance of [mkdocstrings.handlers.base.Handlers][] (the same throughout the build).
        """
        if not self._handlers:
            raise RuntimeError("The plugin hasn't been initialized with a config yet")
        return self._handlers

    # TODO: remove once watch feature is removed
    def on_serve(self, server: LiveReloadServer, builder: Callable, **kwargs: Any):  # noqa: W0613 (unused arguments)
        """Watch directories.

        Hook for the [`on_serve` event](https://www.mkdocs.org/user-guide/plugins/#on_serve).
        In this hook, we add the directories specified in the plugin's configuration to the list of directories
        watched by `mkdocs`. Whenever a change occurs in one of these directories, the documentation is built again
        and the site reloaded.

        Arguments:
            server: The `livereload` server instance.
            builder: The function to build the site.
            **kwargs: Additional arguments passed by MkDocs.
        """
        if self.config["watch"]:
            warn(
                "mkdocstrings' watch feature is deprecated in favor of MkDocs' watch feature, "
                "see https://www.mkdocs.org/user-guide/configuration/#watch.",
                DeprecationWarning,
            )
            for element in self.config["watch"]:
                log.debug(f"Adding directory '{element}' to watcher")
                server.watch(element, builder)

    def on_config(self, config: Config, **kwargs: Any) -> Config:  # noqa: W0613 (unused arguments)
        """Instantiate our Markdown extension.

        Hook for the [`on_config` event](https://www.mkdocs.org/user-guide/plugins/#on_config).
        In this hook, we instantiate our [`MkdocstringsExtension`][mkdocstrings.extension.MkdocstringsExtension]
        and add it to the list of Markdown extensions used by `mkdocs`.

        We pass this plugin's configuration dictionary to the extension when instantiating it (it will need it
        later when processing markdown to get handlers and their global configurations).

        Arguments:
            config: The MkDocs config object.
            **kwargs: Additional arguments passed by MkDocs.

        Returns:
            The modified config.
        """
        log.debug("Adding extension to the list")

        theme_name = None
        if config["theme"].name is None:
            theme_name = os.path.dirname(config["theme"].dirs[0])
        else:
            theme_name = config["theme"].name

        to_import: InventoryImportType = []
        for handler_name, conf in self.config["handlers"].items():
            for import_item in conf.pop("import", ()):
                if isinstance(import_item, str):
                    import_item = {"url": import_item}
                to_import.append((handler_name, import_item))

        extension_config = {
            "site_name": config["site_name"],
            "config_file_path": config["config_file_path"],
            "theme_name": theme_name,
            "mdx": config["markdown_extensions"],
            "mdx_configs": config["mdx_configs"],
            "mkdocstrings": self.config,
        }
        self._handlers = Handlers(extension_config)

        try:  # noqa: WPS229
            # If autorefs plugin is explicitly enabled, just use it.
            autorefs = config["plugins"]["autorefs"]
            log.debug(f"Picked up existing autorefs instance {autorefs!r}")
        except KeyError:
            # Otherwise, add a limited instance of it that acts only on what's added through `register_anchor`.
            autorefs = AutorefsPlugin()
            autorefs.scan_toc = False
            config["plugins"]["autorefs"] = autorefs
            log.debug(f"Added a subdued autorefs instance {autorefs!r}")
        # Add collector-based fallback in either case.
        autorefs.get_fallback_anchor = self.handlers.get_anchors

        mkdocstrings_extension = MkdocstringsExtension(extension_config, self.handlers, autorefs)
        config["markdown_extensions"].append(mkdocstrings_extension)

        config["extra_css"].insert(0, self.css_filename)  # So that it has lower priority than user files.

        self._inv_futures = []
        if to_import:
            inv_loader = futures.ThreadPoolExecutor(4)
            for handler_name, import_item in to_import:  # noqa: WPS440
                future = inv_loader.submit(
                    self._load_inventory, self.get_handler(handler_name).load_inventory, **import_item
                )
                self._inv_futures.append(future)
            inv_loader.shutdown(wait=False)

        return config

    @property
    def inventory_enabled(self) -> bool:
        """Tell if the inventory is enabled or not.

        Returns:
            Whether the inventory is enabled.
        """
        inventory_enabled = self.config["enable_inventory"]
        if inventory_enabled is None:
            inventory_enabled = any(handler.enable_inventory for handler in self.handlers.seen_handlers)
        return inventory_enabled

    def on_env(self, env, config: Config, **kwargs):
        """Extra actions that need to happen after all Markdown rendering and before HTML rendering.

        Hook for the [`on_env` event](https://www.mkdocs.org/user-guide/plugins/#on_env).

        - Write mkdocstrings' extra files into the site dir.
        - Gather results from background inventory download tasks.
        """
        if self._handlers:
            css_content = "\n".join(handler.extra_css for handler in self.handlers.seen_handlers)
            write_file(css_content.encode("utf-8"), os.path.join(config["site_dir"], self.css_filename))

            if self.inventory_enabled:
                log.debug("Creating inventory file objects.inv")
                inv_contents = self.handlers.inventory.format_sphinx()
                write_file(inv_contents, os.path.join(config["site_dir"], "objects.inv"))

        if self._inv_futures:
            log.debug(f"Waiting for {len(self._inv_futures)} inventory download(s)")
            futures.wait(self._inv_futures, timeout=30)
            for page, identifier in collections.ChainMap(*(fut.result() for fut in self._inv_futures)).items():
                config["plugins"]["autorefs"].register_url(page, identifier)
            self._inv_futures = []

    def on_post_build(
        self, config: Config, **kwargs: Any
    ) -> None:  # noqa: W0613,R0201 (unused arguments, cannot be static)
        """Teardown the handlers.

        Hook for the [`on_post_build` event](https://www.mkdocs.org/user-guide/plugins/#on_post_build).
        This hook is used to teardown all the handlers that were instantiated and cached during documentation buildup.

        For example, a handler could open a subprocess in the background and keep it open
        to feed it "autodoc" instructions and get back JSON data. If so, it should then close the subprocess at some point:
        the proper place to do this is in the collector's `teardown` method, which is indirectly called by this hook.

        Arguments:
            config: The MkDocs config object.
            **kwargs: Additional arguments passed by MkDocs.
        """
        for future in self._inv_futures:
            future.cancel()

        if self._handlers:
            log.debug("Tearing handlers down")
            self.handlers.teardown()

    def get_handler(self, handler_name: str) -> BaseHandler:
        """Get a handler by its name. See [mkdocstrings.handlers.base.Handlers.get_handler][].

        Arguments:
            handler_name: The name of the handler.

        Returns:
            An instance of a subclass of [`BaseHandler`][mkdocstrings.handlers.base.BaseHandler].
        """
        return self.handlers.get_handler(handler_name)

    @classmethod
    @functools.lru_cache(maxsize=None)
    def _load_inventory(cls, loader: InventoryLoaderType, url: str, **kwargs: Any) -> Mapping[str, str]:
        """Download and process inventory files using a handler.

        Arguments:
            loader: A function returning a sequence of pairs (identifier, url).
            url: The URL to download and process.
            **kwargs: Extra arguments to pass to the loader.

        Returns:
            A mapping from identifier to absolute URL.
        """
        log.debug(f"Downloading inventory from {url!r}")
        req = request.Request(url, headers={"Accept-Encoding": "gzip", "User-Agent": "mkdocstrings/0.15.0"})
        with request.urlopen(req) as resp:  # noqa: S310 (URL audit OK: comes from a checked-in config)
            content: BinaryIO = resp
            if "gzip" in resp.headers.get("content-encoding", ""):
                content = gzip.GzipFile(fileobj=resp)  # type: ignore[assignment]
            result = dict(loader(content, url=url, **kwargs))
        log.debug(f"Loaded inventory from {url!r}: {len(result)} items")
        return result
