"""This is the plugin module."""
from typing import Generator, Tuple

import yaml
from mkdocs.config.config_options import Type as MkType
from mkdocs.plugins import BasePlugin
from mkdocs.utils import log

from .extension import MkdocstringsExtension

# TODO: make this configurable
DEFAULT_HANDLER = "python"

SELECTION_OPTS_KEY = "selection"
RENDERING_OPTS_KEY = "rendering"
"""This is the name of the rendering parameter."""


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

    def on_serve(self, server, config, **kwargs):
        """On serve hook."""
        builder = list(server.watcher._tasks.values())[0]["func"]
        for element in self.config["watch"]:
            log.info(f"mkdocstrings: Adding directory '{element}' to watcher")
            server.watch(element, builder)
        return server

    def on_config(self, config, **kwargs):
        """On config hook."""
        self.mkdocstrings_extension = MkdocstringsExtension(plugin_config=self.config)
        config["markdown_extensions"].append(self.mkdocstrings_extension)
        return config


def get_instructions(markdown: str) -> Generator[Tuple[str, dict], Tuple[str, dict], Tuple[str, dict]]:
    """
    Read autodoc instructions.

    Parameters:
        markdown: The text to read instructions from.

    Yields:
        Tuples of identifier with their configuration.

    Returns:
        A generator.
    """
    lines = markdown.split("\n")

    in_code_block = False

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("```"):
            in_code_block = not in_code_block

        elif line.startswith("::: ") and not in_code_block:
            identifier = line.replace("::: ", "")
            config_lines = []

            i += 1
            while i < len(lines) and lines[i].startswith("    "):
                config_lines.append(lines[i])
                i += 1

            config = yaml.safe_load("\n".join(config_lines)) or {}
            yield identifier, config

        i += 1
