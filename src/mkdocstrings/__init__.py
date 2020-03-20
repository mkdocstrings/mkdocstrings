"""
mkdocstrings package.

Automatic documentation from source code, for mkdocs.

This project was originally written for Python source code only, hence the name.
It was then refactored to use external tools to load documentation. The main purpose
of this refactor was to be able to collect documentation in a Python subprocess instead
of the current one, allowing to avoid ugly hacks to unload/reload Python modules while
serving the documentation. The obvious benefit that also came from this refactor is
that mkdocstrings can now implement "handlers" for any given language, as long as there's
a tool able to collect documentation in source files for that language.
"""

from .plugin import MkdocstringsPlugin

__all__ = ["MkdocstringsPlugin"]
