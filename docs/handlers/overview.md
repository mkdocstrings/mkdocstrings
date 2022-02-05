# Handlers

A handler is what makes it possible to collect and render documentation for a particular language.

## Available handlers

- <a class="external" href="https://mkdocstrings.github.io/python/">Python</a>
- <a class="external" href="https://mkdocstrings.github.io/crystal/">Crystal</a>

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
