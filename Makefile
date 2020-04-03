.DEFAULT_GOAL := help

PY_SRC := src/ tests/ scripts/*.py

.PHONY: build
build:  ## Build the package wheel and sdist.
	poetry build

.PHONY: check
check: check-bandit check-black check-flake8 check-isort  ## Check it all!

.PHONY: check-bandit
check-bandit:  ## Check for security warnings in code using bandit.
	poetry run bandit -r src/

.PHONY: check-black
check-black:  ## Check if code is formatted nicely using black.
	poetry run black --check $(PY_SRC)

.PHONY: check-flake8
check-flake8:  ## Check for general warnings in code using flake8.
	poetry run flake8 $(PY_SRC)

.PHONY: check-isort
check-isort:  ## Check if imports are correctly ordered using isort.
	poetry run isort -c -rc $(PY_SRC)

.PHONY: check-mypy
check-mypy:  ## Check that the code is correctly typed.
	poetry run mypy $(PY_SRC)

.PHONY: check-pylint
check-pylint:  ## Check for code smells using pylint.
	poetry run pylint $(PY_SRC)

.PHONY: check-safety
check-safety:  ## Check for vulnerabilities in dependencies using safety.
	poetry run pip freeze 2>/dev/null | \
		grep -v mkdocstrings | \
		safety check --stdin --full-report 2>/dev/null

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
	poetry run sphinx-build -E -b html docs build/docs

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
	git commit -am "chore: Prepare release $(v)"
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
