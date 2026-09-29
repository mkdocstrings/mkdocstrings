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

"""mkdocstrings package.

Automatic documentation from sources, for MkDocs.
"""

from __future__ import annotations

from mkdocstrings._internal.extension import AutoDocProcessor, MkdocstringsExtension, makeExtension
from mkdocstrings._internal.handlers.base import (
    BaseHandler,
    CollectionError,
    CollectorItem,
    HandlerConfig,
    HandlerOptions,
    Handlers,
    ThemeNotSupported,
    do_any,
)
from mkdocstrings._internal.handlers.rendering import (
    HeadingShiftingTreeprocessor,
    Highlighter,
    IdPrependingTreeprocessor,
    MkdocstringsInnerExtension,
    ParagraphStrippingTreeprocessor,
)
from mkdocstrings._internal.inventory import Inventory, InventoryItem
from mkdocstrings._internal.loggers import (
    TEMPLATES_DIRS,
    LoggerAdapter,
    TemplateLogger,
    get_logger,
    get_template_logger,
    get_template_logger_function,
    get_template_path,
)
from mkdocstrings._internal.plugin import MkdocstringsPlugin, PluginConfig

__all__: list[str] = [
    "TEMPLATES_DIRS",
    "AutoDocProcessor",
    "BaseHandler",
    "CollectionError",
    "CollectorItem",
    "HandlerConfig",
    "HandlerOptions",
    "Handlers",
    "HeadingShiftingTreeprocessor",
    "Highlighter",
    "IdPrependingTreeprocessor",
    "Inventory",
    "InventoryItem",
    "LoggerAdapter",
    "MkdocstringsExtension",
    "MkdocstringsInnerExtension",
    "MkdocstringsPlugin",
    "ParagraphStrippingTreeprocessor",
    "PluginConfig",
    "TemplateLogger",
    "ThemeNotSupported",
    "do_any",
    "get_logger",
    "get_template_logger",
    "get_template_logger_function",
    "get_template_path",
    "makeExtension",
]
