# Handlers

A handler is what makes it possible to collect and render documentation for a particular language.

## Available handlers

- <a class="external" href="https://mkdocstrings.github.io/crystal/">Crystal</a>
- <a class="external" href="https://mkdocstrings.github.io/python-legacy/">Python (Legacy)</a>
- <a class="external" href="https://mkdocstrings.github.io/python/">Python (Experimental)</a>

## About the Python handlers

Since version 0.18, a new, experimental Python handler is available.
It is based on [Griffe](https://github.com/mkdocstrings/griffe),
which is an improved version of [pytkdocs](https://github.com/mkdocstrings/pytkdocs).

Note that the experimental handler does not yet offer the same features as the legacy one.
If you are making extensive use of the current (legacy) Python handler selection and rendering options,
you might want to wait a bit before trying the experimental handler.
It is also not completely ready to handle dynamically built objects,
like classes built with a call to `type(...)`.
For most other cases, the experimental handler will work just fine.

If you want to keep using the legacy handler as long as possible,
you can already specify the `python-legacy` extra when depending on *mkdocstrings*:

```toml
# PEP 621 dependencies declaration
# adapt to your dependencies manager
[project]
dependencies = [
    "mkdocstrings[python-legacy]>=0.18",
]
```

The legacy handler will keep "working" for many releases,
as long as the new handler does not cover all previous use-cases.

Using the legacy handler will emit Python warnings:

- a `DeprecationWarning` from *mkdocstrings* because the legacy
  handler is loaded from a deprecated namespace package, `mkdocstrings.handlers`.
  The warning will disappear once we migrate it to the new namespace, `mkdocstrings_handlers`.
- another `DeprecationWarning` from *mkdocstrings* because the legacy
  handler templates are loaded from a deprecated namespace as well, `mkdocstrings.templates`.
  The warning will disappear once we migrate the templates inside the handler's package.
- a `UserWarning` from the legacy handler itself, stating that users
  should specify the `python-legacy` extra when depending on *mkdocstrings*.
  The warning will be emitted even if you do specify the extra, as we have
  no way to detect it.

Warnings can be globally ignored by setting the
[`PYTHONWARNINGS` environment variable](https://docs.python.org/3/library/warnings.html#describing-warning-filters):

```bash
PYTHONWARNINGS=\
ignore::DeprecationWarning:mkdocstrings.handlers.base,\
ignore::DeprecationWarning:mkdocstrings.handlers.base,\
ignore::UserWarning:mkdocstrings.handlers.python
```

### Migrate to the experimental Python handler

To use the new, experimental Python handler,
you must specify the `python` extra when depending on *mkdocstrings*:

```toml
# PEP 621 dependencies declaration
# adapt to your dependencies manager
[project]
dependencies = [
    "mkdocstrings[python]>=0.18",
]
```

#### Handler options

- `setup_commands` is not yet implemented. But in most cases, you won't need it,
  since by default the new handler does not execute the code.

#### Selection options

- `filters` is not yet implemented. *Every* declared object is picked up by default,
  but only rendered if it has a docstring. Since code is not executed,
  inherited attributes (like special methods and private members) are not picked up.
- `members` is not yet implemented.
- `inherited_members` is not yet implemented.
- `docstring_style` is implemented, and used as before,
  except for the `restructured-text` style which is renamed `sphinx`.
  Numpy-style is now built-in, so you can stop depending on `pytkdocs[numpy-style]`
  or `docstring_parser`.
- `docstring_options` is implemented, and used as before, however none
  of the provided parsers accept any option yet.
- `new_path_syntax` is irrelevant now. If you were setting it to True,
  remove the option and replace every colon (`:`) in your autodoc identifiers
  by dots (`.`).

#### Rendering options

Every previous option is supported.
Additional options are available:

- `separate_signature`: Render the signature in a code block below the heading,
  instead as inline code. Useful for long signatures. If Black is installed,
  the signature is formatted. Default: false.
- `line_length`: The maximum line length to use when formatting signatures. Default: 60.
- `show_submodules`: Whether to render submodules of a module when iterating on children.
  Default: true.
- `docstring_section_style`: The style to use to render docstring sections such as attributes,
  parameters, etc. Available styles: `table` (default), `list` and `spacy`. The SpaCy style
  is a poor implementation of their [table style](https://spacy.io/api/doc/#init).
  We are open to improvements through PRs!

#### Templates

Templates are mostly the same as before, but the file layout has changed,
as well as some file names. Here is the new tree:

```
theme
├── attribute.html
├── children.html
├── class.html
├── docstring
│   ├── admonition.html
│   ├── attributes.html
│   ├── examples.html
│   ├── other_parameters.html
│   ├── parameters.html
│   ├── raises.html
│   ├── receives.html
│   ├── returns.html
│   ├── warns.html
│   └── yields.html
├── docstring.html
├── expression.html
├── function.html
├── labels.html
├── module.html
└── signature.html
```

See them [in the handler repository](https://github.com/mkdocstrings/python/tree/8fc8ea5b112627958968823ef500cfa46b63613e/src/mkdocstrings_handlers/python/templates/material).

In preparation for Jinja2 blocks, which will improve customization,
each one of these templates extends in fact a base version in `theme/_base`. Example:

```html+jinja title="theme/docstring/admonition.html"
{% extends "_base/docstring/admonition.html" %}
```

```html+jinja title="theme/_base/docstring/admonition.html"
{{ log.debug() }}
<details class="{{ section.value.kind }}">
  <summary>{{ section.title|convert_markdown(heading_level, html_id, strip_paragraph=True) }}</summary>
  {{ section.value.contents|convert_markdown(heading_level, html_id) }}
</details>
```

It means you will be able to customize only *parts* of a template
without having to fully copy-paste it in your project:

```jinja title="templates/theme/docstring.html"
{% extends "_base/docstring.html" %}
{% block contents %}
  {{ block.super }}
  Additional contents
{% endblock contents %}
```

**Block-level customization is not ready yet.**

## Custom handlers

Since version 0.14, you can create and use custom handlers
thanks to namespace packages. For more information about namespace packages,
[see their documentation](https://packaging.python.org/guides/packaging-namespace-packages/).

### Packaging

For *mkdocstrings*, a custom handler package would have the following structure:

```
📁 your_repository
└─╴📁 mkdocstrings
   └─╴📁 handlers
      └─╴📄 custom_handler.py
```

**Note the absence of `__init__.py` modules!**

If you name you handler after an existing handler,
it will overwrite it!
For example, it means you can overwrite the Python handler
to change how it works or to add functionality,
by naming your handler module `python.py`.

### Code

A handler is composed of a Collector and a Renderer.

See the documentation for
[`BaseHandler`][mkdocstrings.handlers.base.BaseHandler],
[`BaseCollector`][mkdocstrings.handlers.base.BaseCollector] and
[`BaseRenderer`][mkdocstrings.handlers.base.BaseRenderer].

Check out how the
[Python handler](https://github.com/pawamoy/mkdocstrings/blob/master/src/mkdocstrings/handlers/python.py)
is written for inspiration.

You must implement a `get_handler` method at the module level.
This function takes the `theme` (string, theme name) and
`custom_templates` (optional string, path to custom templates directory)
arguments, and you can add any other keyword argument you'd like.
The global configuration items (other than `selection` and `rendering`)
will be passed to this function when getting your handler.

### Templates

You renderer's implementation should normally be backed by templates, which go
to the directory `mkdocstrings/handlers/custom_handler/some_theme`.
(`custom_handler` here should be replaced with the actual name of your handler,
and `some_theme` should be the name of an actual MkDocs theme that you support,
e.g. `material`).

With that structure, you can use `self.env.get_template("foo.html")` inside
your `render` implementation. This already chooses the subdirectory based on
the current MkDocs theme.

If you wish to support *any* MkDocs theme, rather than a few specifically
selected ones, you can pick one theme's subdirectory to be the fallback for
when an unknown theme is encountered. Then you just need to set the
`fallback_theme` variable on your renderer subclass. The fallback directory can
be used even for themes you explicitly support: you can omit some template from
one of the other theme directories in case they're exactly the same as in the
fallback theme.

If your theme's HTML requires CSS to go along with it, put it into a file named
`mkdocstrings/handlers/custom_handler/some_theme/style.css`, then this will be
included into the final site automatically if this handler is ever used.
Alternatively, you can put the CSS as a string into the `extra_css` variable of
your renderer.

### Usage

When a custom handler is installed, it is then available to *mkdocstrings*.
You can configure it as usual:

!!! example "mkdocs.yml"
    ```yaml
    plugins:
    - mkdocstrings:
        handlers:
          custom_handler:
            selection:
              some_config_option: "a"
            rendering:
              other_config_option: 0
            handler_config_option: yes
    ```

...and use it in your autodoc instructions:

```markdown
# Documentation for an object

::: some.objects.path
    handler: custom_handler
    selection:
      some_config_option: "b"
    rendering:
      other_config_option: 1
```
