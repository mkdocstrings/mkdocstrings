"""Generate data to render the credits template."""

import json
import sys
from itertools import chain
from pathlib import Path

import httpx
import toml
from pip._internal.commands.show import search_packages_info  # noqa: WPS436 (better way?)


def clean_info(package_dict: dict) -> dict:
    """
    Only keep `name` and `home-page` keys.

    Arguments:
        package_dict: Package information.

    Returns:
        Cleaned-up information.
    """
    return {_: package_dict[_] for _ in ("name", "home-page")}


def get_data() -> dict:
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
    direct_dependencies = sorted(dep.lower() for dep in poetry_dependencies)
    direct_dependencies.remove("python")

    indirect_dependencies = sorted(
        pkg["name"] for pkg in lock_data["package"] if pkg["name"] not in direct_dependencies
    )

    dependencies = direct_dependencies + indirect_dependencies
    packages = {pkg["name"]: clean_info(pkg) for pkg in search_packages_info(dependencies)}
    # poetry.lock seems to always use lowercase for packages names
    packages.update({name.lower(): pkg for name, pkg in packages.items()})  # noqa: WPS221 (not that complex)

    for dependency in dependencies:
        if dependency not in packages:
            pkg_data = httpx.get(f"https://pypi.python.org/pypi/{dependency}/json").json()["info"]
            home_page = pkg_data["home_page"] or pkg_data["project_url"] or pkg_data["package_url"]
            pkg_name = pkg_data["name"]
            pkg = {"name": pkg_name, "home-page": home_page}
            packages.update({pkg_name: pkg, pkg_name.lower(): pkg})

    return {
        "project_name": project_name,
        "direct_dependencies": direct_dependencies,
        "indirect_dependencies": indirect_dependencies,
        "package_info": packages,
    }


def main() -> int:
    """
    Dump data as JSON.

    Returns:
        An exit code.
    """
    print(json.dumps(get_data()))  # noqa: WPS421 (side-effect)
    return 0


if __name__ == "__main__":
    sys.exit(main())
