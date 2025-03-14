"""Deprecated. Import from `mkdocstrings` directly."""

# YORE: Bump 1: Remove file.

import warnings
from typing import Any

from mkdocstrings._internal import plugin


def __getattr__(name: str) -> Any:
    warnings.warn(
        "Importing from `mkdocstrings.plugin` is deprecated. Import from `mkdocstrings` directly.",
        DeprecationWarning,
        stacklevel=2,
    )
    return getattr(plugin, name)
