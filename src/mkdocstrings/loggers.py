"""Logging functions."""

import logging
from pathlib import Path
from typing import Any, Callable, Optional, Tuple

from jinja2 import contextfunction
from jinja2.runtime import Context
from mkdocs.utils import warning_filter

TEMPLATES_DIR = Path(__file__).parent / "templates"


class LoggerAdapter(logging.LoggerAdapter):
    """A logger adapter to prefix messages."""

    def __init__(self, prefix: str, logger):
        """Initialize the object.

        Arguments:
            prefix: The string to insert in front of every message.
            logger: The logger instance.
        """
        super().__init__(logger, {})
        self.prefix = prefix

    def process(self, msg: str, kwargs) -> Tuple[str, Any]:
        """Process the message.

        Arguments:
            msg: The message:
            kwargs: Remaining arguments.

        Returns:
            The processed message.
        """
        return f"{self.prefix}: {msg}", kwargs


class TemplateLogger:
    """A wrapper class to allow logging in templates.

    Attributes:
        debug: Function to log a DEBUG message.
        info: Function to log an INFO message.
        warning: Function to log a WARNING message.
        error: Function to log an ERROR message.
        critical: Function to log a CRITICAL message.
    """

    def __init__(self, logger: LoggerAdapter):
        """Initialize the object.

        Arguments:
            logger: A logger adapter.
        """
        self.debug = get_template_logger_function(logger.debug)
        self.info = get_template_logger_function(logger.info)
        self.warning = get_template_logger_function(logger.warning)
        self.error = get_template_logger_function(logger.error)
        self.critical = get_template_logger_function(logger.critical)


def get_template_logger_function(logger_func: Callable) -> Callable:
    """Create a wrapper function that automatically receives the Jinja template context.

    Arguments:
        logger_func: The logger function to use within the wrapper.

    Returns:
        A function.
    """

    @contextfunction
    def wrapper(context: Context, msg: Optional[str] = None) -> str:
        """Log a message.

        Arguments:
            context: The template context, automatically provided by Jinja.
            msg: The message to log.

        Returns:
            An empty string.
        """
        template_path = get_template_path(context)
        logger_func(f"{template_path}: {msg or 'Rendering'}")
        return ""

    return wrapper


def get_template_path(context: Context) -> str:
    """Return the path to the template currently using the given context.

    Arguments:
        context: The template context.

    Returns:
        The relative path to the template.
    """
    filename = context.environment.get_template(context.name).filename
    if filename:
        try:
            return str(Path(filename).relative_to(TEMPLATES_DIR))
        except ValueError:
            return filename
    return context.name


def get_logger(name: str) -> LoggerAdapter:
    """Return a pre-configured logger.

    Arguments:
        name: The name to use with `logging.getLogger`.

    Returns:
        A logger configured to work well in MkDocs.
    """
    logger = logging.getLogger(f"mkdocs.plugins.{name}")
    logger.addFilter(warning_filter)
    return LoggerAdapter(name, logger)


def get_template_logger() -> TemplateLogger:
    """Return a logger usable in templates.

    Returns:
        A template logger.
    """
    return TemplateLogger(get_logger("mkdocstrings.templates"))
