#!/usr/bin/env python
"""Generate data to render the credits template."""

import json
from itertools import chain
from pathlib import Path

import requests
import toml
from pip._internal.commands.show import search_packages_info


def clean_info(package_dict):
    """Only keep `name` and `home-page` keys."""
    return {k: v for k, v in package_dict.items() if k in ("name", "home-page")}


def get_data():
    """Return data used to generate the credits file."""
    metadata = toml.load(Path(__file__).parent.parent / "pyproject.toml")["tool"]["poetry"]
    project_name = metadata["name"]
    direct_dependencies = sorted(
        _.lower() for _ in chain(metadata["dependencies"].keys(), metadata["dev-dependencies"].keys())
    )
    direct_dependencies.remove("python")

    lock_data = toml.load(Path(__file__).parent.parent / "poetry.lock")
    indirect_dependencies = sorted(p["name"] for p in lock_data["package"] if p["name"] not in direct_dependencies)

    package_info = {p["name"]: clean_info(p) for p in search_packages_info(direct_dependencies + indirect_dependencies)}

    for dependency in direct_dependencies + indirect_dependencies:
        # poetry.lock seems to always use lowercase for packages names
        if dependency not in [_.lower() for _ in package_info.keys()]:
            info = requests.get(f"https://pypi.python.org/pypi/{dependency}/json").json()["info"]
            package_info[info["name"]] = {
                "name": info["name"],
                "home-page": info["home_page"] or info["project_url"] or info["package_url"],
            }

    lower_package_info = {}
    for package_name, package in package_info.items():
        lower = package_name.lower()
        if lower != package_name:
            lower_package_info[lower] = package

    package_info.update(lower_package_info)

    return {
        "project_name": project_name,
        "direct_dependencies": direct_dependencies,
        "indirect_dependencies": indirect_dependencies,
        "package_info": package_info,
    }


def main():
    """Dump data as JSON."""
    print(json.dumps(get_data()))


if __name__ == "__main__":
    main()
