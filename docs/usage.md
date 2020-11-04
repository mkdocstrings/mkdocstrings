# Usage

MkDocstrings works by processing special expressions in your Markdown files.

The syntax is as follow:

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
Check the documentation for your handler of interest in [Handlers](../handlers/overview).

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

MkDocstrings accept a few top-level configuration options in `mkdocs.yml`:

- `watch`: a list of directories to watch while serving the documentation.
  See [Watch directories](#watch-directories).
- `default_handler`: the handler that is used by default when no handler is specified.
- `custom_templates`: the path to a directory containing custom templates.
  The path is relative to the docs directory.
  See [Customization](#customization).
- `handlers`: the handlers global configuration.

Example:

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
    <a href="https://site_url.com/page1#full.path.object1"><code>Object 1</code></a><p>
    <p>With the identifier as title:
    <a href="https://site_url.com/page2#full.path.object2">full.path.object2</a></p>
    ```

## Themes

MkDocstrings can support multiple MkDocs theme,
though it only supports the
*[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)*
theme right now.

Each renderer can fallback to a particular theme when the user selected theme is not supported.
For example, the Python renderer will fallback to the *Material for MkDocs* templates.

## Customization

There is some degree of customization possible in MkDocstrings.
First, you can write custom templates to override the theme templates.
Second, the provided templates make use of CSS classes,
so you can tweak the look and feel with extra CSS rules. 

### Templates

To use custom templates and override the theme ones,
specify the relative path to your templates directory
with the `custom_templates` global configuration option:

```yaml
# mkdocs.yml
plugins:
  - mkdocstrings:
      custom_templates: templates
```

You directory structure must be identical to the provided templates one:

```
templates
├── <HANDLER 1>
│   ├── <THEME 1>
│   └── <THEME 2>
└── <HANDLER 2>
    ├── <THEME 1>
    └── <THEME 2>
```

(*[Check out the template tree on GitHub](https://github.com/pawamoy/mkdocstrings/tree/master/src/mkdocstrings/templates/)*)

You don't have to replicate the whole tree,
only the handlers, themes or templates you want to override.
For example, to override some templates of the *Material* theme for Python:

```
templates
└── python
    └── material
        ├── parameters.html
        └── exceptions.html
```

In the HTML files, replace the original contents with your modified version.
In the future, the templates will use Jinja blocks, so it will be easier
to modify a small part of the template without copy-pasting the whole file.

The *Material* theme provides the following template structure:

- `children.html`: where the recursion happen, to render all children of an object
    - `attribute.html`: to render attributes (class-attributes, etc.)
    - `class.html`: to render classes
    - `function.html`: to render functions
    - `method.html`: to render methods
    - `module.html`: to render modules
- `docstring.html`: to render docstrings
    - `attributes.html`: to render attributes sections of docstrings
    - `examples.html`: to render examples sections of docstrings
    - `exceptions.html`: to render exceptions/"raises" sections of docstrings
    - `parameters.html`: to render parameters/arguments sections of docstrings
    - `return.html`: to render "return" sections of docstrings
- `properties.html`: to render the properties of an object (`staticmethod`, `read-only`, etc.)
- `signature.html`: to render functions and methods signatures

#### Debugging

Every template has access to a `log` function, allowing to log messages as usual:

```jinja
{{ log.debug("A DEBUG message.") }}
{{ log.info("An INFO message.") }}
{{ log.warning("A WARNING message.") }}
{{ log.error("An ERROR message.") }}
{{ log.critical("A CRITICAL message.") }}
```

### CSS classes

The *Material* theme uses the following CSS classes in the HTML:

- `doc`: on all the following elements
- `doc-children`: on `div`s containing the children of an object
- `doc-object`: on `div`s containing an object
    - `doc-attribute`: on `div`s containing an attribute 
    - `doc-class`: on `div`s containing a class 
    - `doc-function`: on `div`s containing a function 
    - `doc-method`: on `div`s containing a method 
    - `doc-module`: on `div`s containing a module 
- `doc-heading`: on objects headings 
- `doc-contents`: on `div`s wrapping the docstring then the children (if any)
    - `first`: same, but only on the root object's contents `div`
- `doc-properties`: on `span`s wrapping the object's properties
    - `doc-property`: on `small` elements containing a property
        - `doc-property-PROPERTY`: same, where `PROPERTY` is replaced by the actual property
        
!!! example "Example with colorful properties"
    === "CSS"
        ```css
        .doc-property { border-radius: 15px; padding: 0 5px; }
        .doc-property-special { background-color: blue; color: white; }
        .doc-property-private { background-color: red; color: white; }
        .doc-property-property { background-color: green; color: white; }
        .doc-property-read-only { background-color: yellow; color: black; }
        ```
        
    === "Result"
        <style>
          .prop { border-radius: 15px; padding: 0 5px; }
        </style>
        <h3 style="margin: 0;"><span>
            <small class="prop" style="background-color: blue; color: white !important;">special</small>
            <small class="prop" style="background-color: red; color: white !important;">private</small>
            <small class="prop" style="background-color: green; color: white !important;">property</small>
            <small class="prop" style="background-color: yellow; color: black !important;">read-only</small>
        </span></h3>
        
        As you can see, CSS is not my field of predilection...

## Watch directories

You can add directories to watch with the `watch` key.
It accepts a list of paths.

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
    see [Python Handler: Finding modules](../handlers/python/#finding-modules).
