"""Generate the credits page."""

import functools
import re
from itertools import chain
from pathlib import Path
from urllib.request import urlopen

import mkdocs_gen_files
import toml
from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment


def get_credits_data() -> dict:
    """Return data used to generate the credits file.

    Returns:
        Data required to render the credits template.
    """
    project_dir = Path(__file__).parent.parent
    metadata = toml.load(project_dir / "pyproject.toml")["project"]
    metadata_pdm = toml.load(project_dir / "pyproject.toml")["tool"]["pdm"]
    lock_data = toml.load(project_dir / "pdm.lock")
    project_name = metadata["name"]

    all_dependencies = chain(
        metadata.get("dependencies", []),
        chain(*metadata.get("optional-dependencies", {}).values()),
        chain(*metadata_pdm.get("dev-dependencies", {}).values()),
    )
    direct_dependencies = {re.sub(r"[^\w-].*$", "", dep) for dep in all_dependencies}
    direct_dependencies = {dep.lower() for dep in direct_dependencies}
    indirect_dependencies = {pkg["name"].lower() for pkg in lock_data["package"]}
    indirect_dependencies -= direct_dependencies

    return {
        "project_name": project_name,
        "direct_dependencies": sorted(direct_dependencies),
        "indirect_dependencies": sorted(indirect_dependencies),
        "more_credits": "http://pawamoy.github.io/credits/",
    }


@functools.lru_cache(maxsize=None)
def get_credits():
    """Return credits as Markdown.

    Returns:
        The credits page Markdown.
    """
    jinja_env = SandboxedEnvironment(undefined=StrictUndefined)
    commit = "c78c29caa345b6ace19494a98b1544253cbaf8c1"
    template_url = f"https://raw.githubusercontent.com/pawamoy/jinja-templates/{commit}/credits.md"
    template_data = get_credits_data()
    template_text = urlopen(template_url).read().decode("utf8")  # noqa: S310
    return jinja_env.from_string(template_text).render(**template_data)


with mkdocs_gen_files.open("credits.md", "w") as fd:
    fd.write(get_credits())
mkdocs_gen_files.set_edit_path("credits.md", "gen_credits.py")
