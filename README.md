# mkdocstrings

[![ci](https://github.com/mkdocstrings/mkdocstrings/workflows/ci/badge.svg)](https://github.com/mkdocstrings/mkdocstrings/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://mkdocstrings.github.io/)
[![pypi version](https://img.shields.io/pypi/v/mkdocstrings.svg)](https://pypi.org/project/mkdocstrings/)
[![conda version](https://img.shields.io/conda/vn/conda-forge/mkdocstrings)](https://anaconda.org/conda-forge/mkdocstrings)
[![gitter](https://img.shields.io/badge/matrix-chat-4DB798.svg?style=flat)](https://app.gitter.im/#/room/#mkdocstrings:gitter.im)

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
  [GitHub Actions](https://watermarkhu.nl/mkdocstrings-github/),
  [Python](https://mkdocstrings.github.io/python/),
  [MATLAB](https://watermarkhu.nl/mkdocstrings-matlab/),
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
[NVIDIA](https://nvidia.github.io/bionemo-framework/main/references/API_reference/bionemo/core/api/),
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

## Sponsors

<!-- sponsors-start -->

<div id="premium-sponsors" style="text-align: center;">

<div id="silver-sponsors"><b>Silver sponsors</b><p>
<a href="https://fastapi.tiangolo.com/"><img alt="FastAPI" src="https://raw.githubusercontent.com/tiangolo/fastapi/master/docs/en/docs/img/logo-margin/logo-teal.png" style="height: 200px; "></a><br>
<a href="https://docs.pydantic.dev/latest/"><img alt="Pydantic" src="https://pydantic.dev/assets/for-external/pydantic_logfire_logo_endorsed_lithium_rgb.svg" style="height: 180px; "></a><br>
</p></div>

<div id="bronze-sponsors"><b>Bronze sponsors</b><p>
<a href="https://www.nixtla.io/"><picture><source media="(prefers-color-scheme: light)" srcset="https://www.nixtla.io/img/logo/full-black.svg"><source media="(prefers-color-scheme: dark)" srcset="https://www.nixtla.io/img/logo/full-white.svg"><img alt="Nixtla" src="https://www.nixtla.io/img/logo/full-black.svg" style="height: 60px; "></picture></a><br>
</p></div>
</div>

---

<div id="sponsors"><p>
<a href="https://github.com/ofek"><img alt="ofek" src="https://avatars.githubusercontent.com/u/9677399?u=386c330f212ce467ce7119d9615c75d0e9b9f1ce&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/samuelcolvin"><img alt="samuelcolvin" src="https://avatars.githubusercontent.com/u/4039449?u=42eb3b833047c8c4b4f647a031eaef148c16d93f&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/tlambert03"><img alt="tlambert03" src="https://avatars.githubusercontent.com/u/1609449?u=922abf0524b47739b37095e553c99488814b05db&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/ssbarnea"><img alt="ssbarnea" src="https://avatars.githubusercontent.com/u/102495?u=c7bd9ddf127785286fc939dd18cb02db0a453bce&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/femtomc"><img alt="femtomc" src="https://avatars.githubusercontent.com/u/34410036?u=f13a71daf2a9f0d2da189beaa94250daa629e2d8&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/cmarqu"><img alt="cmarqu" src="https://avatars.githubusercontent.com/u/360986?v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/kolenaIO"><img alt="kolenaIO" src="https://avatars.githubusercontent.com/u/77010818?v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/ramnes"><img alt="ramnes" src="https://avatars.githubusercontent.com/u/835072?u=3fca03c3ba0051e2eb652b1def2188a94d1e1dc2&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/machow"><img alt="machow" src="https://avatars.githubusercontent.com/u/2574498?u=c41e3d2f758a05102d8075e38d67b9c17d4189d7&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/BenHammersley"><img alt="BenHammersley" src="https://avatars.githubusercontent.com/u/99436?u=4499a7b507541045222ee28ae122dbe3c8d08ab5&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/trevorWieland"><img alt="trevorWieland" src="https://avatars.githubusercontent.com/u/28811461?u=74cc0e3756c1d4e3d66b5c396e1d131ea8a10472&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/MarcoGorelli"><img alt="MarcoGorelli" src="https://avatars.githubusercontent.com/u/33491632?u=7de3a749cac76a60baca9777baf71d043a4f884d&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/analog-cbarber"><img alt="analog-cbarber" src="https://avatars.githubusercontent.com/u/7408243?u=642fc2bdcc9904089c62fe5aec4e03ace32da67d&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/OdinManiac"><img alt="OdinManiac" src="https://avatars.githubusercontent.com/u/22727172?u=36ab20970f7f52ae8e7eb67b7fcf491fee01ac22&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/rstudio-sponsorship"><img alt="rstudio-sponsorship" src="https://avatars.githubusercontent.com/u/58949051?u=0c471515dd18111be30dfb7669ed5e778970959b&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/schlich"><img alt="schlich" src="https://avatars.githubusercontent.com/u/21191435?u=6f1240adb68f21614d809ae52d66509f46b1e877&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/butterlyn"><img alt="butterlyn" src="https://avatars.githubusercontent.com/u/53323535?v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/livingbio"><img alt="livingbio" src="https://avatars.githubusercontent.com/u/10329983?v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/NemetschekAllplan"><img alt="NemetschekAllplan" src="https://avatars.githubusercontent.com/u/912034?v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/EricJayHartman"><img alt="EricJayHartman" src="https://avatars.githubusercontent.com/u/9259499?u=7e58cc7ec0cd3e85b27aec33656aa0f6612706dd&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/15r10nk"><img alt="15r10nk" src="https://avatars.githubusercontent.com/u/44680962?u=f04826446ff165742efa81e314bd03bf1724d50e&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/activeloopai"><img alt="activeloopai" src="https://avatars.githubusercontent.com/u/34816118?v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/roboflow"><img alt="roboflow" src="https://avatars.githubusercontent.com/u/53104118?v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/cmclaughlin"><img alt="cmclaughlin" src="https://avatars.githubusercontent.com/u/1061109?u=ddf6eec0edd2d11c980f8c3aa96e3d044d4e0468&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/blaisep"><img alt="blaisep" src="https://avatars.githubusercontent.com/u/254456?u=97d584b7c0a6faf583aa59975df4f993f671d121&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/RapidataAI"><img alt="RapidataAI" src="https://avatars.githubusercontent.com/u/104209891?v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/rodolphebarbanneau"><img alt="rodolphebarbanneau" src="https://avatars.githubusercontent.com/u/46493454?u=6c405452a40c231cdf0b68e97544e07ee956a733&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/theSymbolSyndicate"><img alt="theSymbolSyndicate" src="https://avatars.githubusercontent.com/u/111542255?v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/blakeNaccarato"><img alt="blakeNaccarato" src="https://avatars.githubusercontent.com/u/20692450?u=bb919218be30cfa994514f4cf39bb2f7cf952df4&v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/ChargeStorm"><img alt="ChargeStorm" src="https://avatars.githubusercontent.com/u/26000165?v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/Alphadelta14"><img alt="Alphadelta14" src="https://avatars.githubusercontent.com/u/480845?v=4" style="height: 32px; border-radius: 100%;"></a>
<a href="https://github.com/Cusp-AI"><img alt="Cusp-AI" src="https://avatars.githubusercontent.com/u/178170649?v=4" style="height: 32px; border-radius: 100%;"></a>
</p></div>


*And 7 more private sponsor(s).*

<!-- sponsors-end -->
