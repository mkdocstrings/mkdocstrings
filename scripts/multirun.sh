#!/usr/bin/env bash
set -e

PYTHON_VERSIONS="${PYTHON_VERSIONS-3.6 3.7 3.8 3.9 3.10 3.11}"

if [ -n "${PYTHON_VERSIONS}" ]; then
    for python_version in ${PYTHON_VERSIONS}; do
        if pdm use -f "python${python_version}" &>/dev/null; then
            echo "> pdm run $@ (Python ${python_version})"
            pdm run "$@"
        else
            echo "> pdm use -f python${python_version}: Python interpreter not available?" >&2
        fi
    done
else
    pdm run "$@"
fi
