# This module contains the "mkdocstrings" plugin for MkDocs.
#
# The plugin instantiates a Markdown extension ([`MkdocstringsExtension`][mkdocstrings.MkdocstringsExtension]),
# and adds it to the list of Markdown extensions used by `mkdocs`
# during the [`on_config` event hook](https://www.mkdocs.org/user-guide/plugins/#on_config).
#
# Once the documentation is built, the [`on_post_build` event hook](https://www.mkdocs.org/user-guide/plugins/#on_post_build)
# is triggered and calls the [`handlers.teardown()` method][mkdocstrings.Handlers.teardown]. This method is
# used to teardown the handlers that were instantiated during documentation buildup.
#
# Finally, when serving the documentation, it can add directories to watch
# during the [`on_serve` event hook](https://www.mkdocs.org/user-guide/plugins/#on_serve).

from __future__ import annotations

import os
import re
from functools import partial
from inspect import signature
from re import Match
from typing import TYPE_CHECKING, Any
from warnings import catch_warnings, simplefilter

from mkdocs.config import Config
from mkdocs.config import config_options as opt
from mkdocs.plugins import BasePlugin, CombinedEvent, event_priority
from mkdocs.utils import write_file
from mkdocs_autorefs import AutorefsConfig, AutorefsPlugin

from mkdocstrings._internal.extension import MkdocstringsExtension
from mkdocstrings._internal.handlers.base import BaseHandler, Handlers
from mkdocstrings._internal.loggers import get_logger

if TYPE_CHECKING:
    from jinja2.environment import Environment
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files


_logger = get_logger("mkdocstrings")


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
    locale = opt.Optional(opt.Type(str))
    """The locale to use for translations."""


class MkdocstringsPlugin(BasePlugin[PluginConfig]):
    """An `mkdocs` plugin.

    This plugin defines the following event hooks:

    - `on_config`
    - `on_env`
    - `on_post_build`

    Check the [Developing Plugins](https://www.mkdocs.org/user-guide/plugins/#developing-plugins) page of `mkdocs`
    for more information about its plugin system.
    """

    css_filename: str = "assets/_mkdocstrings.css"
    """The path of the CSS file to write in the site directory."""

    def __init__(self) -> None:
        """Initialize the object."""
        super().__init__()
        self._handlers: Handlers | None = None

    @property
    def handlers(self) -> Handlers:
        """Get the instance of [mkdocstrings.Handlers][] for this plugin/build.

        Raises:
            RuntimeError: If the plugin hasn't been initialized with a config.

        Returns:
            An instance of [mkdocstrings.Handlers][] (the same throughout the build).
        """
        if not self._handlers:
            raise RuntimeError("The plugin hasn't been initialized with a config yet")
        return self._handlers

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig | None:
        """Instantiate our Markdown extension.

        Hook for the [`on_config` event](https://www.mkdocs.org/user-guide/plugins/#on_config).
        In this hook, we instantiate our [`MkdocstringsExtension`][mkdocstrings.MkdocstringsExtension]
        and add it to the list of Markdown extensions used by `mkdocs`.

        We pass this plugin's configuration dictionary to the extension when instantiating it (it will need it
        later when processing markdown to get handlers and their global configurations).

        Arguments:
            config: The MkDocs config object.

        Returns:
            The modified config.
        """
        if not self.plugin_enabled:
            _logger.debug("Plugin is not enabled. Skipping.")
            return config
        _logger.debug("Adding extension to the list")

        locale = self.config.locale or config.theme.get("language") or config.theme.get("locale") or "en"
        locale = str(locale).replace("_", "-")

        handlers = Handlers(
            default=self.config.default_handler,
            handlers_config=self.config.handlers,
            theme=config.theme.name or os.path.dirname(config.theme.dirs[0]),
            custom_templates=self.config.custom_templates,
            mdx=config.markdown_extensions,
            mdx_config=config.mdx_configs,
            inventory_project=config.site_name,
            inventory_version="0.0.0",  # TODO: Find a way to get actual version.
            locale=locale,
            tool_config=config,
        )

        handlers._download_inventories()

        AutorefsPlugin.record_backlinks = True
        autorefs: AutorefsPlugin
        try:
            # If autorefs plugin is explicitly enabled, just use it.
            autorefs = config.plugins["autorefs"]  # type: ignore[assignment]
            _logger.debug("Picked up existing autorefs instance %r", autorefs)
        except KeyError:
            # Otherwise, add a limited instance of it that acts only on what's added through `register_anchor`.
            autorefs = AutorefsPlugin()
            autorefs.config = AutorefsConfig()
            autorefs.scan_toc = False
            config.plugins["autorefs"] = autorefs
            _logger.debug("Added a subdued autorefs instance %r", autorefs)
        # YORE: Bump 1: Remove block.
        with catch_warnings():
            simplefilter("ignore", category=DeprecationWarning)
            autorefs.get_fallback_anchor = handlers.get_anchors

        mkdocstrings_extension = MkdocstringsExtension(handlers, autorefs)
        config.markdown_extensions.append(mkdocstrings_extension)  # type: ignore[arg-type]

        config.extra_css.insert(0, self.css_filename)  # So that it has lower priority than user files.

        self._autorefs = autorefs
        self._handlers = handlers
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

    @event_priority(50)  # Early, before autorefs' starts applying cross-refs and collecting backlinks.
    def _on_env_load_inventories(self, env: Environment, config: MkDocsConfig, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if self.plugin_enabled and self._handlers:
            register = config.plugins["autorefs"].register_url  # type: ignore[attr-defined]
            for identifier, url in self._handlers._yield_inventory_items():
                register(identifier, url)

    @event_priority(-20)  # Late, not important.
    def _on_env_add_css(self, env: Environment, config: MkDocsConfig, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if self.plugin_enabled and self._handlers:
            css_content = "\n".join(handler.extra_css for handler in self.handlers.seen_handlers)
            write_file(css_content.encode("utf-8"), os.path.join(config.site_dir, self.css_filename))

    @event_priority(-20)  # Late, not important.
    def _on_env_write_inventory(self, env: Environment, config: MkDocsConfig, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if self.plugin_enabled and self._handlers and self.inventory_enabled:
            _logger.debug("Creating inventory file objects.inv")
            inv_contents = self.handlers.inventory.format_sphinx()
            write_file(inv_contents, os.path.join(config.site_dir, "objects.inv"))

    @event_priority(-100)  # Last, after autorefs has finished applying cross-refs and collecting backlinks.
    def _on_env_apply_backlinks(self, env: Environment, /, *, config: MkDocsConfig, files: Files) -> Environment:  # noqa: ARG002
        regex = re.compile(r"<backlinks\s+identifier=\"([^\"]+)\"\s+handler=\"([^\"]+)\"\s*/?>")

        def repl(match: Match) -> str:
            handler_name = match.group(2)
            handler = self.handlers.get_handler(handler_name)

            # The handler doesn't implement backlinks,
            # return early to avoid computing them.
            if handler.render_backlinks.__func__ is BaseHandler.render_backlinks:  # type: ignore[attr-defined]
                return ""

            identifier = match.group(1)
            aliases = handler.get_aliases(identifier)
            backlinks = self._autorefs.get_backlinks(identifier, *aliases, from_url=file.page.url)  # type: ignore[union-attr]

            # No backlinks, avoid calling the handler's method.
            if not backlinks:
                return ""

            if "locale" in signature(handler.render_backlinks).parameters:
                render_backlinks = partial(handler.render_backlinks, locale=self.handlers._locale)
            else:
                render_backlinks = handler.render_backlinks  # type: ignore[assignment]

            return render_backlinks(backlinks)

        for file in files:
            if file.page and file.page.content:
                _logger.debug("Applying backlinks in page %s", file.page.file.src_path)
                file.page.content = regex.sub(repl, file.page.content)

        return env

    on_env = CombinedEvent(_on_env_load_inventories, _on_env_add_css, _on_env_write_inventory, _on_env_apply_backlinks)
    """Extra actions that need to happen after all Markdown-to-HTML page rendering.

    Hook for the [`on_env` event](https://www.mkdocs.org/user-guide/plugins/#on_env).

    - Gather results from background inventory download tasks.
    - Write mkdocstrings' extra files (CSS, inventory) into the site directory.
    - Apply backlinks to the HTML output of each page.
    """

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

        if self._handlers:
            _logger.debug("Tearing handlers down")
            self.handlers.teardown()

    def get_handler(self, handler_name: str) -> BaseHandler:
        """Get a handler by its name. See [mkdocstrings.Handlers.get_handler][].

        Arguments:
            handler_name: The name of the handler.

        Returns:
            An instance of a subclass of [`BaseHandler`][mkdocstrings.BaseHandler].
        """
        return self.handlers.get_handler(handler_name)
