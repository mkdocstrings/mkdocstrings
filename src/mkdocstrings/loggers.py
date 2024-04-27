"""Logging functions."""

from __future__ import annotations

import logging
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, MutableMapping, Sequence

try:
    from jinja2 import pass_context
except ImportError:  # TODO: remove once Jinja2 < 3.1 is dropped
    from jinja2 import contextfunction as pass_context  # type: ignore[attr-defined,no-redef]

try:
    import mkdocstrings_handlers
except ImportError:
    TEMPLATES_DIRS: Sequence[Path] = ()
else:
    TEMPLATES_DIRS = tuple(mkdocstrings_handlers.__path__)


if TYPE_CHECKING:
    from jinja2.runtime import Context


class LoggerAdapter(logging.LoggerAdapter):
    """A logger adapter to prefix messages.

    This adapter also adds an additional parameter to logging methods
    called `once`: if `True`, the message will only be logged once.

    Examples:
        In Python code:

        >>> logger = get_logger("myplugin")
        >>> logger.debug("This is a debug message.")
        >>> logger.info("This is an info message.", once=True)

        In Jinja templates (logger available in context as `log`):

        ```jinja
        {{ log.debug("This is a debug message.") }}
        {{ log.info("This is an info message.", once=True) }}
        ```
    """

    def __init__(self, prefix: str, logger: logging.Logger):
        """Initialize the object.

        Arguments:
            prefix: The string to insert in front of every message.
            logger: The logger instance.
        """
        super().__init__(logger, {})
        self.prefix = prefix
        self._logged: set[tuple[LoggerAdapter, str]] = set()

    def process(self, msg: str, kwargs: MutableMapping[str, Any]) -> tuple[str, Any]:
        """Process the message.

        Arguments:
            msg: The message:
            kwargs: Remaining arguments.

        Returns:
            The processed message.
        """
        return f"{self.prefix}: {msg}", kwargs

    def log(self, level: int, msg: object, *args: object, **kwargs: object) -> None:
        """Log a message.

        Arguments:
            level: The logging level.
            msg: The message.
            *args: Additional arguments passed to parent method.
            **kwargs: Additional keyword arguments passed to parent method.
        """
        if kwargs.pop("once", False):
            if (key := (self, str(msg))) in self._logged:
                return
            self._logged.add(key)
        super().log(level, msg, *args, **kwargs)  # type: ignore[arg-type]


class TemplateLogger:
    """A wrapper class to allow logging in templates.

    The logging methods provided by this class all accept
    two parameters:

    - `msg`: The message to log.
    - `once`: If `True`, the message will only be logged once.

    Methods:
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

    @pass_context
    def wrapper(context: Context, msg: str | None = None, **kwargs: Any) -> str:
        """Log a message.

        Arguments:
            context: The template context, automatically provided by Jinja.
            msg: The message to log.
            **kwargs: Additional arguments passed to the logger function.

        Returns:
            An empty string.
        """
        template_path = get_template_path(context)
        logger_func(f"{template_path}: {msg or 'Rendering'}", **kwargs)
        return ""

    return wrapper


def get_template_path(context: Context) -> str:
    """Return the path to the template currently using the given context.

    Arguments:
        context: The template context.

    Returns:
        The relative path to the template.
    """
    context_name: str = str(context.name)
    filename = context.environment.get_template(context_name).filename
    if filename:
        for template_dir in TEMPLATES_DIRS:
            with suppress(ValueError):
                return str(Path(filename).relative_to(template_dir))
        with suppress(ValueError):
            return str(Path(filename).relative_to(Path.cwd()))
        return filename
    return context_name


def get_logger(name: str) -> LoggerAdapter:
    """Return a pre-configured logger.

    Arguments:
        name: The name to use with `logging.getLogger`.

    Returns:
        A logger configured to work well in MkDocs.
    """
    logger = logging.getLogger(f"mkdocs.plugins.{name}")
    return LoggerAdapter(name.split(".", 1)[0], logger)


def get_template_logger(handler_name: str | None = None) -> TemplateLogger:
    """Return a logger usable in templates.

    Parameters:
        handler_name: The name of the handler.

    Returns:
        A template logger.
    """
    handler_name = handler_name or "base"
    return TemplateLogger(get_logger(f"mkdocstrings_handlers.{handler_name}.templates"))
