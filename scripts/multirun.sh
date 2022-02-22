#!/usr/bin/env bash
set -e

PYTHON_VERSIONS="${PYTHON_VERSIONS-3.7 3.8 3.9 3.10 3.11}"

restore_previous_python_version() {
    if pdm use -f "$1" &>/dev/null; then
        echo "> Restored previous Python version: ${1##*/}"
    fi
}

if [ -n "${PYTHON_VERSIONS}" ]; then
    old_python_version="$(pdm config python.path)"
    echo "> Currently selected Python version: ${old_python_version##*/}"
    trap "restore_previous_python_version ${old_python_version}" EXIT
    for python_version in ${PYTHON_VERSIONS}; do
        if pdm use -f "python${python_version}" &>/dev/null; then
        echo "> pdm run $@ (python${python_version})"
            pdm run "$@"
        else
            echo "> pdm use -f python${python_version}: Python interpreter not available?" >&2
        fi
    done
else
    pdm run "$@"
fi
