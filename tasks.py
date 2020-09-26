"""Development tasks."""

import os
from pathlib import Path
from shutil import which

import invoke

PY_SRC_PATHS = (Path(_) for _ in ("src", "scripts", "tests", "tasks.py"))
PY_SRC_LIST = tuple(str(_) for _ in PY_SRC_PATHS)
PY_SRC = " ".join(PY_SRC_LIST)
TESTING = os.environ.get("TESTING", "0") in {"1", "true"}
CI = os.environ.get("CI", "0") in {"1", "true"}
WINDOWS = os.name == "nt"
PTY = not WINDOWS


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
    context.run(f"failprint -t 'Checking code quality' -- flakehell lint {PY_SRC}", pty=PTY)


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
def check_types(context):
    """Check that the code is correctly typed.

    Arguments:
        context: The context of the Invoke task.
    """
    context.run(f"failprint -t 'Type-checking' -- mypy --config-file config/mypy.ini {PY_SRC}", pty=PTY)


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
    context.run("failprint -t 'Regenerating docfiles' -- python scripts/regen_docs.py", pty=PTY)


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
        "autoflake -ir --exclude tests/fixtures --remove-all-unused-imports " + PY_SRC,
        pty=PTY,
    )
    context.run("failprint -t 'Ordering imports' -- isort -y -rc " + PY_SRC, pty=PTY)
    context.run("failprint -t 'Formatting code' -- black " + PY_SRC, pty=PTY)


@invoke.task
def release(context, version):
    """Release a new Python package.

    Arguments:
        context: The context of the Invoke task.
        version: The new version number to use.
    """
    context.run(f"failprint -t 'Bumping version in pyproject.toml' -- poetry version {version}", pty=PTY)
    context.run("failprint -t 'Staging files' -- git add pyproject.toml CHANGELOG.md", pty=PTY)
    context.run(f"failprint -t 'Committing changes' -- git commit -m 'chore: Prepare release {version}'", pty=PTY)
    context.run(f"failprint -t 'Tagging commit' -- git tag {version}", pty=PTY)
    if not TESTING:
        context.run("failprint -t 'Pushing commits' --no-pty -- git push", pty=PTY)
        context.run("failprint -t 'Pushing tags' --no-pty -- git push --tags", pty=PTY)
        context.run("failprint -t 'Building dist/wheel' -- poetry build", pty=PTY)
        context.run("failprint -t 'Publishing version' -- poetry publish", pty=PTY)
        context.run("failprint -t 'Deploying docs' -- poetry run mkdocs gh-deploy", pty=PTY)


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


@invoke.task(pre=[invoke.task(lambda context: context.run("rm -f .coverage"))])
def test(context, match=""):
    """Run the test suite.

    Arguments:
        context: The context of the Invoke task.
        match: A pytest expression to filter selected tests.
    """
    context.run(f"failprint -t 'Running tests' -- pytest -c config/pytest.ini -n auto -k '{match}' {PY_SRC}", pty=PTY)
