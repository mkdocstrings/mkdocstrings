"""This module implements a handler for the Python language.

The handler collects data with [`pytkdocs`](https://github.com/pawamoy/pytkdocs).
"""

import json
import os
import sys
import traceback
from collections import ChainMap
from subprocess import PIPE, Popen  # noqa: S404 (what other option, more secure that PIPE do we have? sockets?)
from typing import Any, List, Optional

from markdown import Markdown

from mkdocstrings.handlers.base import BaseCollector, BaseHandler, BaseRenderer, CollectionError, CollectorItem
from mkdocstrings.loggers import get_logger

log = get_logger(__name__)


class PythonRenderer(BaseRenderer):
    """The class responsible for loading Jinja templates and rendering them.

    It defines some configuration options, implements the `render` method,
    and overrides the `update_env` method of the [`BaseRenderer` class][mkdocstrings.handlers.base.BaseRenderer].

    Attributes:
        fallback_theme: The theme to fallback to.
        default_config: The default rendering options,
            see [`default_config`][mkdocstrings.handlers.python.PythonRenderer.default_config].
    """

    fallback_theme = "material"

    default_config: dict = {
        "show_root_heading": False,
        "show_root_toc_entry": True,
        "show_root_full_path": True,
        "show_root_members_full_path": False,
        "show_object_full_path": False,
        "show_category_heading": False,
        "show_if_no_docstring": False,
        "show_signature_annotations": False,
        "show_source": True,
        "group_by_category": True,
        "heading_level": 2,
    }
    """The default rendering options.

    Option | Type | Description | Default
    ------ | ---- | ----------- | -------
    **`show_root_heading`** | `bool` | Show the heading of the object at the root of the documentation tree. | `False`
    **`show_root_toc_entry`** | `bool` | If the root heading is not shown, at least add a ToC entry for it. | `True`
    **`show_root_full_path`** | `bool` | Show the full Python path for the root object heading. | `True`
    **`show_object_full_path`** | `bool` | Show the full Python path of every object. | `False`
    **`show_root_members_full_path`** | `bool` | Show the full Python path of objects that are children of the root object (for example, classes in a module). When False, `show_object_full_path` overrides. | `False`
    **`show_category_heading`** | `bool` | When grouped by categories, show a heading for each category. | `False`
    **`show_if_no_docstring`** | `bool` | Show the object heading even if it has no docstring or children with docstrings. | `False`
    **`show_signature_annotations`** | `bool` | Show the type annotations in methods and functions signatures. | `False`
    **`show_source`** | `bool` | Show the source code of this object. | `True`
    **`group_by_category`** | `bool` | Group the object's children by categories: attributes, classes, functions, methods, and modules. | `True`
    **`heading_level`** | `int` | The initial heading level to use. | `2`
    """  # noqa: E501

    def render(self, data: CollectorItem, config: dict) -> str:  # noqa: D102 (ignore missing docstring)
        final_config = ChainMap(config, self.default_config)

        template = self.env.get_template(f"{data['category']}.html")

        # Heading level is a "state" variable, that will change at each step
        # of the rendering recursion. Therefore, it's easier to use it as a plain value
        # than as an item in a dictionary.
        heading_level = final_config["heading_level"]

        return template.render(
            **{"config": final_config, data["category"]: data, "heading_level": heading_level, "root": True},
        )

    def get_anchor(self, data: CollectorItem) -> str:  # noqa: D102 (ignore missing docstring)
        return data.get("path")

    def update_env(self, md: Markdown, config: dict) -> None:  # noqa: D102 (ignore missing docstring)
        super().update_env(md, config)
        self.env.trim_blocks = True
        self.env.lstrip_blocks = True
        self.env.keep_trailing_newline = False


class PythonCollector(BaseCollector):
    """The class responsible for loading Jinja templates and rendering them.

    It defines some configuration options, implements the `render` method,
    and overrides the `update_env` method of the [`BaseRenderer` class][mkdocstrings.handlers.base.BaseRenderer].
    """

    default_config: dict = {"filters": ["!^_[^_]"]}
    """The default selection options.

    Option | Type | Description | Default
    ------ | ---- | ----------- | -------
    **`filters`** | `List[str]` | Filter members with regular expressions. | `[ "!^_[^_]" ]`
    **`members`** | `Union[bool, List[str]]` | Explicitly select the object members. | *`pytkdocs` default: `True`*

    If `members` is a list of names, filters are applied only on the members children (not the members themselves).
    If `members` is `False`, none are selected.
    If `members` is `True` or an empty list, filters are applied on all members and their children.

    Members affect only the first layer of objects, while filters affect the whole object-tree recursively.

    Every filters is run against every object name. An object can be un-selected by a filter and re-selected by the
    next one:

    - `"!^_"`: exclude all objects starting with an underscore
    - `"^__"`: but select all objects starting with **two** underscores

    Obviously one could use a single filter instead: `"!^_[^_]"`, which is the default.
    """

    def __init__(self, setup_commands: Optional[List[str]] = None) -> None:
        """Initialize the object.

        When instantiating a Python collector, we open a subprocess in the background with `subprocess.Popen`.
        It will allow us to feed input to and read output from this subprocess, keeping it alive during
        the whole documentation generation. Spawning a new Python subprocess for each "autodoc" instruction would be
        too resource intensive, and would slow down `mkdocstrings` a lot.

        Arguments:
            setup_commands: A list of python commands as strings to be executed in the subprocess before `pytkdocs`.
        """
        log.debug("Opening 'pytkdocs' subprocess")
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        if setup_commands:
            # prevent the Python interpreter or the setup commands
            # from writing to stdout as it would break pytkdocs output
            commands = [
                "import sys",
                "from io import StringIO",
                "from pytkdocs.cli import main as pytkdocs",
                "sys.stdout = StringIO()",  # redirect stdout to memory buffer
                *setup_commands,
                "sys.stdout.flush()",
                "sys.stdout = sys.__stdout__",  # restore stdout
                "pytkdocs(['--line-by-line'])",
            ]
            cmd = [sys.executable, "-c", "; ".join(commands)]
        else:
            cmd = [sys.executable, "-m", "pytkdocs", "--line-by-line"]

        self.process = Popen(  # noqa: S603,S607 (we trust the input, and we don't want to use the absolute path)
            cmd,
            universal_newlines=True,
            stderr=PIPE,
            stdout=PIPE,
            stdin=PIPE,
            bufsize=-1,
            env=env,
        )

    def collect(self, identifier: str, config: dict) -> CollectorItem:
        """Collect the documentation tree given an identifier and selection options.

        In this method, we feed one line of JSON to the standard input of the subprocess that was opened
        during instantiation of the collector. Then we read one line of JSON on its standard output.

        We load back the JSON text into a Python dictionary.
        If there is a decoding error, we log it as error and raise a CollectionError.

        If the dictionary contains an `error` key, we log it  as error (with the optional `traceback` value),
        and raise a CollectionError.

        If the dictionary values for keys `loading_errors` and `parsing_errors` are not empty,
        we log them as warnings.

        Then we pick up the only object within the `objects` list (there's always only one, because we collect
        them one by one), rebuild it's categories lists
        (see [`rebuild_category_lists()`][mkdocstrings.handlers.python.rebuild_category_lists]),
        and return it.

        Arguments:
            identifier: The dotted-path of a Python object available in the Python path.
            config: Selection options, used to alter the data collection done by `pytkdocs`.

        Raises:
            CollectionError: When there was a problem collecting the object documentation.

        Returns:
            The collected object-tree.
        """
        final_config = ChainMap(config, self.default_config)

        log.debug("Preparing input")
        json_input = json.dumps({"objects": [{"path": identifier, **final_config}]})

        log.debug("Writing to process' stdin")
        self.process.stdin.write(json_input + "\n")  # type: ignore
        self.process.stdin.flush()  # type: ignore

        log.debug("Reading process' stdout")
        stdout = self.process.stdout.readline()  # type: ignore

        log.debug("Loading JSON output as Python object")
        try:
            result = json.loads(stdout)
        except json.decoder.JSONDecodeError as exception:
            error = "\n".join(("Error while loading JSON:", stdout, traceback.format_exc()))
            raise CollectionError(error) from exception

        error = result.get("error")
        if error:
            if "traceback" in result:
                error += f"\n{result['traceback']}"
            raise CollectionError(error)

        for loading_error in result["loading_errors"]:
            log.warning(loading_error)

        for errors in result["parsing_errors"].values():
            for parsing_error in errors:
                log.warning(parsing_error)

        # We always collect only one object at a time
        result = result["objects"][0]

        log.debug("Rebuilding categories and children lists")
        rebuild_category_lists(result)

        return result

    def teardown(self) -> None:
        """Terminate the opened subprocess, set it to `None`."""
        log.debug("Tearing process down")
        self.process.terminate()


class PythonHandler(BaseHandler):
    """The Python handler class, nothing specific here."""


def get_handler(
    theme: str,  # noqa: W0613 (unused argument config)
    custom_templates: Optional[str] = None,
    setup_commands: Optional[List[str]] = None,
    **config: Any,
) -> PythonHandler:
    """Simply return an instance of `PythonHandler`.

    Arguments:
        theme: The theme to use when rendering contents.
        custom_templates: Directory containing custom templates.
        setup_commands: A list of commands as strings to be executed in the subprocess before `pytkdocs`.
        config: Configuration passed to the handler.

    Returns:
        An instance of `PythonHandler`.
    """
    return PythonHandler(
        collector=PythonCollector(setup_commands=setup_commands),
        renderer=PythonRenderer("python", theme, custom_templates),
    )


def rebuild_category_lists(obj: dict) -> None:
    """Recursively rebuild the category lists of a collected object.

    Since `pytkdocs` dumps JSON on standard output, it must serialize the object-tree and flatten it to reduce data
    duplication and avoid cycle-references. Indeed, each node of the object-tree has a `children` list, containing
    all children, and another list for each category of children: `attributes`, `classes`, `functions`, `methods`
    and `modules`. It replaces the values in category lists with only the paths of the objects.

    Here, we reconstruct these category lists by picking objects in the `children` list using their path.

    For each object, we recurse on every one of its children.

    Arguments:
        obj: The collected object, loaded back from JSON into a Python dictionary.
    """
    for category in ("attributes", "classes", "functions", "methods", "modules"):
        obj[category] = [obj["children"][path] for path in obj[category]]
    obj["children"] = [child for _, child in obj["children"].items()]
    for child in obj["children"]:
        rebuild_category_lists(child)
