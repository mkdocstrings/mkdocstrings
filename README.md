# mkdocstrings

[![ci](https://github.com/mkdocstrings/mkdocstrings/workflows/ci/badge.svg)](https://github.com/mkdocstrings/mkdocstrings/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://mkdocstrings.github.io/)
[![pypi version](https://img.shields.io/pypi/v/mkdocstrings.svg)](https://pypi.org/project/mkdocstrings/)
[![conda version](https://img.shields.io/conda/vn/conda-forge/mkdocstrings)](https://anaconda.org/conda-forge/mkdocstrings)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://app.gitter.im/#/room/#mkdocstrings:gitter.im)

Automatic documentation from sources, for [MkDocs](https://www.mkdocs.org/).
Come have a chat or ask questions on our [Gitter channel](https://gitter.im/mkdocstrings/community).

---

**[Features](#features)** - **[Installation](#installation)** - **[Quick usage](#quick-usage)**

![mkdocstrings_gif1](https://user-images.githubusercontent.com/3999221/77157604-fb807480-6aa1-11ea-99e0-d092371d4de0.gif)

## Features

- [**Language-agnostic:**](https://mkdocstrings.github.io/handlers/overview/)
  just like *MkDocs*, *mkdocstrings* is written in Python but is language-agnostic.
  It means you can use it with any programming language, as long as there is a
  [**handler**](https://mkdocstrings.github.io/reference/handlers/base/) for it.
  We currently have [handlers](https://mkdocstrings.github.io/handlers/overview/) for the
  [C](https://mkdocstrings.github.io/c/),
  [Crystal](https://mkdocstrings.github.io/crystal/),
  [Python](https://mkdocstrings.github.io/python/),
  [TypeScript](https://mkdocstrings.github.io/typescript/), and
  [VBA](https://pypi.org/project/mkdocstrings-vba/) languages,
  as well as for [shell scripts/libraries](https://mkdocstrings.github.io/shell/).
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

- **Reasonable defaults:**
  you should be able to just drop the plugin in your configuration and enjoy your auto-generated docs.

## Used by

*mkdocstrings* is used by well-known companies, projects and scientific teams:
[Ansible](https://molecule.readthedocs.io/configuration/),
[Apache](https://streampipes.apache.org/docs/docs/python/latest/reference/client/client/),
[FastAPI](https://fastapi.tiangolo.com/reference/fastapi/),
[Google](https://docs.kidger.site/jaxtyping/api/runtime-type-checking/),
[IBM](https://ds4sd.github.io/docling/api_reference/document_converter/),
[Jitsi](https://jitsi.github.io/jiwer/reference/alignment/),
[Microsoft](https://microsoft.github.io/presidio/api/analyzer_python/),
[NVIDIA](https://nvidia.github.io/bionemo-framework/API_reference/bionemo/core/api/),
[Prefect](https://docs.prefect.io/2.10.12/api-ref/prefect/agent/),
[Pydantic](https://docs.pydantic.dev/dev-v2/api/main/),
[Textual](https://textual.textualize.io/api/app/),
[and more...](https://github.com/mkdocstrings/mkdocstrings/network/dependents)

## Installation

The `mkdocstrings` package doesn't provide support for any language: it's just a common base for language handlers.
It means you likely want to install it with one or more official handlers, using [extras](https://packaging.python.org/en/latest/specifications/dependency-specifiers/#extras).
For example, to install it with Python support:

```bash
pip install 'mkdocstrings[python]'
```

Alternatively, you can directly install the language handlers themselves,
which depend on `mkdocstrings` anyway:

```bash
pip install mkdocstrings-python
```

This will give you more control over the accepted range of versions for the handlers themselves.

See the [official language handlers](https://mkdocstrings.github.io/handlers/overview/).

---

With `conda`:

```bash
conda install -c conda-forge mkdocstrings mkdocstrings-python
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
