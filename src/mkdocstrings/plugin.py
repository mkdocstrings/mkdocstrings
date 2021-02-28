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

import os
from typing import Callable, Optional, Tuple

from livereload import Server
from mkdocs.config import Config
from mkdocs.config.config_options import Type as MkType
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


class MkdocstringsPlugin(BasePlugin):
    """An `mkdocs` plugin.

    This plugin defines the following event hooks:

    - `on_config`
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

    def on_serve(self, server: Server, builder: Callable = None, **kwargs) -> Server:  # noqa: W0613 (unused arguments)
        """Watch directories.

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
        """Instantiate our Markdown extension.

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
        self._handlers = Handlers(extension_config)

        try:
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
        autorefs.get_fallback_anchor = self._handlers.get_anchor

        mkdocstrings_extension = MkdocstringsExtension(extension_config, self._handlers, autorefs)
        config["markdown_extensions"].append(mkdocstrings_extension)

        config["extra_css"].insert(0, self.css_filename)  # So that it has lower priority than user files.

        return config

    def on_post_build(self, config: Config, **kwargs) -> None:  # noqa: W0613,R0201 (unused arguments, cannot be static)
        """Teardown the handlers.

        Hook for the [`on_post_build` event](https://www.mkdocs.org/user-guide/plugins/#on_post_build).
        This hook is used to teardown all the handlers that were instantiated and cached during documentation buildup.

        For example, the [Python handler's collector][mkdocstrings.handlers.python.PythonCollector] opens a subprocess
        in the background and keeps it open to feed it the "autodoc" instructions and get back JSON data. Therefore,
        it must close it at some point, and it does it in its
        [`teardown()` method][mkdocstrings.handlers.python.PythonCollector.teardown] which is indirectly called by
        this hook.

        Arguments:
            config: The MkDocs config object.
            kwargs: Additional arguments passed by MkDocs.
        """
        if self._handlers:
            css_content = "\n".join(handler.renderer.extra_css for handler in self.handlers.seen_handlers)
            write_file(css_content.encode("utf-8"), os.path.join(config["site_dir"], self.css_filename))

            log.debug("Tearing handlers down")
            self._handlers.teardown()

    def get_handler(self, handler_name: str) -> BaseHandler:
        """Get a handler by its name. See [mkdocstrings.handlers.base.Handlers.get_handler][].

        Arguments:
            handler_name: The name of the handler.

        Returns:
            An instance of a subclass of [`BaseHandler`][mkdocstrings.handlers.base.BaseHandler].
        """
        return self.handlers.get_handler(handler_name)
