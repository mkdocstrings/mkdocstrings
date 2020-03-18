import importlib
import textwrap
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from markdown import Markdown
from pymdownx.highlight import Highlight

HANDLERS_CACHE = {}


class CollectionError(Exception):
    pass


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

        def highlight(src, guess_lang=False, language=None, inline=False, linenums=False, linestart=1):
            result = Highlight(use_pygments=False, guess_lang=guess_lang, linenums=linenums).highlight(
                src=textwrap.dedent(textwrap.indent("".join(src), "    ")),
                language=language,
                linestart=linestart,
                inline=inline,
            )
            if inline:
                return result.text
                # placeholder = md.htmlStash.store(result.text)
                # return placeholder
            return result
            # return md.htmlStash.store(result)

        def any_plus(seq, attribute=None):
            if attribute is None:
                return any(seq)
            return any(o[attribute] for o in seq)

        self.env.filters["convert_markdown"] = convert_markdown
        self.env.filters["highlight"] = highlight
        self.env.filters["any"] = any_plus


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


def teardown():
    for handler in HANDLERS_CACHE.values():
        handler.collector.teardown()
        del handler.collector
        del handler.renderer
        del handler
    HANDLERS_CACHE.clear()
