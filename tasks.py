"""Development tasks."""

import os
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from shutil import which
from typing import Callable, Generator, Sequence

import invoke

PY_SRC_PATHS = (Path(_) for _ in ("src", "scripts", "tests", "tasks.py"))
PY_SRC_LIST = tuple(str(_) for _ in PY_SRC_PATHS)
PY_SRC = " ".join(PY_SRC_LIST)
MAIN_PYTHON = "3.6"
PYTHON_VERSIONS = ("3.6", "3.7", "3.8")
TESTING = os.environ.get("TESTING", "0") in {"1", "true"}
CI = os.environ.get("CI", "0") in {"1", "true"}
WINDOWS = os.name == "nt"
PTY = not WINDOWS


def get_poetry_venv(python_version: str) -> str:
    """
    Return the path to a poetry venv.

    Arguments:
        python_version: The version to get the virtual environment for.

    Returns:
        The path to the Poetry virtual environment.
    """
    current_venv = os.environ["VIRTUAL_ENV"]
    if current_venv.endswith(f"py{python_version}"):
        return current_venv
    return current_venv[: current_venv.rfind("-")] + f"-py{python_version}"


@contextmanager
def setpath(path: str) -> Generator:
    """
    Set the PATH environment variable in a with clause.

    Arguments:
        path: The path to prepend to the PATH environment variable.

    Yields:
        Nothing: yield to behave like a context manager.
    """
    current_path = os.environ["PATH"]
    os.environ["PATH"] = f"{path}:{current_path}"
    yield
    os.environ["PATH"] = current_path



def _python_ci_decorator(func: Callable) -> Callable:
    """
    Decorate a task to add `python_version` and `skip` attributes to the context.

    Arguments:
        func: The function to wrap.

    Returns:
        The wrapped function.
    """
    @wraps(func)  # noqa: WPS430 (nested function)
    def wrapper(context, *args, **kwargs):
        context.python_version = which("python")
        context.skip = False
        func(context, *args, **kwargs)

    return wrapper


def _python(versions: Sequence[str]) -> Callable:
    """
    Run a task onto multiple Python versions.

    Arguments:
        versions: The versions to run the decorated function through.

    Returns:
        A decorator.
    """
    if CI:
        return _python_ci_decorator

    def decorator(func):
        @wraps(func)  # noqa: WPS430 (nested function)
        def wrapper(context, *args, **kwargs):
            for version in versions:
                context.python_version = version
                path = Path(get_poetry_venv(version)) / "bin"
                if path.exists():
                    context.skip = False
                    with setpath(path):
                        func(context, *args, **kwargs)
                else:
                    context.skip = True
                    func(context, *args, **kwargs)

        return wrapper

    return decorator


invoke.python = _python


@invoke.task
def changelog(context):
    """
    Update the changelog in-place with latest commits.

    Arguments:
        context: The context of the Invoke task.
    """
    context.run(
        "failprint -t 'Updating changelog' -- python scripts/update_changelog.py "
        r"CHANGELOG.md '<!-- insertion marker -->' '^## \[v?(?P<version>[^\]]+)'",
        pty=PTY,
    )


@invoke.task
def check_code_quality(context):
    """Check the code quality.

    Arguments:
        context: The context of the Invoke task.
    """
    from failprint.cli import run as failprint  # noqa: C0415 (not installed when running invoke directly)

    code = failprint(title="Checking code quality", cmd=["flakehell", "lint", *PY_SRC_LIST])
    context.run("true" if code == 0 else "false")


@invoke.task
def check_dependencies(context):
    """Check for vulnerabilities in dependencies.

    Arguments:
        context: The context of the Invoke task.
    """
    safety = "safety" if which("safety") else "pipx run safety"
    context.run(
        "poetry export -f requirements.txt --without-hashes |"
        f"failprint --no-pty -t 'Checking dependencies' -- {safety} check --stdin --full-report",
        pty=PTY,
    )


@invoke.task
def check_docs(context):
    """Check if the documentation builds correctly.

    Arguments:
        context: The context of the Invoke task.
    """
    context.run("failprint -t 'Building documentation' -- mkdocs build -s", pty=PTY)


@invoke.task
@invoke.python(PYTHON_VERSIONS)
def check_types(context):
    """Check that the code is correctly typed.

    Arguments:
        context: The context of the Invoke task.
    """
    title = f"Type-checking ({context.python_version})"
    command = "mypy --config-file config/mypy.ini " + PY_SRC
    if context.skip:
        title += " (missing interpreter)"
        command = "true"
    context.run(f"failprint -t '{title}' -- {command}", pty=PTY)


@invoke.task(check_code_quality, check_types, check_docs, check_dependencies)
def check(context):  # noqa: W0613 (no use for the context argument)
    """
    Check it all!

    Arguments:
        context: The context of the Invoke task.
    """  # noqa: D400 (exclamation mark is funnier)


@invoke.task
def clean(context):
    """Delete temporary files.

    Arguments:
        context: The context of the Invoke task.
    """
    context.run("rm -rf .coverage*")
    context.run("rm -rf .mypy_cache")
    context.run("rm -rf .pytest_cache")
    context.run("rm -rf build")
    context.run("rm -rf dist")
    context.run("rm -rf pip-wheel-metadata")
    context.run("rm -rf site")
    context.run("find . -type d -name __pycache__ | xargs rm -rf")
    context.run("find . -name '*.rej' -delete")


@invoke.task
def docs_regen(context):
    """Regenerate some documentation pages.

    Arguments:
        context: The context of the Invoke task.
    """
    context.run("failprint -t 'Regenerating docfiles' -- python scripts/regen_docs.py")


@invoke.task(docs_regen)
def docs(context):
    """Build the documentation locally.

    Arguments:
        context: The context of the Invoke task.
    """
    context.run("mkdocs build")


@invoke.task(docs_regen)
def docs_serve(context, host="127.0.0.1", port=8000):
    """Serve the documentation (localhost:8000).

    Arguments:
        context: The context of the Invoke task.
        host: The host to serve the docs from.
        port: The port to serve the docs on.
    """
    context.run(f"mkdocs serve -a {host}:{port}")


@invoke.task(docs_regen)
def docs_deploy(context):
    """Deploy the documentation on GitHub pages.

    Arguments:
        context: The context of the Invoke task.
    """
    context.run("mkdocs gh-deploy")


@invoke.task
def format(context):  # noqa: W0622 (we don't mind shadowing the format builtin)
    """Run formatting tools on the code.

    Arguments:
        context: The context of the Invoke task.
    """
    context.run(
        "failprint -t 'Removing unused imports' -- "
        "autoflake -ir --exclude tests/fixtures --remove-all-unused-imports " + PY_SRC
    )
    context.run("failprint -t 'Ordering imports' -- isort -y -rc " + PY_SRC)
    context.run("failprint -t 'Formatting code' -- black " + PY_SRC)


@invoke.task
def release(context, version):
    """Release a new Python package.

    Arguments:
        context: The context of the Invoke task.
        version: The new version number to use.
    """
    context.run(f"failprint -t 'Bumping version in pyproject.toml' -- poetry version {version}")
    context.run("failprint -t 'Staging files' -- git add pyproject.toml CHANGELOG.md")
    context.run(f"failprint -t 'Committing changes' -- git commit -m 'chore: Prepare release {version}'")
    context.run(f"failprint -t 'Tagging commit' -- git tag {version}")
    if not TESTING:
        context.run("failprint -t 'Pushing commits' --no-pty -- git push")
        context.run("failprint -t 'Pushing tags' --no-pty -- git push --tags")
        context.run("failprint -t 'Building dist/wheel' -- poetry build")
        context.run("failprint -t 'Publishing version' -- poetry publish")
        context.run("failprint -t 'Deploying docs' -- poetry run mkdocs gh-deploy")


@invoke.task
def setup(context):
    """Set up the development environments (install dependencies).

    Arguments:
        context: The context of the Invoke task.
    """
    if CI:
        context.run("poetry install", pty=PTY)
        return
    for python in PYTHON_VERSIONS:
        message = f"Setting up Python {python} environment"
        print(message + "\n" + "-" * len(message))  # noqa: WPS421 (print -> side-effect)
        context.run(f"poetry env use {python} >/dev/null")
        opts = "" if python == MAIN_PYTHON else "--no-dev --extras tests"
        context.run(f"poetry install {opts} || true", pty=PTY)
        print()  # noqa: WPS421 (print -> side-effect)
    context.run(f"poetry env use {MAIN_PYTHON} &>/dev/null")


@invoke.task
def combine(context):
    """Combine coverage data from multiple runs.

    Arguments:
        context: The context of the Invoke task.
    """
    context.run("failprint -t 'Combining coverage data' -- coverage combine --rcfile=config/coverage.ini")


@invoke.task
def coverage(context):
    """Report coverage as text and HTML.

    Arguments:
        context: The context of the Invoke task.
    """
    context.run("coverage report --rcfile=config/coverage.ini")
    context.run("coverage html --rcfile=config/coverage.ini")


@invoke.task(post=[combine])
@invoke.python(PYTHON_VERSIONS)
def test(context, match=""):
    """Run the test suite.

    Arguments:
        context: The context of the Invoke task.
        match: A pytest expression to filter selected tests.
    """
    title = f"Running tests ({context.python_version})"
    command = (
        f"coverage run --rcfile=config/coverage.ini -m pytest -c config/pytest.ini -k '{match}' {PY_SRC} 2>/dev/null"
    )
    if context.skip:
        title += " (missing interpreter)"
        command = "true"
    context.run(f"failprint -t '{title}' -- {command}", pty=PTY)
