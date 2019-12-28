# mkdocstrings
[![pipeline status](https://gitlab.com/pawamoy/mkdocstrings/badges/master/pipeline.svg)](https://gitlab.com/pawamoy/mkdocstrings/pipelines)
[![coverage report](https://gitlab.com/pawamoy/mkdocstrings/badges/master/coverage.svg)](https://gitlab.com/pawamoy/mkdocstrings/commits/master)
[![documentation](https://img.shields.io/badge/docs-latest-green.svg?style=flat)](https://pawamoy.github.io/mkdocstrings)
[![pypi version](https://img.shields.io/pypi/v/mkdocstrings.svg)](https://pypi.org/project/mkdocstrings/)

Automatic documentation from docstrings, for mkdocs.

This plugin is still in alpha status. Here is how it looks with the [mkdocs-material theme](https://squidfunk.github.io/mkdocs-material/) for now:

![mkdocstrings](https://user-images.githubusercontent.com/3999221/71327911-e467d000-250e-11ea-83e7-a81ec59f41e2.gif)

## Features
- **Works great with Material theme:** `mkdocstrings` was designed to work best with
  the great [Material theme](https://squidfunk.github.io/mkdocs-material/).
- **Support for type annotations:** `mkdocstrings` uses your type annotations to display parameters types
  or return types.
- **Recursive documentation of Python objects:** just write the module dotted-path, and you get the full module docs.
  No need to ask for each class, function, etc.
- **Support for documented attribute:** attributes (variables) followed by a docstring (triple-quoted string) will
  be recognized by `mkdocstrings`, in modules, classes and even in `__init__` methods.
- **Support for objects properties:** `mkdocstrings` will know if a method is a `staticmethod`, a `classmethod` or else,
  it will also know if a property is read-only or writable, and more! These properties will be displayed
  next to the object signature.
- **Every object has a TOC entry and a unique permalink:** the navigation is greatly improved! Click the anchor
  next to the object signature to get its permalink, which is its Python dotted-path.
- **Auto-reference other objects:** `mkdocstrings` makes it possible to reference other Python objects from your
  markdown files, and even from your docstrings, with the classic Markdown syntax:
  `[this object][package.module.object]` or directly with `[package.module.object][]`.
- **Google-style sections support in docstrings:** `mkdocstrings` understands `Arguments:`, `Raises:`
  and `Returns:` sections. It will even keep the section order in the generated docs.
- **Support for source code display:** `mkdocstrings` can add a collapsible div containing the source code of the
  Python object, directly below its signature, with the right line numbers.
- **Admonition support in docstrings:** blocks like `Note: ` or `Warning: ` will be transformed
  to their [admonition](https://squidfunk.github.io/mkdocs-material/extensions/admonition/) equivalent.
  *We do not support nested admonitions in docstrings!*
- **Sane defaults:** you should be able to just drop the plugin in your configuration and enjoy your auto-generated docs.
- **Configurable:** *(soon)* `mkdocstrings` is configurable globally, and per autodoc instruction.

To get an example of what is possible, check `mkdocstrings`'
own [documentation](https://pawamoy.github.io/mkdocstrings), generated with itself.

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

In one of your markdown files:

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

Add some style in `docs/custom.css`:

```css
div.autodoc {
  padding-left: 25px;
  border-left: 4px solid rgba(230, 230, 230);
}
```

And add it to your configuration:

```yaml
extra_css:
  - custom.css
```
