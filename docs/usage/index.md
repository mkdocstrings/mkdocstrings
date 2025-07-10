# Usage

## Autodoc syntax

*mkdocstrings* works by processing special expressions in your Markdown files.

The syntax is as follows:

```md
::: identifier
    YAML block
```

> NOTE: **Resources on YAML.**
> YAML can sometimes be a bit tricky, particularly on indentation.
> Here are some resources that other users found useful to better
> understand YAML's peculiarities.
>
> - [YAML idiosyncrasies](https://salt-zh.readthedocs.io/en/latest/topics/troubleshooting/yaml_idiosyncrasies.html)
> - [YAML multiline](https://yaml-multiline.info/)

The `identifier` is a string identifying the object you want to document.
The format of an identifier can vary from one handler to another.
For example, the Python handler expects the full dotted-path to a Python object:
`my_package.my_module.MyClass.my_method`.

The YAML block is optional, and contains some configuration options:

- `handler`: the name of the handler to use to collect and render this object.
  By default, it will use the value defined in the [Global options](#global-options)'s
  `default_handler` key, or `"python"`.
- `options`: a dictionary of options passed to the handler's methods responsible both
  for collecting and rendering the documentation. These options can be defined
  globally (in `mkdocs.yml`, see [Global options](#global-options)),
  locally (as described here), or both.

!!! example "Example with the Python handler"
    === "docs/my_page.md"
        ```md
        # Documentation for `MyClass`

        ::: my_package.my_module.MyClass
            handler: python
            options:
              members:
                - method_a
                - method_b
              show_root_heading: false
              show_source: false
        ```

    === "mkdocs.yml"
        ```yaml
        nav:
          - "My page": my_page.md
        ```

    === "src/my_package/my_module.py"
        ```python
        class MyClass:
            """Print print print!"""

            def method_a(self):
                """Print A!"""
                print("A!")

            def method_b(self):
                """Print B!"""
                print("B!")

            def method_c(self):
                """Print C!"""
                print("C!")
        ```

    === "Result"
        <h3 id="documentation-for-myclass" style="margin: 0;">Documentation for <code>MyClass</code></h3>
        <div><div><p>Print print print!</p><div><div>
        <h4 id="mkdocstrings.my_module.MyClass.method_a">
        <code class="highlight language-python">
        method_a<span class="p">(</span><span class="bp">self</span><span class="p">)</span> </code>
        </h4><div>
        <p>Print A!</p></div></div><div><h4 id="mkdocstrings.my_module.MyClass.method_b">
        <code class="highlight language-python">
        method_b<span class="p">(</span><span class="bp">self</span><span class="p">)</span> </code>
        </h4><div><p>Print B!</p></div></div></div></div></div>

It is also possible to integrate a mkdocstrings identifier into a Markdown header:

```md
## ::: my_package.my_module.MyClass
    options:
      show_source: false
```

The above is equivalent to:

```md
::: my_package.my_module.MyClass
    options:
      show_source: false
      heading_level: 2
```

## Global options

*mkdocstrings* accepts a few top-level configuration options in `mkdocs.yml`:

- `default_handler`: The handler that is used by default when no handler is specified.
- `custom_templates`: The path to a directory containing custom templates.
  The path is relative to the MkDocs configuration file.
  See [Theming](theming.md).
- `handlers`: The handlers' global configuration.
- `enable_inventory`: Whether to enable inventory file generation.
  See [Cross-references to other projects / inventories](#cross-references-to-other-projects-inventories)
- `locale`: The locale used for translations. See [Internationalization](#internationalization-i18n).
- `enabled` **(New in version 0.20)**: Whether to enable the plugin. Defaults to `true`.
  Can be used to reduce build times when doing local development.
  Especially useful when used with environment variables (see example below).

!!! example
    ```yaml title="mkdocs.yml"
    plugins:
    - mkdocstrings:
        enabled: !ENV [ENABLE_MKDOCSTRINGS, true]
        custom_templates: templates
        default_handler: python
        locale: en
        handlers:
          python:
            options:
              show_source: false
    ```

    The handlers global configuration can then be overridden by local configurations:

    ```yaml title="docs/some_page.md"
    ::: my_package.my_module.MyClass
        options:
          show_source: true
    ```

Some handlers accept additional global configuration.
Check the documentation for your handler of interest in [Handlers](handlers.md).

## Internationalization (I18N)

Some handlers support multiple languages.

If the handler supports localization, the locale it uses is determined by the following order of precedence:

- `locale` in [global options](#global-options)
- `theme.language`: used by the [MkDocs Material theme](https://squidfunk.github.io/mkdocs-material/setup/changing-the-language/)
- `theme.locale` in [MkDocs configuration](https://www.mkdocs.org/user-guide/configuration/#theme)

## Cross-references

Cross-references are written as Markdown *reference-style* links:

=== "Markdown"
    ```md
    With a custom title:
    [`Object 1`][full.path.object1]

    With the identifier as title:
    [full.path.object2][]
    ```

=== "HTML Result"
    ```html
    <p>With a custom title:
    <a href="https://example.com/page1#full.path.object1"><code>Object 1</code></a><p>
    <p>With the identifier as title:
    <a href="https://example.com/page2#full.path.object2">full.path.object2</a></p>
    ```

Any item that was inserted using the [autodoc syntax](#autodoc-syntax)
(e.g. `::: full.path.object1`) is possible to link to by using the same identifier with the
cross-reference syntax (`[example][full.path.object1]`).
But the cross-references are also applicable to the items' children that get pulled in.

### Finding out the anchor

If you're not sure which exact identifier a doc item uses, you can look at its "anchor", which your
Web browser will show in the URL bar when clicking an item's entry in the table of contents.
If the URL is `https://example.com/some/page.html#full.path.object1` then you know that this item
is possible to link to with `[example][full.path.object1]`, regardless of the current page.

### Cross-references to any Markdown heading

TIP: **Changed in version 0.15.**
Linking to any Markdown heading used to be the default, but now opt-in is required.

If you want to link to *any* Markdown heading, not just *mkdocstrings*-inserted items, please
enable the [*autorefs* plugin for *MkDocs*](https://github.com/mkdocstrings/autorefs) by adding
`autorefs` to `plugins`:

```yaml title="mkdocs.yml" hl_lines="3"
plugins:
- search
- autorefs
- mkdocstrings:
    [...]
```

Note that you don't need to (`pip`) install anything more; this plugin is guaranteed to be pulled in with *mkdocstrings*.

!!! example
    === "doc1.md"
        ```md
        ## Hello, world!

        Testing
        ```

    === "doc2.md"
        ```md
        ## Something else

        Please see the [Hello, World!][hello-world] section.
        ```

    === "Result HTML for doc2"
        ```html
        <p>Please see the <a href="doc1.html#hello-world">Hello, World!</a> section.</p>
        ```

### Cross-references to a sub-heading in a docstring

TIP: **New in version 0.14.**

If you have a Markdown heading *inside* your docstring, you can also link directly to it.
In the example below you see the identifier to be linked is `foo.bar--tips`, because it's the "Tips" heading that's part of the `foo.bar` object, joined with "`--`".

!!! example
    === "foo.py"
        ```python
        def bar():
            """Hello, world!

            # Tips

            - Stay hydrated.
            """
        ```

    === "doc1.md"
        ```md
        ::: foo.bar
        ```

    === "doc2.md"
        ```md
        Check out the [tips][foo.bar--tips]
        ```

    === "HTML result for doc2"
        ```html
        <p>Check out the <a href="doc1.html#foo.bar--tips">tips</a></p>
        ```

The above tip about [Finding out the anchor](#finding-out-the-anchor) also applies the same way here.

You may also notice that such a heading does not get rendered as a `<h1>` element directly, but rather the level gets shifted to fit the encompassing document structure. If you're curious about the implementation, check out [mkdocstrings.HeadingShiftingTreeprocessor][] and others.

### Cross-references to other projects / inventories

TIP: **New in version 0.16.**

Python developers coming from Sphinx might know about its `intersphinx` extension,
that allows to cross-reference items between several projects.
*mkdocstrings* has a similar feature.

To reference an item from another project, you must first tell *mkdocstrings*
to load the inventory it provides. Each handler will be responsible of loading
inventories specific to its language. For example, the Python handler
can load Sphinx-generated inventories (`objects.inv`).

In the following snippet, we load the inventory provided by `installer`:

```yaml title="mkdocs.yml"
plugins:
- mkdocstrings:
    handlers:
      python:
        inventories:
        - https://installer.readthedocs.io/en/stable/objects.inv
```

Now it is possible to cross-reference `installer`'s items. For example:

=== "Markdown"
    ```md
    See [installer.records][] to learn about records.
    ```

=== "Result (HTML)"
    ```html
    <p>See <a href="https://installer.readthedocs.io/en/stable/api/records/#module-installer.records">installer.records</a>
    to learn about records.</p>
    ```

=== "Result (displayed)"
    See [installer.records][] to learn about records.

You can of course select another version of the inventory, for example:

```yaml
plugins:
- mkdocstrings:
    handlers:
      python:
        inventories:
        # latest instead of stable
        - https://installer.readthedocs.io/en/latest/objects.inv
```

In case the inventory file is not served under the base documentation URL,
you can explicitly specify both URLs:

```yaml
plugins:
- mkdocstrings:
    handlers:
      python:
        inventories:
        - url: https://cdn.example.com/version/objects.inv
          base_url: https://docs.example.com/version
```

Absolute URLs to cross-referenced items will then be based
on `https://docs.example.com/version/` instead of `https://cdn.example.com/version/`.

If you need authentication to access the inventory file, you can provide the credentials in the URL, either as `username:password`:

```yaml
- url: https://username:password@private.example.com/version/objects.inv
```

...or with token authentication:

```yaml
- url: https://token123@private.example.com/version/objects.inv
```

The credentials can also be specified using environment variables in the form `${ENV_VAR}`:

```yaml
- url: https://${USERNAME}:${PASSWORD}@private.example.com/version/objects.inv
```

Reciprocally, *mkdocstrings* also allows to *generate* an inventory file in the Sphinx format.
It will be enabled by default if the Python handler is used, and generated as `objects.inv` in the final site directory.
Other projects will be able to cross-reference items from your project.

To explicitly enable or disable the generation of the inventory file, use the global
`enable_inventory` option:

```yaml
plugins:
- mkdocstrings:
    enable_inventory: false
```
