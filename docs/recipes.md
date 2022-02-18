On this page you will find various recipes, tips and tricks
for *mkdocstrings* and more generally Markdown documentation.

## Automatic code reference pages

*mkdocstrings* allows to inject documentation for any object
into Markdown pages. But as the project grows, it quickly becomes
quite tedious to keep the autodoc instructions, or even the dedicated
Markdown files in sync with all your source files and objects.

In this recipe, we will iteratively automate the process
of generating these pages at each build of the documentation.

---

Let say you have a project called `project`.
This project has a lot of source files, or modules,
which live in the `src` folder:

```
📁 repo
└─╴📁 src
    └─╴📁 project
        ├─╴📄 lorem
        ├─╴📄 ipsum
        ├─╴📄 dolor
        ├─╴📄 sit
        └─╴📄 amet
```

Without an automatic process, you will have to manually
create a Markdown page for each one of these modules,
with the corresponding autodoc instruction, for example `::: project.lorem`,
and also add entry in MkDocs' navigation option (`nav` in `mkdocs.yml`).
With a lot of modules, this is quickly getting cumbersome.

Lets fix that.

### Generate pages on-the-fly

In this recipe, we suggest to use the [mkdocs-gen-files plugin](https://github.com/oprypin/mkdocs-gen-files).
This plugin exposes utilities to generate files at build time.
These files won't be written to the docs directory: you don't have
to track and version them. They are transparently generated each
time you build your docs. This is perfect for our use-case!

Add `mkdocs-gen-files` to your project's docs dependencies,
and configure it like so:

```yaml title="mkdocs.yml"
plugins:
- search  # (1)
- gen-files:
    scripts:
    - docs/gen_ref_pages.py  # (2)
- mkdocstrings:
    watch:
    - src/project  # (3)
```

1. Don't forget to load the `search` plugin when redefining the `plugins` item.
2. The magic happens here, see below how it works.
3. Useful for the live-reload feature of `mkdocs serve`.

mkdocs-gen-files is able to run Python scripts at build time.
The Python script that we will execute lives in the docs folder,
and is named `gen_ref_pages.py`, like "generate code reference pages".

```python title="docs/gen_ref_pages.py"
"""Generate the code reference pages."""

from pathlib import Path

import mkdocs_gen_files

for path in sorted(Path("src").rglob("*.py")):  # (1)
    module_path = path.relative_to("src").with_suffix("")  # (2)
    doc_path = path.relative_to("src").with_suffix(".md")  # (3)
    full_doc_path = Path("reference", doc_path)  # (4)

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:  # (5)
        identifier = ".".join(module_path.parts)  # (6)
        print("::: " + identifier, file=fd)  # (7)

    mkdocs_gen_files.set_edit_path(full_doc_path, path)  # (8)
```

1. Here we recursively list all `.py` files, but you can adapt the code to list
   files with other extensions of course, supporting other languages than Python.
2. The module path will look like `project/lorem`.
   It will be used to build the *mkdocstrings* autodoc identifier.
3. This is the relative path to the Markdown page.
4. This is the absolute path to the Markdown page. Here we put all reference pages
   into a `reference` folder.
5. Magic! Add the file to MkDocs pages, without actually writing it in the docs folder.
6. Build the autodoc identifier. Here we document Python modules, so the identifier
   is a dot-separated path, like `project.lorem`.
7. Actually write to the magic file.
8. We can even set the `edit_uri` on the pages.

With this script, a `reference` folder is automatically created
each time we build our docs. This folder contains a Markdown page
for each of our source modules, and each of these pages
contains a single line of the form `::: project.module`
(module being `lorem`, `ipsum`, etc.). Great!
But, we still have to actually add those pages into our MkDocs
navigation:

```yaml title="mkdocs.yml"
nav:
# rest of the navigation...
- Code Reference:
  - project:
    - lorem: reference/project/lorem.md
    - ipsum: reference/project/ipsum.md
    - dolor: reference/project/dolor.md
    - sit: reference/project/sit.md
    - amet: reference/project/amet.md
# rest of the navigation...
```

Err... so this process is only semi-automatic?
Yes, but don't worry, we can fully automate it.

### Generate a literate navigation file

mkdocs-gen-files is able to generate a literate navigation file.
But to make use of it, we will need an additional plugin:
[mkdocs-literate-nav](https://pypi.org/project/mkdocs-literate-nav/).
This plugin allows to specify the whole navigation, or parts of it,
into Markdown pages, as plain Markdown lists.
We use it here to specify the navigation for the code reference pages.

First, add `mkdocs-literate-nav` to your project's docs dependencies,
and configure the plugin in your MkDocs configuration:

```yaml title="mkdocs.yml" hl_lines="6 7"
plugins:
- search
- gen-files:
    scripts:
    - docs/gen_ref_pages.py
- literate-nav:
    nav_file: SUMMARY.md
- mkdocstrings:
    watch:
    - src/project
```

Then, the previous script is updated like so:

```python title="docs/gen_ref_pages.py" hl_lines="7 14 22 23"
"""Generate the code reference pages and navigation."""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

for path in sorted(Path("src").rglob("*.py")):
    module_path = path.relative_to("src").with_suffix("")
    doc_path = path.relative_to("src").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    nav[module_path.parts] = doc_path  # (1)

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(module_path.parts)
        print("::: " + ident, file=fd)

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:  # (2)
    nav_file.writelines(nav.build_literate_nav())  # (3)
```

1. Progressively build the navigation object.
2. At the end, create a magic, literate navigation file called `SUMMARY.md` in the `reference` folder.
3. Write the navigation as a Markdown list in the literate navigation file.

Now we are able to remove our hard-coded navigation in `mkdocs.yml`,
and replace it with a single line!

```yaml title="mkdocs.yml"
nav:
# rest of the navigation...
# defer to gen-files + literate-nav
- Code Reference: reference/  # (1)
# rest of the navigation...
```

1. Note the trailing slash! It is needed so that `mkdocs-literate-nav` knows
   it has to look for a `SUMMARY.md` file in that folder.

## Prevent selection of `>>>` in Python code blocks

To prevent the selection of `>>>` in Python code blocks,
you can use the `pycon` syntax highlighting on your code block,
and add some CSS rules to your site using MkDocs `extra_css` option:

````md
```pycon
>>> print("Hello mkdocstrings!")
```
````

```css title="docs/css/code_select.css"
.highlight .gp, .highlight .go { /* Generic.Prompt, Generic.Output */
    user-select: none;
}
```

```yaml title="mkdocs.yml"
extra_css:
- css/code_select.css
```

Try to select the following code block's text:

<style>
.highlight .gp, .highlight .go { /* Generic.Prompt, Generic.Output */
    user-select: none;
}
</style>

```pycon
>>> print("Hello mkdocstrings!")
```
