# SPDX-License-Identifier: ISC
#
# ISC License
#
# Copyright (c) 2019, Timothée Mazzucotelli and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

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
