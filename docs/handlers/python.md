# Python handler

## Handler options

Like every handler, the Python handler accepts the common
[`selection`](#selection) and [`rendering`](#rendering) options,
both as **global** and **local** options.
The `selection` options gives you control over the selection of Python objects,
while the `rendering` options lets you change how the documentation is rendered.

It also accepts these additional **global-only** options:

Option | Type | Description | Default
------ | ---- | ----------- | -------
**`setup_commands`** | `list of str` | Run these commands before starting the documentation collection. | `[]`

!!! example "Example: setup Django before collecting documentation"
    ```yaml
    # mkdocs.yml
    plugins:
      - mkdocstrings:
          handlers:
            python:
              setup_commands:
                - import os
                - import django
                - os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_django_app.settings")
                - django.setup()
    ```

!!! important
    Additional options like `setup_commands` are used only once,
    when instantiating the handler the first time it is requested.
    This is why they are considered global-only options,
    as they will have no effect if used as local options.

### Selection

The following options are directly passed to the handler's collector.
See [Collector: pytkdocs](#collector-pytkdocs) to learn more about `pytkdocs`.

Option | Type | Description | Default
------ | ---- | ----------- | -------
**`filters`** | `list of str` | List of filtering regular expressions. Prefix with `!` to exclude objects whose name match. The default means *exclude private members*. | `["!^_[^_]"]`
**`members`** | `bool`, or `list of str` | Explicitly select members. True means *all*, false means *none*. | `True`
**`inherited_members`** | `bool` | Also select members inherited from parent classes. | `False`
**`docstring_style`** | `str` | Docstring style to parse. `pytkdocs` only supports `google` yet. | `"google"`
**`docstring_options`** | `dict` | Options to pass to the docstring parser. See [Collector: pytkdocs](#collector-pytkdocs) | `{}`
**`new_path_syntax`** | `bool` | Whether to use the new "colon" path syntax when importing objects. | `False`

!!! example "Configuration example"
    === "Global"
        ```yaml
        # mkdocs.yml
        plugins:
          - mkdocstrings:
              handlers:
                python:
                  selection:
                    filters:
                      - "!^_"  # exlude all members starting with _
                      - "^__init__$"  # but always include __init__ modules and methods
        ```
        
    === "Local"
        ```yaml
        ::: my_package
            selection:
              filters: []  # pick up everything
        ```
    
### Rendering

::: mkdocstrings.handlers.python:PythonRenderer.default_config
    rendering:
      show_root_toc_entry: false

These options affect how the documentation is rendered.

!!! example "Configuration example"
    === "Global"
        ```yaml
        # mkdocs.yml
        plugins:
          - mkdocstrings:
              handlers:
                python:
                  rendering:
                    show_root_heading: yes
        ```
        
    === "Local"
        ```md
        ## `ClassA`

        ::: my_package.my_module.ClassA
            rendering:
              show_root_heading: no
              heading_level: 3
        ```

## Collector: pytkdocs

The tool used by the Python handler to collect documentation from Python source code
is [`pytkdocs`](https://pawamoy.github.io/pytkdocs).
It stands for *(Python) Take Docs*, and is supposed to be a pun on MkDocs (*Make Docs*?).

### Supported docstrings styles

Right now, `pytkdocs` supports only the Google-style docstring format.

#### Google-style

You can see examples of Google-style docstrings
in [Napoleon's documentation](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).

##### Sections

Docstrings sections are parsed by `pytkdocs` and rendered by MkDocstrings.
Supported sections are:

- `Arguments` (or `Args`, `Parameters`, `Params`)
- `Attributes`
- `Examples` (or `Example`)
- `Raises` (or `Raise`, `Except`, `Exceptions`)
- `Returns` (or `Return`)

##### Admonitions

Additionally, any section that is not recognized will be transformed into its admonition equivalent.
For example:

=== "Original"
    ```python
    """
    Note: You can disable this behavior with the `replace_admonitions` option.
        To prevent `pytkdocs` from converting sections to admonitions,
        use the `replace_admonitions`:
       
        ```md
        ::: my_package.my_module
            selection:
              docstring_style: google  # this is the default
              docstring_options:
                replace_admonitions: no 
        ```
        
        So meta!
    """
    ```

=== "Modified"
    ```python
    """
    !!! note "You can disable this behavior with the `replace_admonitions` option."
        To prevent `pytkdocs` from converting sections to admonitions,
        use the `replace_admonitions`:
       
        ```md
        ::: my_package.my_module
            selection:
              docstring_style: google  # this is the default
              docstring_options:
                replace_admonitions: no 
        ```
        
        So meta!
    """
    ```
    
=== "Result"
    !!! note "You can disable this behavior with the `replace_admonitions` parser option."
        To prevent `pytkdocs` from converting sections to admonitions,
        use the `replace_admonitions` parser option:
       
        ```md
        ::: my_package.my_module
            selection:
              docstring_style: google  # this is the default
              docstring_options:
                replace_admonitions: no 
        ```
        
        So meta!

As shown in the above example, this can be disabled
with the `replace_admonitions` option of the Google-style parser:

```yaml
::: my_package.my_module
    selection:
      docstring_style: google  # this is the default
      docstring_options:
        replace_admonitions: no 
```

##### Annotations

Type annotations are read both in the code and in the docstrings.

!!! example "Example with a function"
    **Expand the source at the end to see the original code!**
    
    ::: snippets.function_annotations:my_function
        rendering:
          show_root_heading: no
          show_root_toc_entry: no

## Finding modules

In order for `pytkdocs` to find your packages and modules,
you should take advantage of the usual Python loading mechanisms:

- install your package in the current virtualenv:
    ```bash
    . venv/bin/activate
    pip install -e .
    ```
  
    ```bash
    poetry install
    ```
  
    ...etc.
    
- or add your package(s) parent directory in the `PYTHONPATH`.
  
(*The following instructions assume your Python package is in the `src` directory.*)

In Bash and other shells, you can run your command like this
(note the prepended `PYTHONPATH=...`):

```bash
PYTHONPATH=src poetry run mkdocs serve
```

You could also export that variable,
but this is **not recommended** as it could affect other Python processes:

```bash
export PYTHONPATH=src  # Linux/Bash and similar
setx PYTHONPATH src  # Windows, USE AT YOUR OWN RISKS
```

You can also use the Python handler `setup_commands`:

```yaml
# mkdocs.yml
plugins:
  - mkdocstrings:
      handlers:
        python:
          setup_commands:
            - import sys
            - sys.path.append("src")
            # or sys.path.insert(0, "src")
```

## Mocking libraries

You may want to to generate documentation for a package while its dependencies are not available.
The Python handler provides itself no builtin way to mock libraries,
but you can use the `setup_commands` to mock them manually:

```yaml
# mkdocs.yml
plugins:
  - mkdocstrings:
      handlers:
        python:
          setup_commands:
            - import sys
            - from unittest.mock import MagicMock as mock
            - sys.modules["lib1"] = mock()
            - sys.modules["lib2"] = mock()
            - sys.modules["lib2.module1"] = mock()
            - sys.modules["lib2.module1.moduleB"] = mock()
            # etc
```

## Recommended style (Material)

Here are some CSS rules for the
[*Material for MkDocs*](https://squidfunk.github.io/mkdocs-material/) theme:

```css
/* Indentation. */
div.doc-contents:not(.first) {
  padding-left: 25px;
  border-left: 4px solid rgba(230, 230, 230);
  margin-bottom: 80px;
}

/* Don't capitalize names. */
h5.doc-heading {
  text-transform: none !important;
}

/* Don't use vertical space on hidden ToC entries. */
.hidden-toc::before {
  margin-top: 0 !important;
  padding-top: 0 !important;
}

/* Don't show permalink of hidden ToC entries. */
.hidden-toc a.headerlink {
  display: none;
}

/* Avoid breaking parameters name, etc. in table cells. */
td code {
  word-break: normal !important;
}

/* For pieces of Markdown rendered in table cells. */
td p {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
}
```

## Recommended style (ReadTheDocs)

Here are some CSS rules for the built-in *ReadTheDocs* theme:

```css
/* Indentation. */
div.doc-contents:not(.first) {
  padding-left: 25px;
  border-left: 4px solid rgba(230, 230, 230);
  margin-bottom: 60px;
}

/* Don't use vertical space on hidden ToC entries. */
.hidden-toc::before {
  margin-top: 0 !important;
  padding-top: 0 !important;
}

/* Don't show permalink of hidden ToC entries. */
.hidden-toc a.headerlink {
  display: none;
}

/* Avoid breaking parameters name, etc. in table cells. */
td code {
  word-break: normal !important;
}

/* For pieces of Markdown rendered in table cells. */
td p {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
}

/* Avoid breaking code headings. */
.doc-heading code {
  white-space: normal;
}

/* Improve rendering of parameters, returns and exceptions. */
.field-name {
  min-width: 100px;
}
.field-name, .field-body {
  border: none !important;
  padding: 0 !important;
}
.field-list {
  margin: 0 !important;
}
```
