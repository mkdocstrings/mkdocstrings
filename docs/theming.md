# Themes

*mkdocstrings* can support multiple MkDocs themes.
It currently supports supports the
*[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)*
theme and, partially, the built-in ReadTheDocs theme.

Each renderer can fallback to a particular theme when the user selected theme is not supported.
For example, the Python renderer will fallback to the *Material for MkDocs* templates.

## Customization

There is some degree of customization possible in *mkdocstrings*.
First, you can write custom templates to override the theme templates.
Second, the provided templates make use of CSS classes,
so you can tweak the look and feel with extra CSS rules.

### Templates

To use custom templates and override the theme ones,
specify the relative path to your templates directory
with the `custom_templates` global configuration option:

!!! example "mkdocs.yml"
    ```yaml
    plugins:
    - mkdocstrings:
        custom_templates: templates
    ```

You directory structure must be identical to the provided templates one:

```
templates
├─╴<HANDLER 1>
│   ├── <THEME 1>
│   └── <THEME 2>
└── <HANDLER 2>
    ├── <THEME 1>
    └── <THEME 2>
```

(*[Check out the template tree on GitHub](https://github.com/mkdocstrings/mkdocstrings/tree/master/src/mkdocstrings/templates/)*)

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
