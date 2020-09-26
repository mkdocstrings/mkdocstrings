.DEFAULT_GOAL := help
SHELL := bash

INVOKE_OR_POETRY = $(shell command -v invoke &>/dev/null || echo poetry run) invoke
INVOKE_AND_POETRY = $(shell [ -n "${VIRTUAL_ENV}" ] || echo poetry run) invoke

PYTHON_VERSIONS ?= 3.6 3.7 3.8

POETRY_TASKS = \
	changelog \
	combine \
	coverage \
	docs \
	docs-deploy \
	docs-regen \
	docs-serve \
	format \
	release

QUALITY_TASKS = \
	check \
	check-code-quality \
	check-dependencies \
	check-docs \
	check-types \
	test

INVOKE_TASKS = \
	clean


.PHONY: help
help:
	@$(INVOKE_OR_POETRY) --list

.PHONY: setup
setup:
	@env PYTHON_VERSIONS="$(PYTHON_VERSIONS)" bash scripts/setup.sh

.PHONY: $(POETRY_TASKS)
$(POETRY_TASKS):
	@$(INVOKE_AND_POETRY) $@ $(args)

.PHONY: $(QUALITY_TASKS)
$(QUALITY_TASKS):
	@env PYTHON_VERSIONS="$(PYTHON_VERSIONS)" bash scripts/run_task.sh $(INVOKE_AND_POETRY) $@ $(args)

.PHONY: $(INVOKE_TASKS)
$(INVOKE_TASKS):
	@$(INVOKE_OR_POETRY) $@ $(args)
