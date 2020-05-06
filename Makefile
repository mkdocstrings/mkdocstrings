.DEFAULT_GOAL := help

PY_SRC := src/ tests/ scripts/
CI ?= false
TESTING ?= false

.PHONY: changelog
changelog:  ## Update the changelog in-place with latest commits.
	@poetry run failprint -t "Updating changelog" -- python scripts/update_changelog.py \
		CHANGELOG.md "<!-- insertion marker -->" "^## \[(?P<version>[^\]]+)"

.PHONY: check
check: check-docs check-code-quality check-types check-dependencies  ## Check it all!

.PHONY: check-code-quality
check-code-quality:  ## Check the code quality.
	@poetry run failprint -t "Checking code quality" -- flake8 --config=config/flake8.ini $(PY_SRC)

.PHONY: check-dependencies
check-dependencies:  ## Check for vulnerabilities in dependencies.
	@SAFETY=safety; \
	if ! $(CI); then \
		if ! command -v $$SAFETY &>/dev/null; then \
			SAFETY="pipx run safety"; \
		fi; \
	fi; \
	poetry run pip freeze 2>/dev/null | \
		grep -v mkdocstrings | \
		poetry run failprint --no-pty -t "Checking dependencies" -- $$SAFETY check --stdin --full-report

.PHONY: check-docs
check-docs:  ## Check if the documentation builds correctly.
	@poetry run failprint -t "Building documentation" -- mkdocs build -s

.PHONY: check-types
check-types:  ## Check that the code is correctly typed.
	@poetry run failprint -t "Type-checking" -- mypy --config-file config/mypy.ini $(PY_SRC)

.PHONY: clean
clean:  ## Delete temporary files.
	@rm -rf build 2>/dev/null
	@rm -rf .coverage* 2>/dev/null
	@rm -rf dist 2>/dev/null
	@rm -rf .mypy_cache 2>/dev/null
	@rm -rf pip-wheel-metadata 2>/dev/null
	@rm -rf .pytest_cache 2>/dev/null
	@rm -rf src/*.egg-info 2>/dev/null
	@rm -rf src/mkdocstrings/__pycache__ 2>/dev/null
	@rm -rf scripts/__pycache__ 2>/dev/null
	@rm -rf site 2>/dev/null
	@rm -rf tests/__pycache__ 2>/dev/null

.PHONY: docs
docs: docs-regen  ## Build the documentation locally.
	@poetry run mkdocs build

.PHONY: docs-regen
docs-regen:  ## Regenerate some documentation pages.
	@poetry run python scripts/regen_docs.py

.PHONY: docs-serve
docs-serve: docs-regen  ## Serve the documentation (localhost:8000).
	@poetry run mkdocs serve

.PHONY: docs-deploy
docs-deploy: docs-regen  ## Deploy the documentation on GitHub pages.
	@poetry run mkdocs gh-deploy

.PHONY: help
help:  ## Print this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.PHONY: format
format:  ## Run formatting tools on the code.
	@poetry run failprint -t "Formatting code" -- black $(PY_SRC)
	@poetry run failprint -t "Ordering imports" -- isort -y -rc $(PY_SRC)

.PHONY: release
release:  ## Create a new release (commit, tag, push, build, publish, deploy docs).
ifndef v
	$(error Pass the new version with 'make release v=0.0.0')
endif
	@poetry run failprint -t "Bumping version" -- poetry version $(v)
	@poetry run failprint -t "Staging files" -- git add pyproject.toml CHANGELOG.md
	@poetry run failprint -t "Committing changes" -- git commit -m "chore: Prepare release $(v)"
	@poetry run failprint -t "Tagging commit" -- git tag v$(v)
	@poetry run failprint -t "Building dist/wheel" -- poetry build
	-@if ! $(CI) && ! $(TESTING); then \
		poetry run failprint -t "Pushing commits" -- git push; \
		poetry run failprint -t "Pushing tags" -- git push --tags; \
		poetry run failprint -t "Publishing version" -- poetry publish; \
		poetry run failprint -t "Deploying docs" -- poetry run mkdocs gh-deploy; \
	fi

.PHONY: setup
setup:  ## Setup the development environment (install dependencies).
	@if ! $(CI); then \
		if ! command -v poetry &>/dev/null; then \
		  if ! command -v pipx &>/dev/null; then \
			  pip install --user pipx; \
			fi; \
		  pipx install poetry; \
		fi; \
	fi; \
	poetry install -v

.PHONY: test
test:  ## Run the test suite and report coverage.
	@poetry run pytest -c config/pytest.ini -n auto -k "$(K)" 2>/dev/null
	-@poetry run coverage html --rcfile=config/coverage.ini
