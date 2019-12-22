# mkdocstrings
[![pipeline status](https://gitlab.com/pawamoy/mkdocstrings/badges/master/pipeline.svg)](https://gitlab.com/pawamoy/mkdocstrings/pipelines)
[![coverage report](https://gitlab.com/pawamoy/mkdocstrings/badges/master/coverage.svg)](https://gitlab.com/pawamoy/mkdocstrings/commits/master)
[![documentation](https://img.shields.io/readthedocs/mkdocstrings.svg?style=flat)](https://mkdocstrings.readthedocs.io/en/latest/index.html)
[![pypi version](https://img.shields.io/pypi/v/mkdocstrings.svg)](https://pypi.org/project/mkdocstrings/)

Automatic documentation from docstrings, for mkdocs.

This plugin is still in alpha status. Here is how it looks with the [mkdocs-material theme](https://squidfunk.github.io/mkdocs-material/) for now:

![mkdocstrings](https://user-images.githubusercontent.com/3999221/71327911-e467d000-250e-11ea-83e7-a81ec59f41e2.gif)

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

## Usage

```yaml
# mkdocs.yml

# designed to work best with material theme
theme:
  name: "material"

# these extensions are required for best results
markdown_extensions:
  - admonition
  - codehilite
  - attr_list
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.inlinehilite
  - toc:
      permalink: true

plugins:
  - search
  - mkdocstrings
```

```markdown
# Reference

::: my_library.my_module.my_class
```

You can reference objects from other modules in your docstrings:

```python
def some_function():
    """
    This is my function.

    It references [another function][package.submodule.function].
    It also references another object directly: [package.submodule.SuperClass][].
    """
    pass
```

Add some style:

```css
div.autodoc {
  padding-left: 25px;
  border-left: 4px solid rgba(230, 230, 230);
}
```
