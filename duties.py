"""Development tasks."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from duty import duty, tools

if TYPE_CHECKING:
    from duty.context import Context


PY_SRC_PATHS = (Path(_) for _ in ("src", "tests", "duties.py", "scripts"))
PY_SRC_LIST = tuple(str(_) for _ in PY_SRC_PATHS)
PY_SRC = " ".join(PY_SRC_LIST)
CI = os.environ.get("CI", "0") in {"1", "true", "yes", ""}
WINDOWS = os.name == "nt"
PTY = not WINDOWS and not CI
MULTIRUN = os.environ.get("MULTIRUN", "0") == "1"
PY_VERSION = f"{sys.version_info.major}{sys.version_info.minor}"
PY_DEV = "315"


def pyprefix(title: str) -> str:
    if MULTIRUN:
        prefix = f"(python{sys.version_info.major}.{sys.version_info.minor})"
        return f"{prefix:14}{title}"
    return title


def _get_changelog_version() -> str:
    changelog_version_re = re.compile(r"^## \[(\d+\.\d+\.\d+)\].*$")
    with Path(__file__).parent.joinpath("CHANGELOG.md").open("r", encoding="utf8") as file:
        return next(filter(bool, map(changelog_version_re.match, file))).group(1)  # ty: ignore[invalid-argument-type,unresolved-attribute]


@duty
def changelog(ctx: Context, bump: str = "") -> None:
    """Update the changelog in-place with latest commits.

    Parameters:
        bump: Bump option passed to git-changelog.
    """
    ctx.run(tools.git_changelog(bump=bump or None), title="Updating changelog")
    ctx.run(tools.yore.check(bump=bump or _get_changelog_version()), title="Checking legacy code")


@duty(pre=["check-quality", "check-types", "check-docs", "check-api"])
def check(ctx: Context) -> None:
    """Check it all!"""


@duty(nofail=PY_VERSION == PY_DEV)
def check_quality(ctx: Context) -> None:
    """Check the code quality."""
    ctx.run(
        tools.ruff.check(*PY_SRC_LIST, config="config/ruff.toml", color=True),
        title=pyprefix("Checking code quality"),
    )


@duty(nofail=PY_VERSION == PY_DEV)
def check_docs(ctx: Context) -> None:
    """Check if the documentation builds correctly."""
    ctx.run(
        tools.zensical.build(strict=True),
        title=pyprefix("Building documentation"),
    )


@duty(nofail=PY_VERSION == PY_DEV)
def check_types(ctx: Context) -> None:
    """Check that the code is correctly typed."""
    py = f"{sys.version_info.major}.{sys.version_info.minor}"
    ctx.run(
        tools.ty.check(
            *PY_SRC_LIST,
            config_file="config/ty.toml",
            color=True,
            error_on_warning=True,
            python_version=py,
        ),
        title=pyprefix("Type-checking"),
    )


@duty(nofail=PY_VERSION == PY_DEV)
def check_api(ctx: Context, *cli_args: str) -> None:
    """Check for API breaking changes."""
    ctx.run(
        tools.griffe.check("mkdocstrings", search=["src"], color=True).add_args(*cli_args),
        title="Checking for API breaking changes",
        nofail=True,
    )


@duty
def docs(ctx: Context, *cli_args: str, host: str = "127.0.0.1", port: int = 8000) -> None:
    """Serve the documentation (localhost:8000).

    Parameters:
        host: The host to serve the docs from.
        port: The port to serve the docs on.
    """
    ctx.run(
        tools.zensical.serve(dev_addr=f"{host}:{port}").add_args(*cli_args),
        title="Serving documentation",
        capture=False,
    )


@duty
def docs_deploy(ctx: Context) -> None:
    """Deploy the documentation to GitHub pages."""
    from ghp_import import ghp_import  # noqa: PLC0415

    ctx.run(tools.zensical.build(), title="Building documentation site")
    ctx.run(
        ghp_import,
        kwargs={
            "srcdir": "site",
            "mesg": "chore: Update documentation",
            "push": True,
            "force": True,
            "remote": "org-pages",
        },
        title="Deploying site to GitHub Pages",
        command="ghp-import site -r org-pages -fpm 'chore: Update documentation'",
        pty=PTY,
    )


@duty
def format(ctx: Context) -> None:
    """Run formatting tools on the code."""
    ctx.run(
        tools.ruff.check(*PY_SRC_LIST, config="config/ruff.toml", fix_only=True, exit_zero=True),
        title="Auto-fixing code",
    )
    ctx.run(tools.ruff.format(*PY_SRC_LIST, config="config/ruff.toml"), title="Formatting code")


@duty
def build(ctx: Context) -> None:
    """Build source and wheel distributions."""
    ctx.run(
        ["uv", "build"],
        title="Building distributions",
        pty=PTY,
    )


@duty
def publish(ctx: Context) -> None:
    """Publish source and wheel distributions to PyPI."""
    if not Path("dist").exists():
        ctx.run("false", title="No distribution files found")
    dists = [str(dist) for dist in Path("dist").iterdir() if dist.suffix in (".gz", ".whl")]
    ctx.run(
        tools.twine.upload(*dists, skip_existing=True),
        title="Publishing distributions to PyPI",
        pty=PTY,
    )


@duty(post=["build", "publish", "docs-deploy"])
def release(ctx: Context, version: str = "") -> None:
    """Release a new Python package.

    Parameters:
        version: The new version number to use.
    """
    if not (version := (version or input("> Version to release: ")).strip()):
        ctx.run("false", title="A version must be provided")
    ctx.run("git add pyproject.toml CHANGELOG.md", title="Staging files", pty=PTY)
    ctx.run(["git", "commit", "-m", f"chore: Prepare release {version}"], title="Committing changes", pty=PTY)
    ctx.run(f"git tag -m '' -a {version}", title="Tagging commit", pty=PTY)
    ctx.run("git push", title="Pushing commits", pty=False)
    ctx.run("git push --tags", title="Pushing tags", pty=False)


@duty(silent=True, aliases=["cov"])
def coverage(ctx: Context) -> None:
    """Report coverage as text and HTML."""
    ctx.run(tools.coverage.combine(), nofail=True)
    ctx.run(tools.coverage.report(rcfile="config/coverage.ini"), capture=False)
    ctx.run(tools.coverage.html(rcfile="config/coverage.ini"))


@duty(nofail=PY_VERSION == PY_DEV)
def test(ctx: Context, *cli_args: str) -> None:
    """Run the test suite."""
    os.environ["COVERAGE_FILE"] = f".coverage.{PY_VERSION}"
    os.environ["PYTHONWARNDEFAULTENCODING"] = "1"
    ctx.run(
        tools.pytest(
            "tests",
            config_file="config/pytest.ini",
            color="yes",
        ).add_args("-n", "auto", *cli_args),
        title=pyprefix("Running tests"),
    )
