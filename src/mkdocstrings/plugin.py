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

from __future__ import annotations

import datetime
import functools
import os
import sys
from concurrent import futures
from io import BytesIO
from typing import TYPE_CHECKING, Any, Callable, Iterable, List, Mapping, Tuple, TypeVar

from mkdocs.config import Config
from mkdocs.config import config_options as opt
from mkdocs.plugins import BasePlugin
from mkdocs.utils import write_file
from mkdocs_autorefs.plugin import AutorefsConfig, AutorefsPlugin

from mkdocstrings._cache import download_and_cache_url, download_url_with_gz
from mkdocstrings.extension import MkdocstringsExtension
from mkdocstrings.handlers.base import BaseHandler, Handlers
from mkdocstrings.loggers import get_logger

if TYPE_CHECKING:
    from jinja2.environment import Environment
    from mkdocs.config.defaults import MkDocsConfig

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

log = get_logger(__name__)

InventoryImportType = List[Tuple[str, Mapping[str, Any]]]
InventoryLoaderType = Callable[..., Iterable[Tuple[str, str]]]

P = ParamSpec("P")
R = TypeVar("R")


def list_to_tuple(function: Callable[P, R]) -> Callable[P, R]:
    """Decorater to convert lists to tuples in the arguments."""

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        safe_args = [tuple(item) if isinstance(item, list) else item for item in args]
        if kwargs:
            kwargs = {key: tuple(value) if isinstance(value, list) else value for key, value in kwargs.items()}  # type: ignore[assignment]
        return function(*safe_args, **kwargs)  # type: ignore[arg-type]

    return wrapper


class PluginConfig(Config):
    """The configuration options of `mkdocstrings`, written in `mkdocs.yml`."""

    handlers = opt.Type(dict, default={})
    """
    Global configuration of handlers.

    You can set global configuration per handler, applied everywhere,
    but overridable in each "autodoc" instruction. Example:

    ```yaml
    plugins:
      - mkdocstrings:
          handlers:
            python:
              options:
                option1: true
                option2: "value"
            rust:
              options:
                option9: 2
    ```
    """

    default_handler = opt.Type(str, default="python")
    """The default handler to use. The value is the name of the handler module. Default is "python"."""
    custom_templates = opt.Optional(opt.Dir(exists=True))
    """Location of custom templates to use when rendering API objects.

    Value should be the path of a directory relative to the MkDocs configuration file.
    """
    enable_inventory = opt.Optional(opt.Type(bool))
    """Whether to enable object inventory creation."""
    enabled = opt.Type(bool, default=True)
    """Whether to enable the plugin. Default is true. If false, *mkdocstrings* will not collect or render anything."""


class MkdocstringsPlugin(BasePlugin[PluginConfig]):
    """An `mkdocs` plugin.

    This plugin defines the following event hooks:

    - `on_config`
    - `on_env`
    - `on_post_build`

    Check the [Developing Plugins](https://www.mkdocs.org/user-guide/plugins/#developing-plugins) page of `mkdocs`
    for more information about its plugin system.
    """

    css_filename = "assets/_mkdocstrings.css"

    def __init__(self) -> None:
        """Initialize the object."""
        super().__init__()
        self._handlers: Handlers | None = None

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

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig | None:
        """Instantiate our Markdown extension.

        Hook for the [`on_config` event](https://www.mkdocs.org/user-guide/plugins/#on_config).
        In this hook, we instantiate our [`MkdocstringsExtension`][mkdocstrings.extension.MkdocstringsExtension]
        and add it to the list of Markdown extensions used by `mkdocs`.

        We pass this plugin's configuration dictionary to the extension when instantiating it (it will need it
        later when processing markdown to get handlers and their global configurations).

        Arguments:
            config: The MkDocs config object.

        Returns:
            The modified config.
        """
        if not self.plugin_enabled:
            log.debug("Plugin is not enabled. Skipping.")
            return config
        log.debug("Adding extension to the list")

        theme_name = config.theme.name or os.path.dirname(config.theme.dirs[0])

        to_import: InventoryImportType = []
        for handler_name, conf in self.config.handlers.items():
            for import_item in conf.pop("import", ()):
                if isinstance(import_item, str):
                    import_item = {"url": import_item}  # noqa: PLW2901
                to_import.append((handler_name, import_item))

        extension_config = {
            "theme_name": theme_name,
            "mdx": config.markdown_extensions,
            "mdx_configs": config.mdx_configs,
            "mkdocstrings": self.config,
            "mkdocs": config,
        }
        self._handlers = Handlers(extension_config)

        autorefs: AutorefsPlugin
        try:
            # If autorefs plugin is explicitly enabled, just use it.
            autorefs = config.plugins["autorefs"]  # type: ignore[assignment]
            log.debug(f"Picked up existing autorefs instance {autorefs!r}")
        except KeyError:
            # Otherwise, add a limited instance of it that acts only on what's added through `register_anchor`.
            autorefs = AutorefsPlugin()
            autorefs.config = AutorefsConfig()
            autorefs.scan_toc = False
            config.plugins["autorefs"] = autorefs
            log.debug(f"Added a subdued autorefs instance {autorefs!r}")
        # Add collector-based fallback in either case.
        autorefs.get_fallback_anchor = self.handlers.get_anchors

        mkdocstrings_extension = MkdocstringsExtension(extension_config, self.handlers, autorefs)
        config.markdown_extensions.append(mkdocstrings_extension)  # type: ignore[arg-type]

        config.extra_css.insert(0, self.css_filename)  # So that it has lower priority than user files.

        self._inv_futures = {}
        if to_import:
            inv_loader = futures.ThreadPoolExecutor(4)
            for handler_name, import_item in to_import:
                loader = self.get_handler(handler_name).load_inventory
                future = inv_loader.submit(
                    self._load_inventory,  # type: ignore[misc]
                    loader,
                    **import_item,
                )
                self._inv_futures[future] = (loader, import_item)
            inv_loader.shutdown(wait=False)

        return config

    @property
    def inventory_enabled(self) -> bool:
        """Tell if the inventory is enabled or not.

        Returns:
            Whether the inventory is enabled.
        """
        inventory_enabled = self.config.enable_inventory
        if inventory_enabled is None:
            inventory_enabled = any(handler.enable_inventory for handler in self.handlers.seen_handlers)
        return inventory_enabled

    @property
    def plugin_enabled(self) -> bool:
        """Tell if the plugin is enabled or not.

        Returns:
            Whether the plugin is enabled.
        """
        return self.config.enabled

    def on_env(self, env: Environment, config: MkDocsConfig, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Extra actions that need to happen after all Markdown rendering and before HTML rendering.

        Hook for the [`on_env` event](https://www.mkdocs.org/user-guide/plugins/#on_env).

        - Write mkdocstrings' extra files into the site dir.
        - Gather results from background inventory download tasks.
        """
        if not self.plugin_enabled:
            return
        if self._handlers:
            css_content = "\n".join(handler.extra_css for handler in self.handlers.seen_handlers)
            write_file(css_content.encode("utf-8"), os.path.join(config.site_dir, self.css_filename))

            if self.inventory_enabled:
                log.debug("Creating inventory file objects.inv")
                inv_contents = self.handlers.inventory.format_sphinx()
                write_file(inv_contents, os.path.join(config.site_dir, "objects.inv"))

        if self._inv_futures:
            log.debug(f"Waiting for {len(self._inv_futures)} inventory download(s)")
            futures.wait(self._inv_futures, timeout=30)
            results = {}
            # Reversed order so that pages from first futures take precedence:
            for fut in reversed(list(self._inv_futures)):
                try:
                    results.update(fut.result())
                except Exception as error:  # noqa: BLE001
                    loader, import_item = self._inv_futures[fut]
                    loader_name = loader.__func__.__qualname__
                    log.error(f"Couldn't load inventory {import_item} through {loader_name}: {error}")  # noqa: TRY400
            for page, identifier in results.items():
                config.plugins["autorefs"].register_url(page, identifier)  # type: ignore[attr-defined]
            self._inv_futures = {}

    def on_post_build(
        self,
        config: MkDocsConfig,  # noqa: ARG002
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Teardown the handlers.

        Hook for the [`on_post_build` event](https://www.mkdocs.org/user-guide/plugins/#on_post_build).
        This hook is used to teardown all the handlers that were instantiated and cached during documentation buildup.

        For example, a handler could open a subprocess in the background and keep it open
        to feed it "autodoc" instructions and get back JSON data. If so, it should then close the subprocess at some point:
        the proper place to do this is in the handler's `teardown` method, which is indirectly called by this hook.

        Arguments:
            config: The MkDocs config object.
            **kwargs: Additional arguments passed by MkDocs.
        """
        if not self.plugin_enabled:
            return

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
    # lru_cache does not allow mutable arguments such lists, but that is what we load from YAML config.
    @list_to_tuple
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
        content = download_and_cache_url(url, download_url_with_gz, datetime.timedelta(days=1))
        result = dict(loader(BytesIO(content), url=url, **kwargs))
        log.debug(f"Loaded inventory from {url!r}: {len(result)} items")
        return result
