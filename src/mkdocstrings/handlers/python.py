import json
from subprocess import PIPE, Popen
import os

from mkdocs.utils import log

from . import BaseCollector, BaseHandler, BaseRenderer, CollectionError


class PythonRenderer(BaseRenderer):
    DEFAULT_CONFIG = {
        "show_root_heading": False,
        "show_root_full_path": True,
        "show_object_full_path": False,
        "show_category_heading": False,
        "show_if_no_docstring": False,
        "show_source": True,
        "group_by_category": True,
        "heading_level": 2,
    }

    def render(self, data, config):
        final_config = dict(self.DEFAULT_CONFIG)
        final_config.update(config)

        template = self.env.get_template(f"{data['category']}.html")

        # Heading level is a "state" variable, that will change at each step
        # of the rendering recursion. Therefore, it's easier to use it as a plain value
        # instead of as an item of a dictionary reference.
        heading_level = final_config.pop("heading_level")

        return template.render(
            **{"config": final_config, data["category"]: data, "heading_level": heading_level, "root": True}
        )

    def update_env(self, md):
        super(PythonRenderer, self).update_env(md)
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


class PythonCollector(BaseCollector):
    DEFAULT_CONFIG = {}

    def __init__(self):
        log.debug("mkdocstrings.handlers.python: Opening 'pytkdocs' subprocess")
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        self.process = Popen(["pytkdocs"], universal_newlines=True, stderr=PIPE, stdout=PIPE, stdin=PIPE, bufsize=-1, env=env)

    def collect(self, identifier, config: dict) -> dict:
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
            log.error("mkdocstrings.handlers.python: Error while loading JSON")
            raise CollectionError(str(error))

        if "error" in result:
            log.error(f"mkdocstrings.handlers.python: Collection failed: {result['error']}")
            raise CollectionError(result["error"])

        # We always collect only one object at a time
        result = result[0]

        log.debug("mkdocstrings.handlers.python: Rebuilding categories and children lists")
        rebuild_category_lists(result)

        return result

    def teardown(self):
        log.debug("mkdocstrings.handlers.python: Tearing process down")
        self.process.terminate()
        self.process = None


class PythonHandler(BaseHandler):
    pass


def get_handler():
    return PythonHandler(collector=PythonCollector(), renderer=PythonRenderer("python", "material"))


def rebuild_category_lists(obj):
    obj["attributes"] = [obj["children"][path] for path in obj["attributes"]]
    obj["classes"] = [obj["children"][path] for path in obj["classes"]]
    obj["functions"] = [obj["children"][path] for path in obj["functions"]]
    obj["methods"] = [obj["children"][path] for path in obj["methods"]]
    obj["modules"] = [obj["children"][path] for path in obj["modules"]]
    obj["children"] = [v for k, v in obj["children"].items()]
    for child in obj["children"]:
        rebuild_category_lists(child)
