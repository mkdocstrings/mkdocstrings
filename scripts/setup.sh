#!/usr/bin/env bash
set -e

PYTHON_VERSIONS="${PYTHON_VERSIONS-3.7 3.8 3.9 3.10 3.11}"

if ! command -v pdm &>/dev/null; then
    if ! command -v pipx &>/dev/null; then
        python3 -m pip install --user pipx
    fi
    pipx install pdm
fi
if ! pdm self list 2>/dev/null | grep -q pdm-multirun; then
    pipx inject pdm pdm-multirun
fi

if [ -n "${PYTHON_VERSIONS}" ]; then
    pdm multirun -vi ${PYTHON_VERSIONS// /,} pdm install
else
    pdm install
fi
