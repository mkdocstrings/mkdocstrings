import importlib
import json


class BaseRenderer:
    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def render(self, data):
        raise NotImplementedError


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
