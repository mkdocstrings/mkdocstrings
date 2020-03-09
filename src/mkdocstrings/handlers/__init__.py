import importlib
import json

from markdown import Markdown


class BaseRenderer:
    DEFAULT_CONFIG = {}

    def __init__(self, env, config):
        self.env = env
        self.theme = "material"
        self.config = self.DEFAULT_CONFIG
        self.config.update(config)

    def render(self, data):
        raise NotImplementedError

    def update_env(self, md):
        md = Markdown(extensions=md.registeredExtensions)

        def convert_markdown(text):
            return md.convert(text)

        self.env.filters["convert_markdown"] = convert_markdown


class BaseHandler:
    def __init__(self, renderer_class):
        self.renderer_class = renderer_class

    def get_collection(self, selection):
        collected = self.collect(selection)
        return {
            hash(json.dumps({identifier: config}, sort_keys=True)): (identifier, collected[identifier])
            for identifier, config in selection.items()
        }

    def collect(self, selection):
        raise NotImplementedError


def get_handler(name):
    module = importlib.import_module(f"mkdocstrings.handlers.{name}")
    return module.handler
