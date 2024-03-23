"""Development tasks."""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from importlib.metadata import version as pkgversion
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

from duty import duty
from duty.callables import coverage, lazy, mkdocs, mypy, pytest, ruff, safety

if TYPE_CHECKING:
    from duty.context import Context


PY_SRC_PATHS = (Path(_) for _ in ("src", "tests", "duties.py", "scripts"))
PY_SRC_LIST = tuple(str(_) for _ in PY_SRC_PATHS)
PY_SRC = " ".join(PY_SRC_LIST)
CI = os.environ.get("CI", "0") in {"1", "true", "yes", ""}
WINDOWS = os.name == "nt"
PTY = not WINDOWS and not CI
MULTIRUN = os.environ.get("MULTIRUN", "0") == "1"


def pyprefix(title: str) -> str:  # noqa: D103
    if MULTIRUN:
        prefix = f"(python{sys.version_info.major}.{sys.version_info.minor})"
        return f"{prefix:14}{title}"
    return title


@contextmanager
def material_insiders() -> Iterator[bool]:  # noqa: D103
    if "+insiders" in pkgversion("mkdocs-material"):
        os.environ["MATERIAL_INSIDERS"] = "true"
        try:
            yield True
        finally:
            os.environ.pop("MATERIAL_INSIDERS")
    else:
        yield False


@duty
def changelog(ctx: Context) -> None:
    """Update the changelog in-place with latest commits.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    from git_changelog.cli import main as git_changelog

    ctx.run(git_changelog, args=[[]], title="Updating changelog")


@duty(pre=["check_quality", "check_types", "check_docs", "check_dependencies", "check-api"])
def check(ctx: Context) -> None:  # noqa: ARG001
    """Check it all!

    Parameters:
        ctx: The context instance (passed automatically).
    """


@duty
def check_quality(ctx: Context) -> None:
    """Check the code quality.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    ctx.run(
        ruff.check(*PY_SRC_LIST, config="config/ruff.toml"),
        title=pyprefix("Checking code quality"),
        command=f"ruff check --config config/ruff.toml {PY_SRC}",
    )


@duty
def check_dependencies(ctx: Context) -> None:
    """Check for vulnerabilities in dependencies.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    # retrieve the list of dependencies
    requirements = ctx.run(
        ["uv", "pip", "freeze"],
        silent=True,
        allow_overrides=False,
    )

    ctx.run(
        safety.check(requirements),
        title="Checking dependencies",
        command="uv pip freeze | safety check --stdin",
    )


@duty
def check_docs(ctx: Context) -> None:
    """Check if the documentation builds correctly.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    Path("htmlcov").mkdir(parents=True, exist_ok=True)
    Path("htmlcov/index.html").touch(exist_ok=True)
    with material_insiders():
        ctx.run(
            mkdocs.build(strict=True, verbose=True),
            title=pyprefix("Building documentation"),
            command="mkdocs build -vs",
        )


@duty
def check_types(ctx: Context) -> None:
    """Check that the code is correctly typed.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    os.environ["MYPYPATH"] = "src"
    ctx.run(
        mypy.run(*PY_SRC_LIST, config_file="config/mypy.ini"),
        title=pyprefix("Type-checking"),
        command=f"mypy --config-file config/mypy.ini {PY_SRC}",
    )


@duty
def check_api(ctx: Context) -> None:
    """Check for API breaking changes.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    from griffe.cli import check as g_check

    griffe_check = lazy(g_check, name="griffe.check")
    ctx.run(
        griffe_check("mkdocstrings", search_paths=["src"], color=True),
        title="Checking for API breaking changes",
        command="griffe check -ssrc mkdocstrings",
        nofail=True,
    )


@duty(silent=True)
def clean(ctx: Context) -> None:
    """Delete temporary files.

    Parameters:
        ctx: The context instance (passed automatically).
    """

    def _rm(*targets: str) -> None:
        for target in targets:
            ctx.run(f"rm -rf {target}")

    def _find_rm(*targets: str) -> None:
        for target in targets:
            ctx.run(f"find . -type d -name '{target}' | xargs rm -rf")

    _rm("build", "dist", ".coverage*", "htmlcov", "site", ".pdm-build")
    _find_rm(".cache", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__")


@duty
def docs(ctx: Context, host: str = "127.0.0.1", port: int = 8000) -> None:
    """Serve the documentation (localhost:8000).

    Parameters:
        ctx: The context instance (passed automatically).
        host: The host to serve the docs from.
        port: The port to serve the docs on.
    """
    with material_insiders():
        ctx.run(
            mkdocs.serve(dev_addr=f"{host}:{port}"),
            title="Serving documentation",
            capture=False,
        )


@duty
def docs_deploy(ctx: Context) -> None:
    """Deploy the documentation on GitHub pages.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    os.environ["DEPLOY"] = "true"
    with material_insiders() as insiders:
        if not insiders:
            ctx.run(lambda: False, title="Not deploying docs without Material for MkDocs Insiders!")
        origin = ctx.run("git config --get remote.origin.url", silent=True)
        if "pawamoy-insiders/mkdocstrings" in origin:
            ctx.run(
                "git remote add org-pages git@github.com:mkdocstrings/mkdocstrings.github.io",
                silent=True,
                nofail=True,
            )
            ctx.run(
                mkdocs.gh_deploy(remote_name="upstream", force=True),
                title="Deploying documentation",
            )
        else:
            ctx.run(
                lambda: False,
                title="Not deploying docs from public repository (do that from insiders instead!)",
                nofail=True,
            )


@duty
def format(ctx: Context) -> None:
    """Run formatting tools on the code.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    ctx.run(
        ruff.check(*PY_SRC_LIST, config="config/ruff.toml", fix_only=True, exit_zero=True),
        title="Auto-fixing code",
    )
    ctx.run(ruff.format(*PY_SRC_LIST, config="config/ruff.toml"), title="Formatting code")


@duty(post=["docs-deploy"])
def release(ctx: Context, version: str) -> None:
    """Release a new Python package.

    Parameters:
        ctx: The context instance (passed automatically).
        version: The new version number to use.
    """
    origin = ctx.run("git config --get remote.origin.url", silent=True)
    if "pawamoy-insiders/mkdocstrings" in origin:
        ctx.run(
            lambda: False,
            title="Not releasing from insiders repository (do that from public repo instead!)",
        )
    ctx.run("git add pyproject.toml CHANGELOG.md", title="Staging files", pty=PTY)
    ctx.run(["git", "commit", "-m", f"chore: Prepare release {version}"], title="Committing changes", pty=PTY)
    ctx.run(f"git tag {version}", title="Tagging commit", pty=PTY)
    ctx.run("git push", title="Pushing commits", pty=False)
    ctx.run("git push --tags", title="Pushing tags", pty=False)
    ctx.run("pyproject-build", title="Building dist/wheel", pty=PTY)
    ctx.run("twine upload --skip-existing dist/*", title="Publishing version", pty=PTY)


@duty(silent=True, aliases=["coverage"])
def cov(ctx: Context) -> None:
    """Report coverage as text and HTML.

    Parameters:
        ctx: The context instance (passed automatically).
    """
    ctx.run(coverage.combine, nofail=True)
    ctx.run(coverage.report(rcfile="config/coverage.ini"), capture=False)
    ctx.run(coverage.html(rcfile="config/coverage.ini"))


@duty
def test(ctx: Context, match: str = "") -> None:
    """Run the test suite.

    Parameters:
        ctx: The context instance (passed automatically).
        match: A pytest expression to filter selected tests.
    """
    py_version = f"{sys.version_info.major}{sys.version_info.minor}"
    os.environ["COVERAGE_FILE"] = f".coverage.{py_version}"
    ctx.run(
        pytest.run("-n", "auto", "tests", config_file="config/pytest.ini", select=match, color="yes"),
        title=pyprefix("Running tests"),
        command=f"pytest -c config/pytest.ini -n auto -k{match!r} --color=yes tests",
    )


@duty
def vscode(ctx: Context) -> None:
    """Configure VSCode.

    This task will overwrite the following files,
    so make sure to back them up:

    - `.vscode/launch.json`
    - `.vscode/settings.json`
    - `.vscode/tasks.json`

    Parameters:
        ctx: The context instance (passed automatically).
    """

    def update_config(filename: str) -> None:
        source_file = Path("config", "vscode", filename)
        target_file = Path(".vscode", filename)
        target_file.parent.mkdir(exist_ok=True)
        target_file.write_text(source_file.read_text())

    for filename in ("launch.json", "settings.json", "tasks.json"):
        ctx.run(update_config, args=[filename], title=f"Update .vscode/{filename}")
