import re
from itertools import chain
from pathlib import Path
from textwrap import dedent

import toml
from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment

try:
    from importlib.metadata import metadata, PackageNotFoundError
except ImportError:
    from importlib_metadata import metadata, PackageNotFoundError

project_dir = Path(".")
pyproject = toml.load(project_dir / "pyproject.toml")
project = pyproject["project"]
pdm = pyproject["tool"]["pdm"]
lock_data = toml.load(project_dir / "pdm.lock")
lock_pkgs = {pkg["name"].lower(): pkg for pkg in lock_data["package"]}
project_name = project["name"]
regex = re.compile(r"(?P<dist>[\w.-]+)(?P<spec>.*)$")

def get_license(pkg_name):
    try:
        data = metadata(pkg_name)
    except PackageNotFoundError:
        return "?"
    license = data.get("License", "").strip()
    multiple_lines = bool(license.count("\n"))
    # TODO: remove author logic once all my packages licenses are fixed
    author = ""
    if multiple_lines or not license or license == "UNKNOWN":
        for header, value in data.items():
            if header == "Classifier" and value.startswith("License ::"):
                license = value.rsplit("::", 1)[1].strip()
            elif header == "Author-email":
                author = value
    if license == "Other/Proprietary License" and "pawamoy" in author:
        license = "ISC"
    return license or "?"

def get_deps(base_deps):
    deps = {}
    for dep in base_deps:
        parsed = regex.match(dep).groupdict()
        dep_name = parsed["dist"].lower()
        deps[dep_name] = {"license": get_license(dep_name), **parsed, **lock_pkgs[dep_name]}

    again = True
    while again:
        again = False
        for pkg_name in lock_pkgs:
            if pkg_name in deps:
                for pkg_dependency in lock_pkgs[pkg_name].get("dependencies", []):
                    parsed = regex.match(pkg_dependency).groupdict()
                    dep_name = parsed["dist"].lower()
                    if dep_name not in deps:
                        deps[dep_name] = {"license": get_license(dep_name), **parsed, **lock_pkgs[dep_name]}
                        again = True
        
    return deps

dev_dependencies = get_deps(chain(*pdm.get("dev-dependencies", {}).values()))
prod_dependencies = get_deps(
    chain(
        project.get("dependencies", []),
        chain(*project.get("optional-dependencies", {}).values()),
    )
)

template_data = {
    "project_name": project_name,
    "prod_dependencies": sorted(prod_dependencies.values(), key=lambda dep: dep["name"]),
    "dev_dependencies": sorted(dev_dependencies.values(), key=lambda dep: dep["name"]),
    "more_credits": "http://pawamoy.github.io/credits/",
}
template_text = dedent(
    """
    These projects were used to build `{{ project_name }}`. **Thank you!**

    [`python`](https://www.python.org/) |
    [`pdm`](https://pdm.fming.dev/) |
    [`copier-pdm`](https://github.com/pawamoy/copier-pdm)

    {% macro dep_line(dep) -%}
    [`{{ dep.name }}`](https://pypi.org/project/{{ dep.name }}/) | {{ dep.summary }} | {{ ("`" ~ dep.spec ~ "`") if dep.spec else "" }} | `{{ dep.version }}` | {{ dep.license }}
    {%- endmacro %}

    ### Runtime dependencies

    Project | Summary | Version (accepted) | Version (last resolved) | License
    ------- | ------- | ------------------ | ----------------------- | -------
    {% for dep in prod_dependencies -%}
    {{ dep_line(dep) }}
    {% endfor %}

    ### Development dependencies

    Project | Summary | Version (accepted) | Version (last resolved) | License
    ------- | ------- | ------------------ | ----------------------- | -------
    {% for dep in dev_dependencies -%}
    {{ dep_line(dep) }}
    {% endfor %}

    {% if more_credits %}**[More credits from the author]({{ more_credits }})**{% endif %}
    """
)
jinja_env = SandboxedEnvironment(undefined=StrictUndefined)
print(jinja_env.from_string(template_text).render(**template_data))
