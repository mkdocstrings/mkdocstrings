# Handlers

A handler is what makes it possible to collect and render documentation for a particular language.

## Available handlers

- <a class="external" href="https://mkdocstrings.github.io/crystal/">Crystal</a>
- <a class="external" href="https://mkdocstrings.github.io/python/">Python</a>
- <a class="external" href="https://mkdocstrings.github.io/python-legacy/">Python (Legacy)</a>

## About the Python handlers

Since version 0.18, a new, experimental Python handler is available.
It is based on [Griffe](https://github.com/mkdocstrings/griffe),
which is an improved version of [pytkdocs](https://github.com/mkdocstrings/pytkdocs).

Note that the experimental handler does not yet support third-party libraries
like Django, Marshmallow, Pydantic, etc.
It is also not completely ready to handle dynamically built objects,
like classes built with a call to `type(...)`.
For most other cases, the experimental handler will work just fine.

If you want to keep using the legacy handler as long as possible,
you can depend on `mkdocstrings-python-legacy` directly,
or specify the `python-legacy` extra when depending on *mkdocstrings*:

```toml title="pyproject.toml"
# PEP 621 dependencies declaration
# adapt to your dependencies manager
[project]
dependencies = [
    "mkdocstrings[python-legacy]>=0.18",
]
```

The legacy handler will continue to "work" for many releases,
as long as the new handler does not cover all previous use-cases.

### Migrate to the experimental Python handler

To use the new, experimental Python handler,
you can depend on `mkdocstrings-python` directly,
or specify the `python` extra when depending on *mkdocstrings*:

```toml title="pyproject.toml"
# PEP 621 dependencies declaration
# adapt to your dependencies manager
[project]
dependencies = [
    "mkdocstrings[python]>=0.18",
]
```

#### Handler options

- `setup_commands` is not yet implemented. In most cases, you won't need it,
  since by default the new handler does not execute the code.

#### Selection options

WARNING: Since *mkdocstrings* 0.19, the YAML `selection` key is merged into the `options` key.

- [x] `filters` is implemented, and used as before.
- [x] `members` is implemented, and used as before.
- [ ] `inherited_members` is not yet implemented.
- [x] `docstring_style` is implemented, and used as before,
  except for the `restructured-text` style which is renamed `sphinx`.
  Numpy-style is now built-in, so you can stop depending on `pytkdocs[numpy-style]`
  or `docstring_parser`.
- [x] `docstring_options` is implemented, and used as before.
  Refer to the [`griffe` documentation](https://mkdocstrings.github.io/griffe/docstrings/#parsing-options)
  for the updated list of supported docstring options.
- [x] `new_path_syntax` is irrelevant now. If you were setting it to True,
  remove the option and replace every colon (`:`) in your autodoc identifiers
  by dots (`.`).

See [all the handler's options](https://mkdocstrings.github.io/python/usage/).

#### Rendering options

WARNING: Since *mkdocstrings* 0.19, the YAML `rendering` key is merged into the `options` key.

Every previous option is supported.
Additional options are available:

- `separate_signature`: Render the signature (or attribute value) in a code block below the heading,
  instead as inline code. Useful for long signatures. If Black is installed,
  the signature is formatted. Default: `False`.
- `line_length`: The maximum line length to use when formatting signatures. Default: `60`.
- `show_submodules`: Whether to render submodules of a module when iterating on children.
  Default: `False`.
- `docstring_section_style`: The style to use to render docstring sections such as attributes,
  parameters, etc. Available styles: `table` (default), `list` and `spacy`. The SpaCy style
  is a poor implementation of their [table style](https://spacy.io/api/doc/#init).
  We are open to improvements through PRs!

See [all the handler's options](https://mkdocstrings.github.io/python/usage/).

#### Templates

Templates are mostly the same as before, but the file layout has changed,
as well as some file names. Here is the new tree:

```
📁 theme/
├── 📄 attribute.html
├── 📄 children.html
├── 📄 class.html
├── 📁 docstring/
│   ├── 📄 admonition.html
│   ├── 📄 attributes.html
│   ├── 📄 examples.html
│   ├── 📄 other_parameters.html
│   ├── 📄 parameters.html
│   ├── 📄 raises.html
│   ├── 📄 receives.html
│   ├── 📄 returns.html
│   ├── 📄 warns.html
│   └── 📄 yields.html
├── 📄 docstring.html
├── 📄 expression.html
├── 📄 function.html
├── 📄 labels.html
├── 📄 module.html
└── 📄 signature.html
```

See them [in the handler repository](https://github.com/mkdocstrings/python/tree/8fc8ea5b112627958968823ef500cfa46b63613e/src/mkdocstrings_handlers/python/templates/material). See the documentation about the Python handler templates:
https://mkdocstrings.github.io/python/customization/#templates.

## Custom handlers

Since version 0.14, you can create and use custom handlers
thanks to namespace packages. For more information about namespace packages,
[see their documentation](https://packaging.python.org/guides/packaging-namespace-packages/).

TIP: **TL;DR - Project template for handlers.**  
*mkdocstrings* provides a [Copier](https://github.com/copier-org/copier) template to kickstart
new handlers: https://github.com/mkdocstrings/handler-template. To use it, install Copier
(`pipx install copier`), then run `copier gh:mkdocstrings/handler-template my_handler`
to generate a new project. See [its upstream documentation](https://pawamoy.github.io/copier-pdm/)
to learn how to work on the generated project.

### Packaging

For *mkdocstrings*, a custom handler package would have the following structure:

```
📁 your_repository
└─╴📁 mkdocstrings_handlers
   └─╴📁 custom_handler
      ├─╴📁 templates
      │  ├─╴📁 material
      │  ├─╴📁 mkdocs
      │  └─╴📁 readthedocs
      └─╴📄 __init__.py
```

NOTE: **Note the absence of `__init__.py` module in `mkdocstrings_handlers`!**

### Code

A handler is a subclass of the base handler provided by *mkdocstrings*.

See the documentation for the [`BaseHandler`][mkdocstrings.handlers.base.BaseHandler].
Subclasses of the base handler must implement the `collect` and `render` methods at least.
The `collect` method is responsible for collecting and returning data (extracting
documentation from source code, loading introspecting objects in memory, other sources? etc.)
while the `render` method is responsible for actually rendering the data to HTML,
using the Jinja templates provided by your package.

You must implement a `get_handler` method at the module level.
This function takes the following parameters:

- `theme` (string, theme name)
- `custom_templates` (optional string, path to custom templates directory)
- `config_file_path` (optional string, path to the config file)

These arguments are all passed as keyword arguments, so you can ignore them
by adding `**kwargs` or similar to your signature. You can also accept
additional parameters: the handler's global-only options and/or the root
config options. This gives flexibility and access to the mkdocs config, mkdocstring
config etc.. You should never modify the root config but can use it to get
information about the MkDocs instance such as where the current `site_dir` lives.
See the [Mkdocs Configuration](https://www.mkdocs.org/user-guide/configuration/) for
more info about what is accessible from it.

Check out how the
[Python handler](https://github.com/mkdocstrings/python/blob/master/src/mkdocstrings_handlers/python)
is written for inspiration.

### Templates

Your handler's implementation should normally be backed by templates, which go
to the directory `mkdocstrings_handlers/custom_handler/templates/some_theme`
(`custom_handler` here should be replaced with the actual name of your handler,
and `some_theme` should be the name of an actual MkDocs theme that you support,
e.g. `material`).

With that structure, you can use `self.env.get_template("foo.html")` inside
your `render` method. This already chooses the subdirectory based on
the current MkDocs theme.

If you wish to support *any* MkDocs theme, rather than a few specifically
selected ones, you can pick one theme's subdirectory to be the fallback for
when an unknown theme is encountered. Then you just need to set the
`fallback_theme` variable on your handler subclass. The fallback directory can
be used even for themes you explicitly support: you can omit some template from
one of the other theme directories in case they're exactly the same as in the
fallback theme.

If your theme's HTML requires CSS to go along with it, put it into a file named
`mkdocstrings_handlers/custom_handler/templates/some_theme/style.css`, then this will be
included into the final site automatically if this handler is ever used.
Alternatively, you can put the CSS as a string into the `extra_css` variable of
your renderer.

Finally, it's possible to entirely omit templates, and tell *mkdocstrings*
to use the templates of another handler. In you handler, override the
`get_templates_dir()` method to return the other handlers templates path:

```python
from pathlib import Path
from mkdocstrings.handlers.base import BaseHandler


class CobraHandler(BaseHandler):
    def get_templates_dir(self, handler: str) -> Path:
        # use the python handler templates
        # (it assumes the python handler is installed)
        return super().get_templates_dir("python")
```

### Usage

When a custom handler is installed, it is then available to *mkdocstrings*.
You can configure it as usual:

```yaml title="mkdocs.yml"
plugins:
- mkdocstrings:
    handlers:
      custom_handler:
        handler_config_option: yes
        options:
          some_config_option: "a"
          other_config_option: 0
```

...and use it in your autodoc instructions:

```md title="docs/some_page.md"
# Documentation for an object

::: some.objects.path
    handler: custom_handler
    options:
      some_config_option: "b"
      other_config_option: 1
```

## Handler extensions

*mkdocstrings* provides a way for third-party packages
to extend or alter the behavior of handlers.
For example, an extension of the Python handler
could add specific support for another Python library.

NOTE: This feature is intended for developers.
If you are a user and want to customize how objects are rendered,
see [Theming / Customization](../theming/#customization).

Such extensions can register additional template folders
that will be used when rendering collected data.
Extensions are responsible for synchronizing
with the handler itself so that it uses the additional templates.

An extension is a Python package
that defines an entry-point for a specific handler:

```toml title="pyproject.toml"
[project.entry-points."mkdocstrings.python.templates"] # (1)!
extension-name = "extension_package:get_templates_path" # (2)!
```

1. Replace `python` by the name of the handler you want to add templates to.
1. Replace `extension-name` by any name you want,
    and replace `extension_package:get_templates_path`
    by the actual module path and function name in your package.

This entry-point assumes that the extension provides
a `get_templates_path` function directly under the `extension_package` package:

```tree
pyproject.toml
extension_package/
    __init__.py
    templates/
```

```python title="extension_package/__init__.py"
from pathlib import Path


def get_templates_path() -> Path:
    return Path(__file__).parent / "templates"
```

This function doesn't accept any argument
and returns the path ([`pathlib.Path`][] or [`str`][])
to a directory containing templates.
The directory must contain one subfolder
for each supported theme, even if empty
(see "fallback theme" in [custom handlers templates](#templates_1)).
For example:

```tree
pyproject.toml
extension_package/
    __init__.py
    templates/
        material/
        readthedocs/
        mkdocs/
```

*mkdocstrings* will add the folders corresponding to the user-selected theme,
and to the handler's defined fallback theme, as usual.

The names of the extension templates
must not overlap with the handler's original templates.

The extension is then responsible, in collaboration with its target handler,
for mutating the collected data in order to instruct the handler
to use one of the extension template when rendering particular objects.
See each handler's docs to see if they support extensions, and how.
