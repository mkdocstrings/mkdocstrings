import importlib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from markdown import Markdown


HANDLERS_CACHE = {}


class BaseRenderer:
    DEFAULT_RENDERING_OPTS = {}

    def __init__(self, directory, theme):
        self.env = Environment(loader=FileSystemLoader(Path(__file__).parent.parent / "templates" / directory / theme))

    def render(self, data, config):
        raise NotImplementedError

    def update_env(self, md):
        md = Markdown(extensions=md.registeredExtensions)

        def convert_markdown(text):
            return md.convert(text)

        self.env.filters["convert_markdown"] = convert_markdown


class BaseCollector:
    DEFAULT_SELECTION_OPTS = {}

    def collect(self, identifier, config):
        raise NotImplementedError

    def teardown(self):
        pass


class BaseHandler:
    def __init__(self, collector, renderer):
        self.collector = collector
        self.renderer = renderer


def get_handler(name):
    if name not in HANDLERS_CACHE:
        module = importlib.import_module(f"mkdocstrings.handlers.{name}")
        HANDLERS_CACHE[name] = module.get_handler()
    return HANDLERS_CACHE[name]
