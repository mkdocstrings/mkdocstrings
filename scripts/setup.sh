#!/usr/bin/env bash
set -e

PYTHON_VERSIONS="${PYTHON_VERSIONS-3.6 3.7 3.8 3.9 3.10 3.11}"

install_with_pipx() {
    if ! command -v "$1" &>/dev/null; then
        if ! command -v pipx &>/dev/null; then
            python3 -m pip install --user pipx
        fi
        pipx install "$1"
    fi
}

install_with_pipx pdm

if [ -n "${PYTHON_VERSIONS}" ]; then
    for python_version in ${PYTHON_VERSIONS}; do
        if pdm use -f "python${python_version}" &>/dev/null; then
            echo "> Using Python ${python_version} interpreter"
            pdm install
        else
            echo "> pdm use -f python${python_version}: Python interpreter not available?" >&2
        fi
    done
else
    pdm install
fi
