.DEFAULT_GOAL := help
SHELL := bash

INVOKE_OR_POETRY = $(shell ! command -v invoke &>/dev/null && echo poetry run) invoke
INVOKE_AND_POETRY = $(shell [ ! -n "${VIRTUAL_ENV}" ] && echo poetry run) invoke

POETRY_TASKS = \
	changelog \
	check \
	check-code-quality \
	check-dependencies \
	check-docs \
	check-types \
	combine \
	coverage \
	docs \
	docs-deploy \
	docs-regen \
	docs-serve \
	format \
	release \
	test

INVOKE_TASKS = \
	clean \
	setup


.PHONY: help
help:
	@$(INVOKE) --list

$(POETRY_TASKS):
	@$(INVOKE_AND_POETRY) $@ $(args)

$(INVOKE_TASKS):
	@$(INVOKE_OR_POETRY) $@ $(args)