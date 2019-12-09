"""
Module that contains the command line application.

Why does this file exist, and why not put this in __main__?

You might be tempted to import things from __main__ later,
but that will cause problems: the code will get executed twice:

- When you run `python -m mkdocstrings` python will execute
  ``__main__.py`` as a script. That means there won't be any
  ``mkdocstrings.__main__`` in ``sys.modules``.
- When you import __main__ it will get executed again (as a module) because
  there's no ``mkdocstrings.__main__`` in ``sys.modules``.

Also see http://click.pocoo.org/5/setuptools/#setuptools-integration.
"""

import argparse
import re


def main(args=None):
    """The main function, which is executed when you type ``mkdocstrings`` or ``python -m mkdocstrings``."""
    parser = get_parser()
    args = parser.parse_args(args=args)

    classes_filters = ["!^_[^_]", "!^__weakref__$"]
    classes_filters = [(f, re.compile(f.lstrip("!"))) for f in classes_filters]
    for name in ["_hello", "__weakref__", "__weakref", "__weakref__hehe", "__init__", "__init__hehe"]:
        print("should keep", name, should_keep(name, classes_filters))

    return 0


def should_keep(name, filters):
    keep = True
    for f, regex in filters:
        is_matching = bool(regex.match(name))
        if is_matching:
            if str(f).startswith("!"):
                is_matching = not is_matching
            keep = is_matching
    return keep


def get_parser():
    return argparse.ArgumentParser(prog="mkdocstrings")
