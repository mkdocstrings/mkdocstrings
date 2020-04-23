.DEFAULT_GOAL := help

PY_SRC := src/ tests/ scripts/*.py

.PHONY: build
build:  ## Build the package wheel and sdist.
	poetry build

.PHONY: changelog
changelog:  ## Write the new changelog to the standard output.
	poetry run git-changelog -s angular .

.PHONY: check
check: check-docs check-flake8 check-mypy check-safety  ## Check it all!

.PHONY: check-docs
check-docs:  ## Check if the documentation builds correctly.
	@poetry run failprint -- mkdocs build -s

.PHONY: check-flake8
check-flake8:  ## Check for general warnings in code using flake8.
	@poetry run failprint -- flake8 $(PY_SRC)

.PHONY: check-mypy
check-mypy:  ## Check that the code is correctly typed.
	@poetry run failprint -- mypy $(PY_SRC)

.PHONY: check-safety
check-safety:  ## Check for vulnerabilities in dependencies using safety.
	@if ! command -v safety &>/dev/null; then \
		echo "Please install safety in a isolated virtualenv with 'pipx install safety'"; \
	else \
		poetry run pip freeze 2>/dev/null | \
			grep -v mkdocstrings | \
			poetry run failprint --no-pty -- safety check --stdin --full-report; \
	fi

.PHONY: clean
clean: clean-tests  ## Delete temporary files.
	@rm -rf build 2>/dev/null
	@rm -rf dist 2>/dev/null
	@rm -rf src/*.egg-info 2>/dev/null
	@rm -rf .coverage* 2>/dev/null
	@rm -rf .pytest_cache 2>/dev/null
	@rm -rf pip-wheel-metadata 2>/dev/null

.PHONY: clean-tests
clean-tests:  ## Delete temporary tests files.
	@rm -rf tests/tmp/* 2>/dev/null

.PHONY: credits
credits:  ## Regenerate CREDITS.md.
	poetry run ./scripts/gen-credits-data.py | \
		poetry run jinja2 --strict -o CREDITS.md --format=json scripts/templates/CREDITS.md -

.PHONY: docs
docs:  ## Build the documentation locally.
	poetry run mkdocs build -s

.PHONY: docs-serve
docs-serve:  ## Serve the documentation on localhost:8000.
	poetry run mkdocs serve

.PHONY: help
help:  ## Print this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.PHONY: lint
lint: lint-black lint-isort  ## Run linting tools on the code.

.PHONY: lint-black
lint-black:  ## Lint the code using black.
	poetry run black $(PY_SRC)

.PHONY: lint-isort
lint-isort:  ## Sort the imports using isort.
	poetry run isort -y -rc $(PY_SRC)

.PHONY: publish
publish:  ## Publish the latest built version on PyPI.
	poetry publish

.PHONY: release
release:  ## Create a new release (commit, tag, push, build, publish, deploy docs).
	poetry version $(v)
	git add pyproject.toml CHANGELOG.md
	git commit -m "chore: Prepare release $(v)"
	git tag v$(v)
	git push
	git push --tags
	poetry build
	poetry publish
	poetry run mkdocs gh-deploy

.PHONY: setup
setup:  ## Setup the development environment.
	poetry install

.PHONY: test
test: clean-tests  ## Run the tests using pytest.
	poetry run pytest -n auto -k "$(K)" 2>/dev/null
	-poetry run coverage html --rcfile=coverage.ini
