"""mkdocstrings package.

Automatic documentation from sources, for MkDocs.
"""

from __future__ import annotations

from mkdocstrings._internal.extension import AutoDocProcessor, MkdocstringsExtension
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
]
