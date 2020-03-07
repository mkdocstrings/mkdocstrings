import json
from subprocess import PIPE, Popen

from mkdocs.utils import log

from .. import BaseHandler, BaseRenderer


class PythonRenderer(BaseRenderer):
    def render(self, data):
        return ""


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
