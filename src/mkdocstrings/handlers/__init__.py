"""
Base module for handlers.

This module contains the base classes for implementing collectors, renderers, and the combination of the two: handlers.

It also provides two methods:

- `get_handler`, that will cache handlers into the `HANDLERS_CACHE` dictionary.
- `teardown`, that will teardown all the cached handlers, and then clear the cache.
"""

import importlib
import textwrap
from pathlib import Path
from typing import Type

from jinja2 import Environment, FileSystemLoader
from jinja2.filters import do_mark_safe
from markdown import Markdown
from pymdownx.highlight import Highlight

HANDLERS_CACHE = {}


DataType = Type["T"]


class CollectionError(Exception):
    """An exception raised when some collection of data failed."""


class BaseRenderer:
    """
    The base renderer class.

    Inherit from this class to implement a renderer.

    You will have to implement the `render` method.
    You can also override the `update_env` method, to add more filters to the Jinja environment,
    making them available in your Jinja templates.
    """

    def __init__(self, directory: str, theme: str) -> None:
        """
        Initialization method.

        Arguments:
            directory: The name of the directory containing the themes for this renderer.
            theme: The name of theme to use.
        """
        self.env = Environment(
            autoescape=True, loader=FileSystemLoader(Path(__file__).parent.parent / "templates" / directory / theme)
        )

    def render(self, data: DataType, config: dict) -> str:
        """
        Render a template using provided data and configuration options.

        Arguments:
            data: The collected data to render.
            config: The rendering options.

        Returns:
            The renderer template as HTML.
        """
        raise NotImplementedError

    def update_env(self, md: Markdown) -> None:
        """
        Update the Jinja environment.

        Arguments:
            md: The Markdown instance. Useful to add functions able to convert Markdown into the environment filters.
        """
        # FIXME: see https://github.com/tomchristie/mkautodoc/issues/14
        md = Markdown(extensions=md.registeredExtensions)

        def convert_markdown(text):
            return do_mark_safe(md.convert(text))

        def highlight(src, guess_lang=False, language=None, inline=False, linenums=False, linestart=1):
            result = Highlight(use_pygments=True, guess_lang=guess_lang, linenums=linenums).highlight(
                src=textwrap.dedent(textwrap.indent("".join(src), "    ")),
                language=language,
                linestart=linestart,
                inline=inline,
            )
            if inline:
                return do_mark_safe(result.text)
            return do_mark_safe(result)

        def any_plus(seq, attribute=None):
            if attribute is None:
                return any(seq)
            return any(o[attribute] for o in seq)

        self.env.filters["convert_markdown"] = convert_markdown
        self.env.filters["highlight"] = highlight
        self.env.filters["any"] = any_plus


class BaseCollector:
    """
    The base collector class.

    Inherit from this class to implement a collector.

    You will have to implement the `collect` method.
    You can also implement the `teardown` method.
    """

    def collect(self, identifier: str, config: dict) -> DataType:
        """
        Collect data given an identifier and selection configuration.

        In the implementation, you typically call a subprocess that returns JSON, and load that JSON again into
        a Python dictionary for example, though the implementation is completely free.

        Args:
            identifier: An identifier for which to collect data. For example, in Python,
              it would be 'mkdocstrings.handlers' to collect documentation about the handlers module.
              It can be anything that you can feed to the tool of your choice.
            config: Configuration options for the tool you use to collect data. Typically called "selection" because
              these options modify how the objects or documentation are "selected" in the source code.

        Returns:
            Anything you want, as long as you can feed it to the renderer `render` method.
        """
        raise NotImplementedError

    def teardown(self) -> None:
        """Placeholder to remember this method can be implemented."""


class BaseHandler:
    """
    The base handler class.

    Inherit from this class to implement a handler.

    It's usually just a combination of a collector and a renderer, but you can make it as complex as you need.
    """

    def __init__(self, collector, renderer):
        """
        Initialization method.

        Arguments:
            collector: A collector instance.
            renderer: A renderer instance.
        """
        self.collector = collector
        self.renderer = renderer


def get_handler(name) -> BaseHandler:
    if name not in HANDLERS_CACHE:
        module = importlib.import_module(f"mkdocstrings.handlers.{name}")
        HANDLERS_CACHE[name] = module.get_handler()
    return HANDLERS_CACHE[name]


def teardown() -> None:
    """Teardown all cached handlers."""
    for handler in HANDLERS_CACHE.values():
        handler.collector.teardown()
        del handler.collector
        del handler.renderer
        del handler
    HANDLERS_CACHE.clear()
