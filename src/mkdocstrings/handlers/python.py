import json
from subprocess import PIPE, Popen

from . import BaseHandler, BaseRenderer, BaseCollector


class PythonRenderer(BaseRenderer):
    DEFAULT_RENDERING_OPTS = {
        "show_top_object_heading": False,
        "show_top_object_full_path": True,
        "group_by_categories": True,
        "show_groups_headings": False,
        "hide_no_doc": True,
        "add_source_details": True,
    }

    def render(self, data, config):
        final_config = dict(self.DEFAULT_RENDERING_OPTS)
        final_config.update(config)
        template = self.env.get_template(f"{data['category']}.html")
        return template.render(**{"config": final_config, data["category"]: data, "heading_level": 2})

    def update_env(self, md):
        super(PythonRenderer, self).update_env(md)
        # TODO: actually do this when we have a proper Google-Style docstring Markdown extension
        # md = Markdown(extensions=md.registeredExtensions + ["google_style_docstrings_markdown_extension"])
        #
        # def convert_docstring(text):
        #     return md.convert(text)
        #
        # self.env.filters["convert_docstring"] = convert_docstring


class PythonCollector(BaseCollector):
    DEFAULT_SELECTION_OPTS = {}

    def __init__(self):
        self.process = Popen(["pydocload"], universal_newlines=True, stderr=PIPE, stdout=PIPE, stdin=PIPE, bufsize=-1)

    def collect(self, identifier, config: dict) -> dict:
        json_input = json.dumps(
            {
                "global_config": {},
                "objects": [{"path": identifier, "config": config}],
            }
        )

        print(json_input, file=self.process.stdin, flush=True)
        stdout = self.process.stdout.readline()
        # if stderr:
        #     log.error(stderr)
        return json.loads(stdout)[0]

    def teardown(self):
        self.process.terminate()


class PythonHandler(BaseHandler):
    pass


def get_handler():
    return PythonHandler(collector=PythonCollector(), renderer=PythonRenderer("python", "material"))
