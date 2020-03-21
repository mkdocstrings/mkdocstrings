"""
This module implements a handler for the Python language.

The handler collects data with [`pytkdocs`](https://github.com/pawamoy/pytkdocs).
"""

import json
import os
from subprocess import PIPE, Popen  # nosec: what other option, more secure that PIPE do we have? sockets?

from markdown import Markdown
from mkdocs.utils import log

from . import BaseCollector, BaseHandler, BaseRenderer, CollectionError


class PythonRenderer(BaseRenderer):
    """
    The class responsible for loading Jinja templates and rendering them.

    It defines some configuration options, implements the `render` method,
    and overrides the `update_env` method of the [`BaseRenderer` class][mkdocstrings.handlers.BaseRenderer].
    """

    FALLBACK_THEME = "material"

    DEFAULT_CONFIG: dict = {
        "show_root_heading": False,
        "show_root_toc_entry": True,
        "show_root_full_path": True,
        "show_object_full_path": False,
        "show_category_heading": False,
        "show_if_no_docstring": False,
        "show_source": True,
        "group_by_category": True,
        "heading_level": 2,
    }
    """
    The default rendering options.
    
    Option | Type | Description | Default
    ------ | ---- | ----------- | -------
    **`show_root_heading`** | `bool` | Show the heading of the object at the root of the documentation tree. | `False`
    **`show_root_toc_entry`** | `bool` | If the root heading is not shown, at least add a ToC entry for it. | `True`
    **`show_root_full_path`** | `bool` | Show the full Python path for the root object heading. | `True`
    **`show_object_full_path`** | `bool` | Show the full Python path of every object. | `False`
    **`show_category_heading`** | `bool` | When grouped by categories, show a heading for each category. | `False`
    **`show_if_no_docstring`** | `bool` | Show the object heading even if it has no docstring or children with docstrings. | `False`
    **`show_source`** | `bool` | Show the source code of this object. | `True`
    **`group_by_category`** | `bool` | Group the object's children by categories: attributes, classes, functions, methods, and modules. | `True`
    **`heading_level`** | `int` | The initial heading level to use. | `2`
    """

    def render(self, data: dict, config: dict) -> str:
        final_config = dict(self.DEFAULT_CONFIG)
        final_config.update(config)

        template = self.env.get_template(f"{data['category']}.html")

        # Heading level is a "state" variable, that will change at each step
        # of the rendering recursion. Therefore, it's easier to use it as a plain value
        # instead of as an item in a dictionary.
        heading_level = final_config.pop("heading_level")

        return template.render(
            **{"config": final_config, data["category"]: data, "heading_level": heading_level, "root": True}
        )

    def update_env(self, md: Markdown, config: dict) -> None:
        super(PythonRenderer, self).update_env(md, config)
        self.env.trim_blocks = True
        self.env.lstrip_blocks = True
        self.env.keep_trailing_newline = False

        # TODO: actually do this when we have a proper Google-Style docstring Markdown extension
        # md = Markdown(extensions=md.registeredExtensions + ["google_style_docstrings_markdown_extension"])
        #
        # def convert_docstring(text):
        #     return md.convert(text)
        #
        # self.env.filters["convert_docstring"] = convert_docstring

        # def break_args(signature, align=False):
        #     signature = signature.replace("\n", "")
        #     name, args = signature.split("(", 1)
        #     name = name.rstrip(" ")
        #     args = args.rstrip(")").split(", ")
        #     if not align:
        #         args = ",\n    ".join(args)
        #         return f"{name}(\n    {args}\n)"
        #     else:
        #         indent = " " * (name + 1)
        #         arg0 = args.pop(0)
        #         args = f",\n{indent}".join(args)
        #         return f"{name}({arg0}\n{indent}{args})"


class PythonCollector(BaseCollector):
    """
    The class responsible for loading Jinja templates and rendering them.

    It defines some configuration options, implements the `render` method,
    and overrides the `update_env` method of the [`BaseRenderer` class][mkdocstrings.handlers.BaseRenderer].
    """

    DEFAULT_CONFIG = {}

    def __init__(self) -> None:
        """
        Initialization method.

        When instantiating a Python collector, we open a subprocess in the background with `subprocess.Popen`.
        It will allow us to feed input to and read output from this subprocess, keeping it alive during
        the whole documentation generation. Spawning a new Python subprocess for each "autodoc" instruction would be
        too resource intensive, and would slow down `mkdocstrings` a lot.
        """
        log.debug("mkdocstrings.handlers.python: Opening 'pytkdocs' subprocess")
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        self.process = Popen(  # nosec: there's no way to give the full path to the executable, is there?
            ["pytkdocs", "--line-by-line"],
            universal_newlines=True,
            stderr=PIPE,
            stdout=PIPE,
            stdin=PIPE,
            bufsize=-1,
            env=env,
        )

    def collect(self, identifier: str, config: dict) -> dict:
        """
        Collect the documentation tree given an identifier and selection options.

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

        Returns:
            The collected object-tree.
        """
        log.debug("mkdocstrings.handlers.python: Preparing input")
        json_input = json.dumps({"global_config": {}, "objects": [{"path": identifier, "config": config}]})

        log.debug("mkdocstrings.handlers.python: Writing to process' stdin")
        print(json_input, file=self.process.stdin, flush=True)

        log.debug("mkdocstrings.handlers.python: Reading process' stdout")
        stdout = self.process.stdout.readline()

        log.debug("mkdocstrings.handlers.python: Loading JSON output as Python object")
        try:
            result = json.loads(stdout)
        except json.decoder.JSONDecodeError as error:
            log.error(f"mkdocstrings.handlers.python: Error while loading JSON: {stdout}")
            raise CollectionError(str(error))

        if "error" in result:
            message = f"mkdocstrings.handlers.python: Collection failed: {result['error']}"
            if "traceback" in result:
                message += f"\n{result['traceback']}"
            log.error(message)
            raise CollectionError(result["error"])

        if result["loading_errors"]:
            for error in result["loading_errors"]:
                log.warning(f"mkdocstrings.handlers.python: {error}")

        if result["parsing_errors"]:
            for path, errors in result["parsing_errors"].items():
                for error in errors:
                    log.warning(f"mkdocstrings.handlers.python: {path}: {error}")

        # We always collect only one object at a time
        result = result["objects"][0]

        log.debug("mkdocstrings.handlers.python: Rebuilding categories and children lists")
        rebuild_category_lists(result)

        return result

    def teardown(self) -> None:
        """Terminate the opened subprocess, set it to None."""
        log.debug("mkdocstrings.handlers.python: Tearing process down")
        self.process.terminate()
        self.process = None


class PythonHandler(BaseHandler):
    """The Python handler class, nothing specific here."""


def get_handler(theme: str) -> PythonHandler:
    """
    Simply return an instance of `PythonHandler`.

    Arguments:
        theme: The theme to use when rendering contents.

    Returns:
        An instance of `PythonHandler`.
    """
    return PythonHandler(collector=PythonCollector(), renderer=PythonRenderer("python", theme))


def rebuild_category_lists(obj: dict) -> None:
    """
    Recursively rebuild the category lists of a collected object.

    Since `pytkdocs` dumps JSON on standard output, it must serialize the object-tree and flatten it to reduce data
    duplication and avoid cycle-references. Indeed, each node of the object-tree has a `children` list, containing
    all children, and another list for each category of children: `attributes`, `classes`, `functions`, `methods`
    and `modules`. It replaces the values in category lists with only the paths of the objects.

    Here, we reconstruct these category lists by picking objects in the `children` list using their path.

    For each object, we recurse on every one of its children.

    Args:
        obj: The collected object, loaded back from JSON into a Python dictionary.
    """
    obj["attributes"] = [obj["children"][path] for path in obj["attributes"]]
    obj["classes"] = [obj["children"][path] for path in obj["classes"]]
    obj["functions"] = [obj["children"][path] for path in obj["functions"]]
    obj["methods"] = [obj["children"][path] for path in obj["methods"]]
    obj["modules"] = [obj["children"][path] for path in obj["modules"]]
    obj["children"] = [v for k, v in obj["children"].items()]
    for child in obj["children"]:
        rebuild_category_lists(child)
