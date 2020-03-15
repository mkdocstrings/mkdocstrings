from pathlib import Path

import yaml
from mkdocs.config.config_options import Type as MkType
from mkdocs.plugins import BasePlugin
from mkdocs.utils import log

from .extension import MkdocstringsExtension

# TODO: make this configurable
DEFAULT_HANDLER = "python"

SELECTION_OPTS_KEY = "selection"
RENDERING_OPTS_KEY = "rendering"


class MkdocstringsPlugin(BasePlugin):
    config_scheme = (
        ("watch", MkType(list, default=[])),
        ("handlers", MkType(dict, default={})),
        ("default_handler", MkType(str, default="python")),
    )

    def __init__(self, *args, **kwargs) -> None:
        super(MkdocstringsPlugin, self).__init__()
        self.mkdocstrings_extension = None

    def on_serve(self, server, config, **kwargs):
        builder = list(server.watcher._tasks.values())[0]["func"]
        for element in self.config["watch"]:
            log.info(f"mkdocstrings: Adding directory '{element}' to watcher")
            server.watch(element, builder)
        return server

    def on_config(self, config, **kwargs):
        self.mkdocstrings_extension = MkdocstringsExtension(plugin_config=self.config)
        config["markdown_extensions"].append(self.mkdocstrings_extension)
        return config

    # TODO: update the un-rendered links using references collected in the extension
    # how to remember the page URL associated to an identifier?

    # TODO: run collectors teardown methods at the very end


def get_instructions(markdown):
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
