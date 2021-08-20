import functools
import urllib
from itertools import chain
from pathlib import Path

import mkdocs_gen_files
import toml
from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment
from pip._internal.commands.show import search_packages_info  # noqa: WPS436 (no other way?)


def get_credits_data() -> dict:
    """Return data used to generate the credits file.

    Returns:
        Data required to render the credits template.
    """
    project_dir = Path(__file__).parent.parent
    metadata = toml.load(project_dir / "pyproject.toml")["tool"]["poetry"]
    lock_data = toml.load(project_dir / "poetry.lock")
    project_name = metadata["name"]

    poetry_dependencies = chain(metadata["dependencies"].keys(), metadata["dev-dependencies"].keys())
    direct_dependencies = {dep.lower() for dep in poetry_dependencies}
    direct_dependencies.remove("python")
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
    commit = "398879aba2a365049870709116a689618afeb5b7"
    template_url = f"https://raw.githubusercontent.com/pawamoy/jinja-templates/{commit}/credits.md"
    template_data = get_credits_data()
    template_text = urllib.request.urlopen(template_url).read().decode("utf8")  # noqa: S310
    return jinja_env.from_string(template_text).render(**template_data)


with mkdocs_gen_files.open("credits.md", "w") as f:
    f.write(get_credits())
mkdocs_gen_files.set_edit_path("credits.md", "gen_credits.py")
