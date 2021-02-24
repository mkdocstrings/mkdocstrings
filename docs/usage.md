# Usage

## Autodoc syntax

*mkdocstrings* works by processing special expressions in your Markdown files.

The syntax is as follows:

```md
::: identifier
    YAML block
```

The `identifier` is a string identifying the object you want to document.
The format of an identifier can vary from one handler to another.
For example, the Python handler expects the full dotted-path to a Python object:
`my_package.my_module.MyClass.my_method`.

The YAML block is optional, and contains some configuration options:

- `handler`: the name of the handler to use to collect and render this object.
  By default, it will use the value defined in the [Global options](#global-options)'s
  `default_handler` key, or `"python"`.
- `selection`: a dictionary of options passed to the handler's collector.
  The collector is responsible for collecting the documentation from the source code.
  Therefore, selection options change how the documentation is collected from the source code.
- `rendering`: a dictionary of options passed to the handler's renderer.
  The renderer is responsible for rendering the documentation with Jinja2 templates.
  Therefore, rendering options affect how the selected object's documentation is rendered.

Every handler accepts at least these two keys, `selection` and `rendering`,
and some handlers accept additional keys.
Check the documentation for your handler of interest in [Handlers](handlers/overview.md).

!!! example "Example with the Python handler"
    === "docs/my_page.md"
        ```md
        # Documentation for `MyClass`

        ::: my_package.my_module.MyClass
            handler: python
            selection:
              members:
                - method_a
                - method_b
            rendering:
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
    rendering:
      show_source: false
```

The above is equivalent to:

```md
::: my_package.my_module.MyClass
    rendering:
      show_source: false
      heading_level: 2
```

## Global options

*mkdocstrings* accepts a few top-level configuration options in `mkdocs.yml`:

- `watch`: a list of directories to watch while serving the documentation.
  See [Watch directories](#watch-directories).
- `default_handler`: the handler that is used by default when no handler is specified.
- `custom_templates`: the path to a directory containing custom templates.
  The path is relative to the docs directory.
  See [Theming](theming.md).
- `handlers`: the handlers global configuration.

Example:

!!! example "mkdocs.yml"
    ```yaml
    plugins:
    - mkdocstrings:
        default_handler: python
        handlers:
          python:
            rendering:
              show_source: false
        custom_templates: templates
        watch:
          - src/my_package
    ```

The handlers global configuration can then be overridden by local configurations:

```yaml
::: my_package.my_module.MyClass
    rendering:
      show_source: true
```

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

#### Finding out the anchor

If you're not sure which exact identifier a doc item uses, you can look at its "anchor", which your
Web browser will show in the URL bar when clicking an item's entry in the table of contents.
If the URL is `https://example.com/some/page.html#full.path.object1` then you know that this item
is possible to link to with `[example][full.path.object1]`, regardless of the current page.

### Cross-references to any Markdown heading

!!! important "Changed in version 0.15"
    Linking to any Markdown heading used to be the default, but now opt-in is required.

If you want to link to *any* Markdown heading, not just *mkdocstrings*-inserted items, please
enable the [*autorefs* plugin for *MkDocs*](https://github.com/mkdocstrings/autorefs) by adding
`autorefs` to `plugins`:

!!! example "mkdocs.yml"
    ```yaml hl_lines="4"
    plugins:
      - admonition
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

!!! important "New in version 0.14"

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

    === "Result HTML for doc2"
        ```html
        <p>Check out the <a href="doc1.html#foo.bar--tips">tips</a></p>
        ```

The above tip about [Finding out the anchor](#finding-out-the-anchor) also applies the same way here.

You may also notice that such a heading does not get rendered as a `<h1>` element directly, but rather the level gets shifted to fit the encompassing document structure. If you're curious about the implementation, check out [mkdocstrings.handlers.rendering.HeadingShiftingTreeprocessor][] and others.


## Watch directories

You can add directories to watch with the `watch` key.
It accepts a list of paths.

!!! example "mkdocs.yml"
    ```yaml
    plugins:
      - mkdocstrings:
          watch:
            - src/my_package_1
            - src/my_package_2
    ```

When serving your documentation
and a change occur in one of the listed path,
MkDocs will rebuild the site and reload the current page.

!!! note "The `watch` feature doesn't have special effects."
    Adding directories to the `watch` list doesn't have any other effect than watching for changes.
    For example, it will not tell the Python handler to look for packages in these paths
    (the paths are not added to the `PYTHONPATH` variable).
    If you want to tell Python where to look for packages and modules,
    see [Python Handler: Finding modules](handlers/python.md#finding-modules).
