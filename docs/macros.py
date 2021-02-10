"""Macros and filters made available in Markdown pages."""

import functools
from itertools import chain
from pathlib import Path

import httpx
import toml
from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment
from pip._internal.commands.show import search_packages_info  # noqa: WPS436 (no other way?)


def get_credits_data() -> dict:
    """
    Return data used to generate the credits file.

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
    dependencies = direct_dependencies | indirect_dependencies

    packages = {}
    for pkg in search_packages_info(dependencies):
        pkg = {_: pkg[_] for _ in ("name", "home-page")}
        packages[pkg["name"].lower()] = pkg

    # all packages might not be credited,
    # like the ones that are now part of the standard library
    # or the ones that are only used on other operating systems,
    # and therefore are not installed,
    # but it's not that important

    return {
        "project_name": project_name,
        "direct_dependencies": sorted(direct_dependencies),
        "indirect_dependencies": sorted(indirect_dependencies),
        "package_info": packages,
    }


@functools.lru_cache(maxsize=None)
def get_credits():
    """
    Return credits as Markdown.

    Returns:
        The credits page Markdown.
    """
    jinja_env = SandboxedEnvironment(undefined=StrictUndefined)
    commit = "166758a98d5e544aaa94fda698128e00733497f4"
    template_url = f"https://raw.githubusercontent.com/pawamoy/jinja-templates/{commit}/credits.md"
    template_data = get_credits_data()
    template_text = httpx.get(template_url).text
    return jinja_env.from_string(template_text).render(**template_data)


def define_env(env):
    """
    Add macros and filters into the Jinja2 environment.

    This hook is called by `mkdocs-macros-plugin`
    when building the documentation.

    Arguments:
        env: An object used to add macros and filters to the environment.
    """

    @env.macro  # noqa: WPS430 (nested function)
    def credits():  # noqa: W0612,W0622,WPS430 (unused, shadows credits)
        return get_credits()
