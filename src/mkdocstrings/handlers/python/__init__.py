import json
from subprocess import PIPE, Popen

from mkdocs.utils import log

from .. import BaseHandler, BaseRenderer


class PythonRenderer(BaseRenderer):
    DEFAULT_CONFIG = {
        "show_top_object_heading": False,
        "show_top_object_full_path": True,
        "group_by_categories": True,
        "show_groups_headings": False,
        "hide_no_doc": True,
        "add_source_details": True,
    }

    def render(self, data):
        template = self.env.get_template(f"python/{self.theme}/{data['category']}.html")
        return template.render(**{"config": self.config, data["category"]: data, "heading_level": 2})

    def update_env(self, md):
        super(PythonRenderer, self).update_env(md)
        # TODO: actually do this when we have a proper Google-Style docstring Markdown extension
        # md = Markdown(extensions=md.registeredExtensions + ["google_style_docstrings_markdown_extension"])
        #
        # def convert_docstring(text):
        #     return md.convert(text)
        #
        # self.env.filters["convert_docstring"] = convert_docstring


class PythonHandler(BaseHandler):
    def collect(self, selection: dict) -> dict:
        stdin = json.dumps(
            {
                "global_config": {},
                "objects": [{"path": identifier, "config": config} for identifier, config in selection.items()],
            }
        )
        with Popen(["pydocload"], universal_newlines=True, stderr=PIPE, stdout=PIPE, stdin=PIPE, bufsize=1) as process:
            stdout, stderr = process.communicate(input=stdin)
        if stderr:
            log.error(stderr)
        collected = json.loads(stdout)
        return {item["path"]: item for item in collected}


handler = PythonHandler(renderer_class=PythonRenderer)
