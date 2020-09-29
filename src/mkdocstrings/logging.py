"""Utility functions."""

import logging

from mkdocs.utils import warning_filter


class LoggerAdapter(logging.LoggerAdapter):
    """A logger adapter to prefix messages."""

    def __init__(self, prefix, logger):
        """
        Initialize the object.

        Arguments:
            prefix: The string to insert in front of every message.
            logger: The logger instance.
        """
        super().__init__(logger, {})
        self.prefix = prefix

    def process(self, msg, kwargs):
        """
        Process the message.

        Arguments:
            msg: The message:
            kwargs: Remaining arguments.

        Returns:
            The processed message.
        """
        return f"{self.prefix}: {msg}", kwargs


def get_logger(name):
    """
    Return a pre-configured logger.

    Arguments:
        name: The name to use with `logging.getLogger`.

    Returns:
        A logger configured to work well in MkDocs.
    """
    logger = logging.getLogger(f"mkdocs.plugins.{name}")
    logger.addFilter(warning_filter)
    return LoggerAdapter(name, logger)
