.DEFAULT_GOAL := help
SHELL := bash

DUTY = $(shell [ -n "${VIRTUAL_ENV}" ] || echo pdm run) duty

args = $(foreach a,$($(subst -,_,$1)_args),$(if $(value $a),$a="$($a)"))
check_quality_args = files
docs_serve_args = host port
release_args = version
test_args = match

BASIC_DUTIES = \
	changelog \
	check-dependencies \
	clean \
	coverage \
	docs \
	docs-deploy \
	docs-regen \
	docs-serve \
	format \
	release

QUALITY_DUTIES = \
	check-quality \
	check-docs \
	check-types \
	test

.PHONY: help
help:
	@$(DUTY) --list

.PHONY: lock
lock:
	@pdm lock

.PHONY: setup
setup:
	@bash scripts/setup.sh

.PHONY: check
check:
	@bash scripts/multirun.sh duty check-quality check-types check-docs
	@$(DUTY) check-dependencies

.PHONY: $(BASIC_DUTIES)
$(BASIC_DUTIES):
	@$(DUTY) $@ $(call args,$@)

.PHONY: $(QUALITY_DUTIES)
$(QUALITY_DUTIES):
	@bash scripts/multirun.sh duty $@ $(call args,$@)
