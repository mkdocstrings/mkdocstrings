#!/usr/bin/env bash
set -e

if ! command -v pdm &>/dev/null; then
    if ! command -v pipx &>/dev/null; then
        python3 -m pip install --user pipx
    fi
    pipx install pdm
fi
if ! pdm self list 2>/dev/null | grep -q pdm-multirun; then
    pdm install --plugins
fi

if [ -n "${PDM_MULTIRUN_VERSIONS}" ]; then
    if [ "${PDM_MULTIRUN_USE_VENVS}" -eq "1" ]; then
        for version in ${PDM_MULTIRUN_VERSIONS}; do
            if ! pdm venv --path "${version}" &>/dev/null; then
                pdm venv create --name "${version}" "${version}"
            fi
        done
    fi
    pdm multirun -v pdm install --dev
else
    pdm install --dev
fi
