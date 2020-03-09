from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from mkdocs.config.config_options import Type as MkType
from mkdocs.plugins import BasePlugin
from mkdocs.utils import log

from .extension import MkdocstringsExtension
from .handlers import get_handler

# TODO: make this configurable
DEFAULT_HANDLER = "python"


class MkdocstringsPlugin(BasePlugin):
    config_scheme = (
        ("global_filters", MkType(list, default=["!^_[^_]", "!^__weakref__$"])),
        ("watch", MkType(list, default=[])),
    )

    def __init__(self, *args, **kwargs) -> None:
        super(MkdocstringsPlugin, self).__init__()
        self.mkdocstrings_extension = None
        self.env = None

    def on_serve(self, server, config, **kwargs):
        builder = list(server.watcher._tasks.values())[0]["func"]
        for element in self.config["watch"]:
            log.info(f"mkdocstrings: Adding directory '{element}' to watcher")
            server.watch(element, builder)
        return server

    def on_config(self, config, **kwargs):
        self.env = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"))
        self.mkdocstrings_extension = MkdocstringsExtension()
        config["markdown_extensions"].append(self.mkdocstrings_extension)
        return config

    def on_nav(self, nav, **kwargs):
        instructions_by_handler = {}

        for page in nav.pages:
            with open(page.file.abs_src_path, "r") as file:
                dispatch(instructions_by_handler, get_instructions(file.read()))

        for handler_name, instructions in instructions_by_handler.items():
            handler = get_handler(handler_name)
            selection = for_collection(instructions)
            rendering = for_rendering(instructions)
            collected = handler.get_collection(selection)
            for selection_hash, (identifier, item) in collected.items():
                self.mkdocstrings_extension.store(
                    selection_hash, item, handler.renderer_class(env=self.env, config=rendering[identifier])
                )

        return nav


def for_collection(instructions):
    return {identifier: config.get("collector", {}) for identifier, config in instructions}


def for_rendering(instructions):
    return {identifier: config.get("renderer", {}) for identifier, config in instructions}


def dispatch(by_handler, instructions):
    for instruction in instructions:
        handler = instruction[1].get("handler", DEFAULT_HANDLER)
        if handler not in by_handler:
            by_handler[handler] = []
        by_handler[handler].append(instruction)


def get_instructions(markdown):
    lines = markdown.split("\n")

    instructions = []
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
            instructions.append((identifier, config))

        i += 1

    return instructions
