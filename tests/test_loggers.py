"""Tests for the loggers module."""

from unittest.mock import MagicMock

import pytest

from mkdocstrings import get_logger, get_template_logger


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"once": False},
        {"once": True},
    ],
)
def test_logger(kwargs: dict, caplog: pytest.LogCaptureFixture) -> None:
    """Test logger methods.

    Parameters:
        kwargs: Keyword arguments passed to the logger methods.
    """
    logger = get_logger("mkdocstrings.test")
    caplog.set_level(0)
    for _ in range(2):
        logger.debug("Debug message", **kwargs)
        logger.info("Info message", **kwargs)
        logger.warning("Warning message", **kwargs)
        logger.error("Error message", **kwargs)
        logger.critical("Critical message", **kwargs)
    if kwargs.get("once", False):
        assert len(caplog.records) == 5
    else:
        assert len(caplog.records) == 10


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"once": False},
        {"once": True},
    ],
)
def test_template_logger(kwargs: dict, caplog: pytest.LogCaptureFixture) -> None:
    """Test template logger methods.

    Parameters:
        kwargs: Keyword arguments passed to the template logger methods.
    """
    logger = get_template_logger()
    mock = MagicMock()
    caplog.set_level(0)
    for _ in range(2):
        logger.debug(mock, "Debug message", **kwargs)
        logger.info(mock, "Info message", **kwargs)
        logger.warning(mock, "Warning message", **kwargs)
        logger.error(mock, "Error message", **kwargs)
        logger.critical(mock, "Critical message", **kwargs)
    if kwargs.get("once", False):
        assert len(caplog.records) == 5
    else:
        assert len(caplog.records) == 10
