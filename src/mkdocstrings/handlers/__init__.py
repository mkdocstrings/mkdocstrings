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
from typing import Sequence, Type

from jinja2 import Environment, FileSystemLoader
from jinja2.filters import do_mark_safe
from markdown import Markdown
from mkdocs.utils import log
from pymdownx.highlight import Highlight

HANDLERS_CACHE = {}


DataType = Type["T"]


class CollectionError(Exception):
    """An exception raised when some collection of data failed."""


class ThemeNotSupported(Exception):
    """An exception raised to tell a theme is not supported."""


def do_highlight(
    src: str,
    guess_lang: bool = False,
    language: str = None,
    inline: bool = False,
    dedent: bool = True,
    line_nums: bool = False,
    line_start: int = 1,
) -> str:
    """
    A code-snippet highlighting function for Jinja templates.

    Args:
        src: The code to highlight.
        guess_lang: Whether to guess the language or not.
        language: Explicitly tell what language to use for highlighting.
        inline: Whether to do inline highlighting.
        dedent: Whether to dedent the code before highlighting it or not.
        line_nums: Whether to add line numbers in the result.
        line_start: The line number to start with.

    Returns:
        The highlighted code as HTML text, marked safe (not escaped for HTML).
    """
    if dedent:
        src = textwrap.dedent(src)

    highlighter = Highlight(use_pygments=True, guess_lang=guess_lang, linenums=line_nums)
    result = highlighter.highlight(src=src, language=language, linestart=line_start, inline=inline)

    if inline:
        return do_mark_safe(result.text)
    return do_mark_safe(result)


def do_any(seq: Sequence, attribute: str = None) -> bool:
    """
    The `any` builtin as a filter for Jinja templates.

    Args:
        seq: An iterable object.
        attribute: The attribute name to use on each object of the iterable.

    Returns:
        A boolean telling if any object of the iterable evaluated to True.
    """
    if attribute is None:
        return any(seq)
    return any(o[attribute] for o in seq)


class BaseRenderer:
    """
    The base renderer class.

    Inherit from this class to implement a renderer.

    You will have to implement the `render` method.
    You can also override the `update_env` method, to add more filters to the Jinja environment,
    making them available in your Jinja templates.

    To define a fallback theme, add a `FALLBACK_THEME` class-variable.
    """

    def __init__(self, directory: str, theme: str) -> None:
        """
        Initialization method.

        If the given theme is not supported (it does not exist), it will look for a `FALLBACK_THEME` attribute
        in `self` to use as a fallback theme.

        Arguments:
            directory: The name of the directory containing the themes for this renderer.
            theme: The name of theme to use.
        """
        themes_dir = Path(__file__).parent.parent / "templates" / directory
        theme_dir = themes_dir / theme
        if not theme_dir.exists():
            if hasattr(self, "FALLBACK_THEME"):
                log.warning(
                    f"mkdocstrings.handlers: No '{theme}' theme in '{directory}', "
                    f"falling back to theme '{self.FALLBACK_THEME}'"
                )
                theme_dir = themes_dir / self.FALLBACK_THEME
            else:
                raise ThemeNotSupported(theme)

        self.env = Environment(autoescape=True, loader=FileSystemLoader(theme_dir))
        self.env.filters["highlight"] = do_highlight
        self.env.filters["any"] = do_any

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

    def update_env(self, md: Markdown, config: dict) -> None:
        """
        Update the Jinja environment.

        Arguments:
            md: The Markdown instance. Useful to add functions able to convert Markdown into the environment filters.
            config: Configuration options for `mkdocs` and `mkdocstrings`, read from `mkdocs.yml`. See the source code
              of [mkdocstrings.plugin.MkdocstringsPlugin.on_config][] to see what's in this dictionary.
        """
        md = Markdown(extensions=config["mdx"], extensions_configs=config["mdx_configs"])

        def convert_markdown(text):
            return do_mark_safe(md.convert(text))

        self.env.filters["convert_markdown"] = convert_markdown


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
            Anything you want, as long as you can feed it to the renderer's `render` method.
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

    def __init__(self, collector: BaseCollector, renderer: BaseRenderer) -> None:
        """
        Initialization method.

        Arguments:
            collector: A collector instance.
            renderer: A renderer instance.
        """
        self.collector = collector
        self.renderer = renderer


def get_handler(name: str, theme: str) -> BaseHandler:
    """
    Get a handler thanks to its name.

    This function dynamically import a module named "mkdocstrings.handlers.NAME", calls its
    `get_handler` method to get an instance of a handler, and caches it in dictionary.
    It means that during one run (for each reload when serving, or once when building),
    a handler is instantiated only once, and reused for each "autodoc" instruction asking for it.

    Args:
        name: The name of the handler. Really, it's the name of the Python module holding it.
        theme: The name of the theme to use.

    Returns:
        An instance of a subclass of [`BaseHandler`][mkdocstrings.handlers.BaseHandler],
        as instantiated by the `get_handler` method of the handler's module.
    """
    if name not in HANDLERS_CACHE:
        module = importlib.import_module(f"mkdocstrings.handlers.{name}")
        HANDLERS_CACHE[name] = module.get_handler(theme)
    return HANDLERS_CACHE[name]


def teardown() -> None:
    """Teardown all cached handlers and clear the cache."""
    for handler in HANDLERS_CACHE.values():
        handler.collector.teardown()
        del handler.collector
        del handler.renderer
        del handler
    HANDLERS_CACHE.clear()
