# Handlers

A handler is what makes it possible to collect and render documentation for a particular language.

## Available handlers

- [Python](../python)

## Custom handlers

Since version 0.14, you can create and use custom handlers
thanks to namespace packages. For more information about namespace packages,
[see their documentation](https://packaging.python.org/guides/packaging-namespace-packages/).

### Packaging

For MkDocstrings, a custom handler package would have the following structure:

```
📁 your_repository
└── 📁 mkdocstrings
    └── 📁 handlers
        └── 📄 custom_handler.py
```

Or with a `src` layout:

```
📁 your_repository
└── 📁 src
    └── 📁 mkdocstrings
        └── 📁 handlers
            └── 📄 custom_handler.py
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

### Usage

When a custom handler is installed,
it is then available to MkDocstrings.
You can configure it as usual:

```yaml
# mkdocs.yml
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
