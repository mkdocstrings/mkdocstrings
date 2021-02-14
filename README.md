# mkdocstrings

[![ci](https://github.com/mkdocstrings/mkdocstrings/workflows/ci/badge.svg)](https://github.com/mkdocstrings/mkdocstrings/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://mkdocstrings.github.io/)
[![pypi version](https://img.shields.io/pypi/v/mkdocstrings.svg)](https://pypi.org/project/mkdocstrings/)
[![conda version](https://img.shields.io/conda/vn/conda-forge/mkdocstrings)](https://anaconda.org/conda-forge/mkdocstrings)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://gitter.im/mkdocstrings/community)

Automatic documentation from sources, for [MkDocs](https://mkdocs.org/).

---

![mkdocstrings_gif1](https://user-images.githubusercontent.com/3999221/77157604-fb807480-6aa1-11ea-99e0-d092371d4de0.gif)

---

- [Features](#features)
    - [Python handler features](#python-handler-features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick usage](#quick-usage)

## Features

- [**Language-agnostic:**](https://mkdocstrings.github.io/handlers/overview/)
  just like *MkDocs*, *mkdocstrings* is written in Python but is language-agnostic.
  It means you can use it with any programming language, as long as there is a
  [**handler**](https://mkdocstrings.github.io/reference/handlers/base/) for it.
  The [Python handler](https://mkdocstrings.github.io/handlers/python/) is built-in.
  [Others](https://mkdocstrings.github.io/handlers/overview/) are external.
  Maybe you'd like to add another one to the list? :wink:

- [**Multiple themes support:**](https://mkdocstrings.github.io/theming/)
  each handler can offer multiple themes. Currently, we offer the
  :star: [Material theme](https://squidfunk.github.io/mkdocs-material/) :star:
  as well as basic support for the ReadTheDocs theme for the Python handler.

- [**Cross-links across pages:**](https://mkdocstrings.github.io/usage/#cross-references)
  *mkdocstrings* makes it possible to reference headings in other Markdown files with the classic Markdown linking
  syntax: `[identifier][]` or `[title][identifier]` -- and you don't need to remember which exact page this object was
  on. This works for any heading that's produced by a *mkdocstrings* language handler, and you can opt to include
  *any* Markdown heading into the global referencing scheme.

    **Note**: in versions prior to 0.15 *all* Markdown headers were included, but now you need to
    [opt in](https://mkdocstrings.github.io/usage/#cross-references).

- [**Inline injection in Markdown:**](https://mkdocstrings.github.io/usage/)
  instead of generating Markdown files, *mkdocstrings* allows you to inject
  documentation anywhere in your Markdown contents. The syntax is simple: `::: identifier` followed by a 4-spaces
  indented YAML block. The identifier and YAML configuration will be passed to the appropriate handler
  to collect and render documentation.

- [**Global and local configuration:**](https://mkdocstrings.github.io/usage/#global-options)
  each handler can be configured globally in `mkdocs.yml`, and locally for each
  "autodoc" instruction.

- [**Watch source code directories:**](https://mkdocstrings.github.io/usage/#watch-directories)
  you can tell *mkdocstrings* to add directories to be watched by *MkDocs* when
  serving the documentation, for auto-reload.

- **Reasonable defaults:**
  you should be able to just drop the plugin in your configuration and enjoy your auto-generated docs.

### Python handler features

- **Data collection from source code**: collection of the object-tree and the docstrings is done by
  [`pytkdocs`](https://github.com/pawamoy/pytkdocs). The following features are possible thanks to it:
    - **Support for type annotations:** `pytkdocs` collects your type annotations and *mkdocstrings* uses them
      to display parameters types or return types.
    - **Recursive documentation of Python objects:** just use the module dotted-path as identifier, and you get the full
      module docs. You don't need to inject documentation for each class, function, etc.
    - **Support for documented attribute:** attributes (variables) followed by a docstring (triple-quoted string) will
      be recognized by `pytkdocs` in modules, classes and even in `__init__` methods.
    - **Support for objects properties:** `pytkdocs` detects if a method is a `staticmethod`, a `classmethod`, etc.,
      it also detects if a property is read-only or writable, and more! These properties will be displayed
      next to the object signature by *mkdocstrings*.
    - **Google-style sections support in docstrings:** `pytkdocs` understands `Arguments:`, `Raises:`
      and `Returns:` sections, and returns structured data for *mkdocstrings* to render them.
    - **reStructuredText-style sections support in docstrings:** `pytkdocs` understands all the
      [reStructuredText fields](https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html?highlight=python%20domain#info-field-lists),
      and returns structured data for *mkdocstrings* to render them.
      *Note: only RST **style** is supported, not the whole markup.*
    - **Admonition support in docstrings:** blocks like `Note: ` or `Warning: ` will be transformed
      to their [admonition](https://squidfunk.github.io/mkdocs-material/extensions/admonition/) equivalent.
      *We do not support nested admonitions in docstrings!*
    - **Support for reStructuredText in docstrings:** `pytkdocs` can parse simple RST.
- **Every object has a TOC entry:** we render a heading for each object, meaning *MkDocs* picks them into the Table
  of Contents, which is nicely display by the Material theme. Thanks to *mkdocstrings* cross-reference ability,
  you can even reference other objects within your docstrings, with the classic Markdown syntax:
  `[this object][package.module.object]` or directly with `[package.module.object][]`
- **Source code display:** *mkdocstrings* can add a collapsible div containing the highlighted source code
  of the Python object.

To get an example of what is possible, check *mkdocstrings*'
own [documentation](https://mkdocstrings.github.io/), auto-generated from sources by itself of course,
and the following GIF:

![mkdocstrings_gif2](https://user-images.githubusercontent.com/3999221/77157838-7184db80-6aa2-11ea-9f9a-fe77405202de.gif)

## Roadmap

See the [Feature Roadmap issue](https://github.com/mkdocstrings/mkdocstrings/issues/183) on the bugtracker.

## Requirements

*mkdocstrings* requires Python 3.6 or above.

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
pyenv install 3.6.12

# make it available globally
pyenv global system 3.6.12
```
</details>

This project currently only works with the Material theme of MkDocs.
Therefore, it is required that you have it installed.

```
pip install mkdocs-material
```

## Installation

With `pip`:
```bash
python3.6 -m pip install mkdocstrings
```

With `conda`:
```bash
conda install -c conda-forge mkdocstrings
```

## Quick usage

```yaml
# mkdocs.yml
theme:
  name: "material"

plugins:
- search
- mkdocstrings
```

In one of your markdown files:

```markdown
# Reference

::: my_library.my_module.my_class
```

See the [Usage](https://mkdocstrings.github.io/usage) section of the docs for more examples!
