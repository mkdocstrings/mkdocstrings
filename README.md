# mkdocstrings

[![ci](https://github.com/mkdocstrings/mkdocstrings/workflows/ci/badge.svg)](https://github.com/mkdocstrings/mkdocstrings/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://mkdocstrings.github.io/)
[![pypi version](https://img.shields.io/pypi/v/mkdocstrings.svg)](https://pypi.org/project/mkdocstrings/)
[![conda version](https://img.shields.io/conda/vn/conda-forge/mkdocstrings)](https://anaconda.org/conda-forge/mkdocstrings)
[![gitpod](https://img.shields.io/badge/gitpod-workspace-blue.svg?style=flat)](https://gitpod.io/#https://github.com/mkdocstrings/mkdocstrings)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://gitter.im/mkdocstrings/community)

Automatic documentation from sources, for [MkDocs](https://mkdocs.org/).
Come have a chat or ask questions on our [Gitter channel](https://gitter.im/mkdocstrings/community).

---

**[Features](#features)** - **[Requirements](#requirements)** - **[Installation](#installation)** - **[Quick usage](#quick-usage)**

![mkdocstrings_gif1](https://user-images.githubusercontent.com/3999221/77157604-fb807480-6aa1-11ea-99e0-d092371d4de0.gif)

## Features

- [**Language-agnostic:**](https://mkdocstrings.github.io/handlers/overview/)
  just like *MkDocs*, *mkdocstrings* is written in Python but is language-agnostic.
  It means you can use it with any programming language, as long as there is a
  [**handler**](https://mkdocstrings.github.io/reference/handlers/base/) for it.
  We currently have [handlers](https://mkdocstrings.github.io/handlers/overview/)
  for the [Crystal](https://mkdocstrings.github.io/crystal/) and [Python](https://mkdocstrings.github.io/python/) languages.
  Maybe you'd like to add another one to the list? :wink:

- [**Multiple themes support:**](https://mkdocstrings.github.io/theming/)
  each handler can offer multiple themes. Currently, we offer the
  :star: [Material theme](https://squidfunk.github.io/mkdocs-material/) :star:
  as well as basic support for the ReadTheDocs and MkDocs themes for the Python handler.

- [**Cross-references across pages:**](https://mkdocstrings.github.io/usage/#cross-references)
  *mkdocstrings* makes it possible to reference headings in other Markdown files with the classic Markdown linking
  syntax: `[identifier][]` or `[title][identifier]` -- and you don't need to remember which exact page this object was
  on. This works for any heading that's produced by a *mkdocstrings* language handler, and you can opt to include
  *any* Markdown heading into the global referencing scheme.

    **Note**: in versions prior to 0.15 *all* Markdown headers were included, but now you need to
    [opt in](https://mkdocstrings.github.io/usage/#cross-references-to-any-markdown-heading).

- [**Cross-references across sites:**](https://mkdocstrings.github.io/usage/#cross-references-to-other-projects-inventories)
  similarly to [Sphinx's intersphinx extension](https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html),
  *mkdocstrings* can reference API items from other libraries, given they provide an inventory and you load
  that inventory in your MkDocs configuration.

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

## Installation

With `pip`:
```bash
pip install mkdocstrings
```

You can install support for specific languages using extras, for example:

```bash
pip install 'mkdocstrings[crystal,python]'
```

See the [available language handlers](https://mkdocstrings.github.io/handlers/overview/).

With `conda`:
```bash
conda install -c conda-forge mkdocstrings
```

## Quick usage

In `mkdocs.yml`:

```yaml
site_name: "My Library"

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
