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
- mkdocstrings
```

1. Don't forget to load the `search` plugin when redefining the `plugins` item.
2. The magic happens here, see below how it works.

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

    parts = list(module_path.parts)

    if parts[-1] == "__init__":  # (5)
        parts = parts[:-1]
    elif parts[-1] == "__main__":
        continue

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:  # (6)
        identifier = ".".join(parts)  # (7)
        print("::: " + identifier, file=fd)  # (8)

    mkdocs_gen_files.set_edit_path(full_doc_path, path)  # (9)
```

1. Here we recursively list all `.py` files, but you can adapt the code to list
   files with other extensions of course, supporting other languages than Python.
2. The module path will look like `project/lorem`.
   It will be used to build the *mkdocstrings* autodoc identifier.
3. This is the relative path to the Markdown page.
4. This is the absolute path to the Markdown page. Here we put all reference pages
   into a `reference` folder.
5. This part is only relevant for Python modules. We skip `__main__` modules and
   remove `__init__` from the module parts as it's implicit during imports.
6. Magic! Add the file to MkDocs pages, without actually writing it in the docs folder.
7. Build the autodoc identifier. Here we document Python modules, so the identifier
   is a dot-separated path, like `project.lorem`.
8. Actually write to the magic file.
9. We can even set the `edit_uri` on the pages.

> NOTE:
> It is important to look out for correct edit page behaviour when using generated pages.
> For example, if we have `edit_uri` set to `blob/master/docs/` and the following
> file structure:
>
> ```
> 📁 repo
> ├─ 📄 mkdocs.yml
> │
> ├─ 📁 docs
> │   ├─╴📄 index.md
> │   └─╴📄 gen_ref_pages.py
> │
> └─╴📁 src
>    └─╴📁 project
>        ├─╴📄 lorem.py
>        ├─╴📄 ipsum.py
>        ├─╴📄 dolor.py
>        ├─╴📄 sit.py
>        └─╴📄 amet.py
> ```
>
> Then we will have to change our `set_edit_path` call to:
>
> ```python
> mkdocs_gen_files.set_edit_path(full_doc_path, Path("../") / path)  # (1)
> ```
>
> 1. Path can be used to traverse the structure in any way you may need, but
>    remember to use relative paths!
>
> ...so that it correctly sets the edit path of (for example) `lorem.py` to
> `<repo_url>/blob/master/src/project/lorem.py` instead of
> `<repo_url>/blob/master/docs/src/project/lorem.py`.

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
[mkdocs-literate-nav](https://github.com/oprypin/mkdocs-literate-nav).
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
- mkdocstrings
```

Then, the previous script is updated like so:

```python title="docs/gen_ref_pages.py" hl_lines="7 21 29 30"
"""Generate the code reference pages and navigation."""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

for path in sorted(Path("src").rglob("*.py")):
    module_path = path.relative_to("src").with_suffix("")
    doc_path = path.relative_to("src").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
    elif parts[-1] == "__main__":
        continue

    nav[parts] = doc_path.as_posix()  # (1)

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"::: {ident}")

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

At this point, we should be able to see the tree of our modules
in the navigation.

### Bind pages to sections themselves

There's a last improvement we can do.
With the current script, sections, corresponding to folders,
will expand or collapse when you click on them,
revealing `__init__` modules under them
(or equivalent modules in other languages, if relevant).
Since we are documenting a public API, and given users
never explicitly import `__init__` modules, it would be nice
if we could get rid of them and instead render their documentation
inside the section itself.

Well, this is possible thanks to a third plugin:
[mkdocs-section-index](https://github.com/oprypin/mkdocs-section-index).

Update the script like this:

```python title="docs/gen_ref_pages.py" hl_lines="18 19"
"""Generate the code reference pages and navigation."""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

for path in sorted(Path("src").rglob("*.py")):
    module_path = path.relative_to("src").with_suffix("")
    doc_path = path.relative_to("src").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue

    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        fd.write(f"::: {ident}")

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
```

And update your MkDocs configuration to list the plugin:

```yaml title="mkdocs.yml" hl_lines="8"
plugins:
- search
- gen-files:
    scripts:
    - docs/gen_ref_pages.py
- literate-nav:
    nav_file: SUMMARY.md
- section-index
- mkdocstrings
```

With this, `__init__` modules will be documented and bound to the sections
themselves, better reflecting our public API.

## Prevent selection of prompts and output in Python code blocks

To prevent the selection of `>>>`, `...` and output in Python "Console" code blocks,
you can use the `pycon` syntax highlighting on your code blocks,
and add global CSS rules to your site using MkDocs `extra_css` option:

````md
```pycon
>>> for word in ("Hello", "mkdocstrings!"):
...     print(word, end=" ")
...
Hello mkdocstrings!
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

> WARNING:
> The `.highlight .gp, .highlight .go` CSS selector can have unintended side-effects.
> To target `pycon` code blocks more specifically, you can configure the
> `pymdownx.highlight` extension to use Pygments and set language classes
> on code blocks:
> 
> ```yaml title="mkdocs.yml"
> markdown_extensions:
> - pymdownx.highlight:
>     use_pygments: true
>     pygments_lang_class: true
> ```
> 
> Then you can update the CSS selector like this:
> 
> ```css title="docs/css/code_select.css"
> .language-pycon .gp, .language-pycon .go { /* Generic.Prompt, Generic.Output */
>     user-select: none;
> }
> ```

If you don't want to enable this globally,
you can still use `style` tags in the relevant pages,
with more accurate CSS selectors:

```html
<style>
#my-div .highlight .gp, #my-div .highlight .go { /* Generic.Prompt, Generic.Output */
    user-select: none;
}
</style>
```

Try to select the following code block's text:

<style>
.highlight .gp, .highlight .go { /* Generic.Prompt, Generic.Output */
    user-select: none;
}
</style>

```pycon
>>> for word in ("Hello", "mkdocstrings!"):
...     print(word, end=" ")
Hello mkdocstrings!
```
