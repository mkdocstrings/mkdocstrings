#!/usr/bin/env python

import json
from itertools import chain
from pathlib import Path

import requests
import toml
from pip._internal.commands.show import search_packages_info


def add_vlz_url(p):
    try:
        with open(Path(__file__).parent / "templates" / "vlz" / (p["name"] + ".txt")) as stream:
            p["vlz-url"] = stream.read().rstrip("\n")
    except FileNotFoundError:
        pass
    return p


def clean_info(p):
    p = add_vlz_url(p)
    return {k: v for k, v in p.items() if k in ("name", "home-page", "vlz-url")}


metadata = toml.load(Path(__file__).parent.parent / "pyproject.toml")["tool"]["poetry"]
direct_dependencies = sorted(
    [_.lower() for _ in chain(metadata["dependencies"].keys(), metadata["dev-dependencies"].keys())]
)
direct_dependencies.remove("python")

lock_data = toml.load(Path(__file__).parent.parent / "poetry.lock")
indirect_dependencies = sorted([p["name"] for p in lock_data["package"] if p["name"] not in direct_dependencies])

# poetry.lock seems to always use lowercase for packages names
package_info = {p["name"]: clean_info(p) for p in search_packages_info(direct_dependencies + indirect_dependencies)}

for dependency in direct_dependencies + indirect_dependencies:
    if dependency not in [_.lower() for _ in package_info.keys()]:
        info = requests.get(f"https://pypi.python.org/pypi/{dependency}/json").json()["info"]
        package_info[info["name"]] = add_vlz_url(
            {"name": info["name"], "home-page": info["home_page"] or info["project_url"] or info["package_url"]}
        )

lower_package_info = {}
for package_name, package in package_info.items():
    lower = package_name.lower()
    if lower != package_name:
        lower_package_info[lower] = package

package_info.update(lower_package_info)

json_output = json.dumps(
    {
        "direct_dependencies": direct_dependencies,
        "indirect_dependencies": indirect_dependencies,
        "package_info": package_info,
    }
)
print(json_output)
