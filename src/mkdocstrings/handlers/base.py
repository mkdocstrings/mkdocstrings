"""
Base module for handlers.

This module contains the base classes for implementing collectors, renderers, and the combination of the two: handlers.

It also provides two methods:

- `get_handler`, that will cache handlers into the `HANDLERS_CACHE` dictionary.
- `teardown`, that will teardown all the cached handlers, and then clear the cache.
"""

import importlib
import textwrap
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from jinja2 import Environment, FileSystemLoader
from jinja2.filters import do_mark_safe
from markdown import Markdown
from pymdownx.highlight import Highlight

from mkdocstrings.loggers import get_template_logger

handlers_cache: Dict[str, Any] = {}


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
    Highlight a code-snippet.

    This function is used as a filter in Jinja templates.

    Arguments:
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
    Check if at least one of the item in the sequence evaluates to true.

    The `any` builtin as a filter for Jinja templates.

    Arguments:
        seq: An iterable object.
        attribute: The attribute name to use on each object of the iterable.

    Returns:
        A boolean telling if any object of the iterable evaluated to True.
    """
    if attribute is None:
        return any(seq)
    return any(_[attribute] for _ in seq)


class BaseRenderer(ABC):
    """
    The base renderer class.

    Inherit from this class to implement a renderer.

    You will have to implement the `render` method.
    You can also override the `update_env` method, to add more filters to the Jinja environment,
    making them available in your Jinja templates.

    To define a fallback theme, add a `FALLBACK_THEME` class-variable.
    """

    fallback_theme: str = ""

    def __init__(self, directory: str, theme: str, custom_templates: Optional[str] = None) -> None:
        """
        Initialize the object.

        If the given theme is not supported (it does not exist), it will look for a `fallback_theme` attribute
        in `self` to use as a fallback theme.

        Arguments:
            directory: The name of the directory containing the themes for this renderer.
            theme: The name of theme to use.
            custom_templates: Directory containing custom templates.
        """
        paths = []

        if custom_templates is not None:
            paths.append(Path(custom_templates) / directory / theme)

        themes_dir = Path(__file__).parent.parent / "templates" / directory

        paths.append(themes_dir / theme)

        if self.fallback_theme != "":
            paths.append(themes_dir / self.fallback_theme)

        self.env = Environment(autoescape=True, loader=FileSystemLoader(paths))  # type: ignore
        self.env.filters["highlight"] = do_highlight
        self.env.filters["any"] = do_any
        self.env.globals["log"] = get_template_logger()

    @abstractmethod
    def render(self, data: Any, config: dict) -> str:
        """
        Render a template using provided data and configuration options.

        Arguments:
            data: The collected data to render.
            config: The rendering options.

        Returns:
            The rendered template as HTML.
        """  # noqa: DAR202 (excess return section)

    def update_env(self, md: Markdown, config: dict) -> None:
        """
        Update the Jinja environment.

        Arguments:
            md: The Markdown instance. Useful to add functions able to convert Markdown into the environment filters.
            config: Configuration options for `mkdocs` and `mkdocstrings`, read from `mkdocs.yml`. See the source code
                of [mkdocstrings.plugin.MkdocstringsPlugin.on_config][] to see what's in this dictionary.
        """
        # Re-instantiate md: see https://github.com/tomchristie/mkautodoc/issues/14
        md = Markdown(extensions=config["mdx"], extensions_configs=config["mdx_configs"])
        self.env.filters["convert_markdown"] = lambda text: do_mark_safe(md.convert(text))


class BaseCollector(ABC):
    """
    The base collector class.

    Inherit from this class to implement a collector.

    You will have to implement the `collect` method.
    You can also implement the `teardown` method.
    """

    @abstractmethod
    def collect(self, identifier: str, config: dict) -> Any:
        """
        Collect data given an identifier and selection configuration.

        In the implementation, you typically call a subprocess that returns JSON, and load that JSON again into
        a Python dictionary for example, though the implementation is completely free.

        Arguments:
            identifier: An identifier for which to collect data. For example, in Python,
                it would be 'mkdocstrings.handlers' to collect documentation about the handlers module.
                It can be anything that you can feed to the tool of your choice.
            config: Configuration options for the tool you use to collect data. Typically called "selection" because
                these options modify how the objects or documentation are "selected" in the source code.

        Returns:
            Anything you want, as long as you can feed it to the renderer's `render` method.
        """  # noqa: DAR202 (excess return section)

    def teardown(self) -> None:
        """
        Teardown the collector.

        This method should be implemented to, for example, terminate a subprocess
        that was started when creating the collector instance.
        """


class BaseHandler:
    """
    The base handler class.

    Inherit from this class to implement a handler.

    It's usually just a combination of a collector and a renderer, but you can make it as complex as you need.
    """

    def __init__(self, collector: BaseCollector, renderer: BaseRenderer) -> None:
        """
        Initialize the object.

        Arguments:
            collector: A collector instance.
            renderer: A renderer instance.
        """
        self.collector = collector
        self.renderer = renderer


def get_handler(
    name: str,
    theme: str,
    custom_templates: Optional[str] = None,
    **config: Any,
) -> BaseHandler:
    """
    Get a handler thanks to its name.

    This function dynamically imports a module named "mkdocstrings.handlers.NAME", calls its
    `get_handler` method to get an instance of a handler, and caches it in dictionary.
    It means that during one run (for each reload when serving, or once when building),
    a handler is instantiated only once, and reused for each "autodoc" instruction asking for it.

    Arguments:
        name: The name of the handler. Really, it's the name of the Python module holding it.
        theme: The name of the theme to use.
        custom_templates: Directory containing custom templates.
        config: Configuration passed to the handler.

    Returns:
        An instance of a subclass of [`BaseHandler`][mkdocstrings.handlers.base.BaseHandler],
        as instantiated by the `get_handler` method of the handler's module.
    """
    if name not in handlers_cache:
        module = importlib.import_module(f"mkdocstrings.handlers.{name}")
        handlers_cache[name] = module.get_handler(theme, custom_templates, **config)  # type: ignore
    return handlers_cache[name]


def teardown() -> None:
    """Teardown all cached handlers and clear the cache."""
    for handler in handlers_cache.values():
        handler.collector.teardown()
    handlers_cache.clear()
