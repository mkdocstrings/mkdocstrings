<!--
IMPORTANT:
  This file is generated from the template at 'scripts/templates/README.md'.
  Please update the template instead of this file.
-->

# mkdocstrings
[![pipeline status](https://gitlab.com/pawamoy/mkdocstrings/badges/master/pipeline.svg)](https://gitlab.com/pawamoy/mkdocstrings/pipelines)
[![coverage report](https://gitlab.com/pawamoy/mkdocstrings/badges/master/coverage.svg)](https://gitlab.com/pawamoy/mkdocstrings/commits/master)
[![documentation](https://img.shields.io/readthedocs/mkdocstrings.svg?style=flat)](https://mkdocstrings.readthedocs.io/en/latest/index.html)
[![pypi version](https://img.shields.io/pypi/v/mkdocstrings.svg)](https://pypi.org/project/mkdocstrings/)

Automatic documentation from docstrings, for mkdocs.

## Requirements
mkdocstrings requires Python 3.6 or above.

<details>
<summary>To install Python 3.6, I recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>

```bash
# install pyenv
git clone https://github.com/pyenv/pyenv ~/.pyenv

# setup pyenv (you should also put these three lines in .bashrc or similar)
export PATH="${HOME}/.pyenv/bin:${PATH}"
export PYENV_ROOT="${HOME}/.pyenv"
eval "$(pyenv init -)"

# install Python 3.6
pyenv install 3.6.8

# make it available globally
pyenv global system 3.6.8
```
</details>

## Installation
With `pip`:
```bash
python3.6 -m pip install mkdocstrings
```

With [`pipx`](https://github.com/cs01/pipx):
```bash
python3.6 -m pip install --user pipx

pipx install --python python3.6 mkdocstrings
```

## Usage (as a library)
TODO

## Usage (command-line)
```
usage: mkdocstrings [-h]

optional arguments:
  -h, --help  show this help message and exit

```
