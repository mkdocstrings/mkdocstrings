"""Script to generate the project's credits."""

from __future__ import annotations

import os
import sys
from collections import defaultdict
from importlib.metadata import distributions
from itertools import chain
from pathlib import Path
from textwrap import dedent
from typing import Dict, Iterable, Union

from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment
from packaging.requirements import Requirement

# TODO: Remove once support for Python 3.10 is dropped.
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

project_dir = Path(os.getenv("MKDOCS_CONFIG_DIR", "."))
with project_dir.joinpath("pyproject.toml").open("rb") as pyproject_file:
    pyproject = tomllib.load(pyproject_file)
project = pyproject["project"]
project_name = project["name"]
with project_dir.joinpath("devdeps.txt").open() as devdeps_file:
    devdeps = [line.strip() for line in devdeps_file if not line.startswith("-e")]

PackageMetadata = Dict[str, Union[str, Iterable[str]]]
Metadata = Dict[str, PackageMetadata]


def _merge_fields(metadata: dict) -> PackageMetadata:
    fields = defaultdict(list)
    for header, value in metadata.items():
        fields[header.lower()].append(value.strip())
    return {
        field: value if len(value) > 1 or field in ("classifier", "requires-dist") else value[0]
        for field, value in fields.items()
    }


def _norm_name(name: str) -> str:
    return name.replace("_", "-").replace(".", "-").lower()


def _requirements(deps: list[str]) -> dict[str, Requirement]:
    return {_norm_name((req := Requirement(dep)).name): req for dep in deps}


def _extra_marker(req: Requirement) -> str | None:
    if not req.marker:
        return None
    try:
        return next(marker[2].value for marker in req.marker._markers if getattr(marker[0], "value", None) == "extra")
    except StopIteration:
        return None


def _get_metadata() -> Metadata:
    metadata = {}
    for pkg in distributions():
        name = _norm_name(pkg.name)  # type: ignore[attr-defined,unused-ignore]
        metadata[name] = _merge_fields(pkg.metadata)  # type: ignore[arg-type]
        metadata[name]["spec"] = set()
        metadata[name]["extras"] = set()
        metadata[name].setdefault("summary", "")
        _set_license(metadata[name])
    return metadata


def _set_license(metadata: PackageMetadata) -> None:
    license_field = metadata.get("license-expression", metadata.get("license", ""))
    license_name = license_field if isinstance(license_field, str) else " + ".join(license_field)
    check_classifiers = license_name in ("UNKNOWN", "Dual License", "") or license_name.count("\n")
    if check_classifiers:
        license_names = []
        for classifier in metadata["classifier"]:
            if classifier.startswith("License ::"):
                license_names.append(classifier.rsplit("::", 1)[1].strip())
        license_name = " + ".join(license_names)
    metadata["license"] = license_name or "?"


def _get_deps(base_deps: dict[str, Requirement], metadata: Metadata) -> Metadata:
    deps = {}
    for dep_name, dep_req in base_deps.items():
        if dep_name not in metadata:
            continue
        metadata[dep_name]["spec"] |= {str(spec) for spec in dep_req.specifier}  # type: ignore[operator]
        metadata[dep_name]["extras"] |= dep_req.extras  # type: ignore[operator]
        deps[dep_name] = metadata[dep_name]

    again = True
    while again:
        again = False
        for pkg_name in metadata:
            if pkg_name in deps:
                for pkg_dependency in metadata[pkg_name].get("requires-dist", []):
                    requirement = Requirement(pkg_dependency)
                    dep_name = _norm_name(requirement.name)
                    extra_marker = _extra_marker(requirement)
                    if (
                        dep_name in metadata
                        and dep_name not in deps
                        and dep_name != project["name"]
                        and (not extra_marker or extra_marker in deps[pkg_name]["extras"])
                    ):
                        metadata[dep_name]["spec"] |= {str(spec) for spec in requirement.specifier}  # type: ignore[operator]
                        deps[dep_name] = metadata[dep_name]
                        again = True

    return deps


def _render_credits() -> str:
    metadata = _get_metadata()
    dev_dependencies = _get_deps(_requirements(devdeps), metadata)
    prod_dependencies = _get_deps(
        _requirements(
            chain(  # type: ignore[arg-type]
                project.get("dependencies", []),
                chain(*project.get("optional-dependencies", {}).values()),
            ),
        ),
        metadata,
    )

    template_data = {
        "project_name": project_name,
        "prod_dependencies": sorted(prod_dependencies.values(), key=lambda dep: str(dep["name"])),
        "dev_dependencies": sorted(dev_dependencies.values(), key=lambda dep: str(dep["name"])),
        "more_credits": "http://pawamoy.github.io/credits/",
    }
    template_text = dedent(
        """
        # Credits

        These projects were used to build *{{ project_name }}*. **Thank you!**

        [Python](https://www.python.org/) |
        [uv](https://github.com/astral-sh/uv) |
        [copier-uv](https://github.com/pawamoy/copier-uv)

        {% macro dep_line(dep) -%}
        [{{ dep.name }}](https://pypi.org/project/{{ dep.name }}/) | {{ dep.summary }} | {{ ("`" ~ dep.spec|sort(reverse=True)|join(", ") ~ "`") if dep.spec else "" }} | `{{ dep.version }}` | {{ dep.license }}
        {%- endmacro %}

        {% if prod_dependencies -%}
        ### Runtime dependencies

        Project | Summary | Version (accepted) | Version (last resolved) | License
        ------- | ------- | ------------------ | ----------------------- | -------
        {% for dep in prod_dependencies -%}
        {{ dep_line(dep) }}
        {% endfor %}

        {% endif -%}
        {% if dev_dependencies -%}
        ### Development dependencies

        Project | Summary | Version (accepted) | Version (last resolved) | License
        ------- | ------- | ------------------ | ----------------------- | -------
        {% for dep in dev_dependencies -%}
        {{ dep_line(dep) }}
        {% endfor %}

        {% endif -%}
        {% if more_credits %}**[More credits from the author]({{ more_credits }})**{% endif %}
        """,
    )
    jinja_env = SandboxedEnvironment(undefined=StrictUndefined)
    return jinja_env.from_string(template_text).render(**template_data)


print(_render_credits())
