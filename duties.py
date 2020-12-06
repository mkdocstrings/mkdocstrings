"""Development tasks."""

import os
import re
import sys
from itertools import chain
from pathlib import Path
from shutil import which
from typing import List, Optional, Pattern

import httpx
import toml
from duty import duty
from git_changelog.build import Changelog, Version
from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment
from pip._internal.commands.show import search_packages_info  # noqa: WPS436 (no other way?)

PY_SRC_PATHS = (Path(_) for _ in ("src/mkdocstrings", "tests", "duties.py"))
PY_SRC_LIST = tuple(str(_) for _ in PY_SRC_PATHS)
PY_SRC = " ".join(PY_SRC_LIST)
TESTING = os.environ.get("TESTING", "0") in {"1", "true"}
CI = os.environ.get("CI", "0") in {"1", "true", "yes", ""}
WINDOWS = os.name == "nt"
PTY = not WINDOWS and not CI


def latest(lines: List[str], regex: Pattern) -> Optional[str]:
    """
    Return the last released version.

    Arguments:
        lines: Lines of the changelog file.
        regex: A compiled regex to find version numbers.

    Returns:
        The last version.
    """
    for line in lines:
        match = regex.search(line)
        if match:
            return match.groupdict()["version"]
    return None


def unreleased(versions: List[Version], last_release: str) -> List[Version]:
    """
    Return the most recent versions down to latest release.

    Arguments:
        versions: All the versions (released and unreleased).
        last_release: The latest release.

    Returns:
        A list of versions.
    """
    for index, version in enumerate(versions):
        if version.tag == last_release:
            return versions[:index]
    return versions


def read_changelog(filepath: str) -> List[str]:
    """
    Read the changelog file.

    Arguments:
        filepath: The path to the changelog file.

    Returns:
        The changelog lines.
    """
    with open(filepath, "r") as changelog_file:
        return changelog_file.read().splitlines()


def write_changelog(filepath: str, lines: List[str]) -> None:
    """
    Write the changelog file.

    Arguments:
        filepath: The path to the changelog file.
        lines: The lines to write to the file.
    """
    with open(filepath, "w") as changelog_file:
        changelog_file.write("\n".join(lines).rstrip("\n") + "\n")


def update_changelog(
    inplace_file: str,
    marker: str,
    version_regex: str,
    template_url: str,
    commit_style: str,
) -> None:
    """
    Update the given changelog file in place.

    Arguments:
        inplace_file: The file to update in-place.
        marker: The line after which to insert new contents.
        version_regex: A regular expression to find currently documented versions in the file.
        template_url: The URL to the Jinja template used to render contents.
        commit_style: The style of commit messages to parse.
    """
    env = SandboxedEnvironment(autoescape=True)
    template = env.from_string(httpx.get(template_url).text)
    changelog = Changelog(".", style=commit_style)  # noqa: W0621 (shadowing changelog)

    if len(changelog.versions_list) == 1:
        last_version = changelog.versions_list[0]
        if last_version.planned_tag is None:
            planned_tag = "0.1.0"
            last_version.tag = planned_tag
            last_version.url += planned_tag
            last_version.compare_url = last_version.compare_url.replace("HEAD", planned_tag)

    lines = read_changelog(inplace_file)
    last_released = latest(lines, re.compile(version_regex))
    if last_released:
        changelog.versions_list = unreleased(changelog.versions_list, last_released)
    rendered = template.render(changelog=changelog, inplace=True)
    lines[lines.index(marker)] = rendered
    write_changelog(inplace_file, lines)


@duty
def changelog(ctx):
    """
    Update the changelog in-place with latest commits.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run(
        update_changelog,
        kwargs={
            "inplace_file": "CHANGELOG.md",
            "marker": "<!-- insertion marker -->",
            "version_regex": r"^## \[v?(?P<version>[^\]]+)",
            "template_url": "https://raw.githubusercontent.com/pawamoy/jinja-templates/master/keepachangelog.md",
            "commit_style": "angular",
        },
        title="Updating changelog",
        pty=PTY,
    )


@duty(pre=["check_code_quality", "check_types", "check_docs", "check_dependencies"])
def check(ctx):  # noqa: W0613 (no use for the context argument)
    """
    Check it all!

    Arguments:
        ctx: The context instance (passed automatically).
    """  # noqa: D400 (exclamation mark is funnier)


@duty
def check_code_quality(ctx, files=PY_SRC):
    """
    Check the code quality.

    Arguments:
        ctx: The context instance (passed automatically).
        files: The files to check.
    """
    ctx.run(f"flakehell lint {files}", title="Checking code quality", pty=PTY)


@duty
def check_dependencies(ctx):
    """
    Check for vulnerabilities in dependencies.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    nofail = False
    safety = which("safety")
    if not safety:
        pipx = which("pipx")
        if pipx:
            safety = f"{pipx} run safety"
        else:
            safety = "safety"
            nofail = True
    ctx.run(
        f"poetry export -f requirements.txt --without-hashes | {safety} check --stdin --full-report",
        title="Checking dependencies",
        pty=PTY,
        nofail=nofail,
    )


@duty
def check_docs(ctx):
    """
    Check if the documentation builds correctly.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    # pytkdocs fails on Python 3.9 for now
    nofail = sys.version.startswith("3.9")
    ctx.run("mkdocs build -s", title="Building documentation", pty=PTY, nofail=nofail, quiet=nofail)


@duty
def check_types(ctx):
    """
    Check that the code is correctly typed.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run(f"mypy --config-file config/mypy.ini {PY_SRC}", title="Type-checking", pty=PTY)


@duty(silent=True)
def clean(ctx):
    """
    Delete temporary files.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run("rm -rf .coverage*")
    ctx.run("rm -rf .mypy_cache")
    ctx.run("rm -rf .pytest_cache")
    ctx.run("rm -rf build")
    ctx.run("rm -rf dist")
    ctx.run("rm -rf pip-wheel-metadata")
    ctx.run("rm -rf site")
    ctx.run("find . -type d -name __pycache__ | xargs rm -rf")
    ctx.run("find . -name '*.rej' -delete")


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

    for dependency in dependencies:
        if dependency not in packages:
            pkg_data = httpx.get(f"https://pypi.python.org/pypi/{dependency}/json").json()["info"]
            home_page = pkg_data["home_page"] or pkg_data["project_url"] or pkg_data["package_url"]
            pkg_name = pkg_data["name"]
            package = {"name": pkg_name, "home-page": home_page}
            packages.update({pkg_name.lower(): package})

    return {
        "project_name": project_name,
        "direct_dependencies": sorted(direct_dependencies),
        "indirect_dependencies": sorted(indirect_dependencies),
        "package_info": packages,
    }


@duty
def docs_regen(ctx):
    """
    Regenerate some documentation pages.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    url_prefix = "https://raw.githubusercontent.com/pawamoy/jinja-templates/master/"
    regen_list = (("CREDITS.md", get_credits_data, url_prefix + "credits.md"),)

    def regen() -> int:  # noqa: WPS430 (nested function)
        """
        Regenerate pages listed in global `REGEN` list.

        Returns:
            An exit code.
        """
        env = SandboxedEnvironment(undefined=StrictUndefined)
        for target, get_data, template in regen_list:
            print("Regenerating", target)  # noqa: WPS421 (print)
            template_data = get_data()
            template_text = httpx.get(template).text
            rendered = env.from_string(template_text).render(**template_data)
            with open(target, "w") as stream:
                stream.write(rendered)
        return 0

    ctx.run(regen, title="Regenerating docfiles", pty=PTY)


@duty(pre=[docs_regen])
def docs(ctx):
    """
    Build the documentation locally.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run("mkdocs build", title="Building documentation")


@duty(pre=[docs_regen])
def docs_serve(ctx, host="127.0.0.1", port=8000):
    """
    Serve the documentation (localhost:8000).

    Arguments:
        ctx: The context instance (passed automatically).
        host: The host to serve the docs from.
        port: The port to serve the docs on.
    """
    ctx.run(f"mkdocs serve -a {host}:{port}", title="Serving documentation", capture=False)


@duty(pre=[docs_regen])
def docs_deploy(ctx):
    """
    Deploy the documentation on GitHub pages.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run("mkdocs gh-deploy", title="Deploying documentation")


@duty
def format(ctx):  # noqa: W0622 (we don't mind shadowing the format builtin)
    """
    Run formatting tools on the code.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run(
        f"autoflake -ir --exclude tests/fixtures --remove-all-unused-imports {PY_SRC}",
        title="Removing unused imports",
        pty=PTY,
    )
    ctx.run(f"isort -y -rc {PY_SRC}", title="Ordering imports", pty=PTY)
    ctx.run(f"black {PY_SRC}", title="Formatting code", pty=PTY)


@duty
def release(ctx, version):
    """
    Release a new Python package.

    Arguments:
        ctx: The context instance (passed automatically).
        version: The new version number to use.
    """
    ctx.run(f"poetry version {version}", title=f"Bumping version in pyproject.toml to {version}", pty=PTY)
    ctx.run("git add pyproject.toml CHANGELOG.md", title="Staging files", pty=PTY)
    ctx.run(["git", "commit", "-m", f"chore: Prepare release {version}"], title="Committing changes", pty=PTY)
    ctx.run(f"git tag {version}", title="Tagging commit", pty=PTY)
    if not TESTING:
        ctx.run("git push", title="Pushing commits", pty=False)
        ctx.run("git push --tags", title="Pushing tags", pty=False)
        ctx.run("poetry build", title="Building dist/wheel", pty=PTY)
        ctx.run("poetry publish", title="Publishing version", pty=PTY)
        ctx.run("mkdocs gh-deploy", title="Deploying documentation", pty=PTY)


@duty(silent=True)
def coverage(ctx):
    """
    Report coverage as text and HTML.

    Arguments:
        ctx: The context instance (passed automatically).
    """
    ctx.run("coverage report --rcfile=config/coverage.ini", capture=False)
    ctx.run("coverage html --rcfile=config/coverage.ini")


@duty(pre=[duty(lambda ctx: ctx.run("rm -f .coverage", silent=True))])
def test(ctx, match=""):
    """
    Run the test suite.

    Arguments:
        ctx: The context instance (passed automatically).
        match: A pytest expression to filter selected tests.
    """
    ctx.run(
        ["pytest", "-c", "config/pytest.ini", "-n", "auto", "-k", match, "tests"],
        title="Running tests",
        pty=PTY,
    )
