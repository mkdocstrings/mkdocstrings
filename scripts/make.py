#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator


PYTHON_VERSIONS = os.getenv("PYTHON_VERSIONS", "3.9 3.10 3.11 3.12 3.13 3.14").split()
PYTHON_DEV = "3.14"


def shell(cmd: str, *, capture_output: bool = False, **kwargs: Any) -> str | None:
    """Run a shell command."""
    if capture_output:
        return subprocess.check_output(cmd, shell=True, text=True, **kwargs)  # noqa: S602
    subprocess.run(cmd, shell=True, check=True, stderr=subprocess.STDOUT, **kwargs)  # noqa: S602
    return None


@contextmanager
def environ(**kwargs: str) -> Iterator[None]:
    """Temporarily set environment variables."""
    original = dict(os.environ)
    os.environ.update(kwargs)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(original)


def uv_install(venv: Path) -> None:
    """Install dependencies using uv."""
    with environ(UV_PROJECT_ENVIRONMENT=str(venv), PYO3_USE_ABI3_FORWARD_COMPATIBILITY="1"):
        if "CI" in os.environ:
            shell("uv sync --no-editable")
        else:
            shell("uv sync")


def setup() -> None:
    """Setup the project."""
    if not shutil.which("uv"):
        raise ValueError("make: setup: uv must be installed, see https://github.com/astral-sh/uv")

    print("Installing dependencies (default environment)")
    default_venv = Path(".venv")
    if not default_venv.exists():
        shell("uv venv")
    uv_install(default_venv)

    if PYTHON_VERSIONS:
        for version in PYTHON_VERSIONS:
            print(f"\nInstalling dependencies (python{version})")
            venv_path = Path(f".venvs/{version}")
            if not venv_path.exists():
                shell(f"uv venv --python {version} {venv_path}")
            with environ(UV_PROJECT_ENVIRONMENT=str(venv_path.resolve())):
                uv_install(venv_path)


class _RunError(subprocess.CalledProcessError):
    def __init__(self, *args: Any, python_version: str, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.python_version = python_version


def run(version: str, cmd: str, *args: str, **kwargs: Any) -> None:
    """Run a command in a virtual environment."""
    kwargs = {"check": True, **kwargs}
    uv_run = ["uv", "run", "--no-sync"]
    try:
        if version == "default":
            with environ(UV_PROJECT_ENVIRONMENT=".venv"):
                subprocess.run([*uv_run, cmd, *args], **kwargs)  # noqa: S603, PLW1510
        else:
            with environ(UV_PROJECT_ENVIRONMENT=f".venvs/{version}", MULTIRUN="1"):
                subprocess.run([*uv_run, cmd, *args], **kwargs)  # noqa: S603, PLW1510
    except subprocess.CalledProcessError as process:
        raise _RunError(
            returncode=process.returncode,
            python_version=version,
            cmd=process.cmd,
            output=process.output,
            stderr=process.stderr,
        ) from process


def multirun(cmd: str, *args: str, **kwargs: Any) -> None:
    """Run a command for all configured Python versions."""
    if PYTHON_VERSIONS:
        for version in PYTHON_VERSIONS:
            run(version, cmd, *args, **kwargs)
    else:
        run("default", cmd, *args, **kwargs)


def allrun(cmd: str, *args: str, **kwargs: Any) -> None:
    """Run a command in all virtual environments."""
    run("default", cmd, *args, **kwargs)
    if PYTHON_VERSIONS:
        multirun(cmd, *args, **kwargs)


def clean() -> None:
    """Delete build artifacts and cache files."""
    paths_to_clean = ["build", "dist", "htmlcov", "site", ".coverage*", ".pdm-build"]
    for path in paths_to_clean:
        shutil.rmtree(path, ignore_errors=True)

    cache_dirs = {".cache", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__"}
    for dirpath in Path(".").rglob("*/"):
        if dirpath.parts[0] not in (".venv", ".venvs") and dirpath.name in cache_dirs:
            shutil.rmtree(dirpath, ignore_errors=True)


def vscode() -> None:
    """Configure VSCode to work on this project."""
    shutil.copytree("config/vscode", ".vscode", dirs_exist_ok=True)


def main() -> int:
    """Main entry point."""
    args = list(sys.argv[1:])
    if not args or args[0] == "help":
        if len(args) > 1:
            run("default", "duty", "--help", args[1])
        else:
            print(
                dedent(
                    """
                    Available commands
                      help                  Print this help. Add task name to print help.
                      setup                 Setup all virtual environments (install dependencies).
                      run                   Run a command in the default virtual environment.
                      multirun              Run a command for all configured Python versions.
                      allrun                Run a command in all virtual environments.
                      3.x                   Run a command in the virtual environment for Python 3.x.
                      clean                 Delete build artifacts and cache files.
                      vscode                Configure VSCode to work on this project.
                    """,
                ),
                flush=True,
            )
            if os.path.exists(".venv"):
                print("\nAvailable tasks", flush=True)
                run("default", "duty", "--list")
        return 0

    while args:
        cmd = args.pop(0)

        if cmd == "run":
            if not args:
                print("make: run: missing command", file=sys.stderr)
                return 1
            run("default", *args)  # ty: ignore[missing-argument]
            return 0

        if cmd == "multirun":
            if not args:
                print("make: run: missing command", file=sys.stderr)
                return 1
            multirun(*args)  # ty: ignore[missing-argument]
            return 0

        if cmd == "allrun":
            if not args:
                print("make: run: missing command", file=sys.stderr)
                return 1
            allrun(*args)  # ty: ignore[missing-argument]
            return 0

        if cmd.startswith("3."):
            if not args:
                print("make: run: missing command", file=sys.stderr)
                return 1
            run(cmd, *args)  # ty: ignore[missing-argument]
            return 0

        opts = []
        while args and (args[0].startswith("-") or "=" in args[0]):
            opts.append(args.pop(0))

        if cmd == "clean":
            clean()
        elif cmd == "setup":
            setup()
        elif cmd == "vscode":
            vscode()
        elif cmd == "check":
            multirun("duty", "check-quality", "check-types", "check-docs")
            run("default", "duty", "check-api")
        elif cmd in {"check-quality", "check-docs", "check-types", "test"}:
            multirun("duty", cmd, *opts)
        else:
            run("default", "duty", cmd, *opts)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except _RunError as process:
        if process.output:
            print(process.output, file=sys.stderr)
        if (code := process.returncode) == 139:  # noqa: PLR2004
            print(
                f"✗ (python{process.python_version})  '{' '.join(process.cmd)}' failed with return code {code} (segfault)",
                file=sys.stderr,
            )
            if process.python_version == PYTHON_DEV:
                code = 0
        sys.exit(code)
