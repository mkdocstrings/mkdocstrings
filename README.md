# mkdocstrings
[![pipeline status](https://gitlab.com/pawamoy/mkdocstrings/badges/master/pipeline.svg)](https://gitlab.com/pawamoy/mkdocstrings/pipelines)
[![coverage report](https://gitlab.com/pawamoy/mkdocstrings/badges/master/coverage.svg)](https://gitlab.com/pawamoy/mkdocstrings/commits/master)
[![documentation](https://img.shields.io/badge/docs-latest-green.svg?style=flat)](https://pawamoy.github.io/mkdocstrings)
[![pypi version](https://img.shields.io/pypi/v/mkdocstrings.svg)](https://pypi.org/project/mkdocstrings/)

Automatic documentation from docstrings, for mkdocs.

This plugin is still in alpha status. Here is how it looks with the [mkdocs-material theme](https://squidfunk.github.io/mkdocs-material/) for now:

![mkdocstrings](https://user-images.githubusercontent.com/3999221/71327911-e467d000-250e-11ea-83e7-a81ec59f41e2.gif)

## Features
- **Works great with Material theme:** `mkdocstrings` was designed to work best with
  the great [Material theme](https://squidfunk.github.io/mkdocs-material/).
- **Support for type annotations:** `mkdocstrings` uses your type annotations to display parameters types
  or return types.
- **Recursive documentation of Python objects:** just write the module dotted-path, and you get the full module docs.
  No need to ask for each class, function, etc.
- **Support for documented attribute:** attributes (variables) followed by a docstring (triple-quoted string) will
  be recognized by `mkdocstrings`, in modules, classes and even in `__init__` methods.
- **Support for objects properties:** `mkdocstrings` will know if a method is a `staticmethod`, a `classmethod` or else,
  it will also know if a property is read-only or writable, and more! These properties will be displayed
  next to the object signature.
- **Every object has a TOC entry and a unique permalink:** the navigation is greatly improved! Click the anchor
  next to the object signature to get its permalink, which is its Python dotted-path.
- **Auto-reference other objects:** `mkdocstrings` makes it possible to reference other Python objects from your
  markdown files, and even from your docstrings, with the classic Markdown syntax:
  `[this object][package.module.object]` or directly with `[package.module.object][]`.
- **Google-style sections support in docstrings:** `mkdocstrings` understands `Arguments:`, `Raises:`
  and `Returns:` sections. It will even keep the section order in the generated docs.
- **Support for source code display:** `mkdocstrings` can add a collapsible div containing the source code of the
  Python object, directly below its signature, with the right line numbers.
- **Admonition support in docstrings:** blocks like `Note: ` or `Warning: ` will be transformed
  to their [admonition](https://squidfunk.github.io/mkdocs-material/extensions/admonition/) equivalent.
  *We do not support nested admonitions in docstrings!*
- **Sane defaults:** you should be able to just drop the plugin in your configuration and enjoy your auto-generated docs.

To get an example of what is possible, check `mkdocstrings`'
own [documentation](https://pawamoy.github.io/mkdocstrings), generated with itself.

## Roadmap
- [x] **December 2019:** It all started with a Proof of Concept.
  I familiarized myself with mkdocs and its plugin system,
  wrote quick and dirty code to retrieve Python objects with their docstrings
  and generate markdown from it. Markdown was automatically rendered to HTML
  in the mkdocs rendering process. It worked well but was really messy and not
  flexible at all.
- [x] **January 2020:** I started designing a better architecture (mkdocs plugin + markdown extension),
  see [issue #28](https://github.com/pawamoy/mkdocstrings/issues/28)
- [x] **January 2020:** I still packaged it (with Poetry :heart:) and released the first versions to try it on real projects.
- [x] **January 2020:** Some people tried it as well, contributed (thanks a lot!) and then
  someone with a lot of followers starred it and it got more attention.
- [x] **January 2020:** It was the end of the year and the beginning of a new one, and I started a new job
  so my time was very limited. There were a few bug fixes, but overall slow progress.
- [ ] **February 2020:** Efforts are being put into the implementation of the desired architecture.
  Once it's done, it will be easier to contribute and things will move faster. It's just a bit hard right now
  because of my limited time, and the task requiring more than a few consecutive minutes to be done
  (more like a few consecutive hours).
- [ ] **Mars 2020:** At this point I'll make a new release (still 0.x of course)
- [ ] **Mars 2020:** And obviously we'll need an extensive test suite to ensure quality :slightly_smiling_face:
- [ ] **Mars-April 2020:** We'll make mkdocstrings configurable (for selecting objects and rendering them)
- [ ] **April 2020:** Work the backlog!

## Requirements
mkdocstrings requires Python 3.6 or above.

<details>
<summary>To install Python 3.6, I recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>

```bash
# install pyenv
git clone https://github.com/pyenv/pyenv ~/.pyenv

# setup pyenv (you should also put these three lines in .bashrc or similar)
export PATH="${HOME}/.pyenv/bin:${PATH}"
export PYENV_ROOT="${HOME}/.pyenv"
eval "$(pyenv init -)"

# install Python 3.6
pyenv install 3.6.8

# make it available globally
pyenv global system 3.6.8
```
</details>

## Installation
With `pip`:
```bash
python3.6 -m pip install mkdocstrings
```

## Usage

```yaml
# mkdocs.yml

# designed to work best with material theme
theme:
  name: "material"

plugins:
  - search
  - mkdocstrings
```

In one of your markdown files:

```markdown
# Reference

::: my_library.my_module.my_class
```

You can reference objects from other modules in your docstrings:

```python
def some_function():
    """
    This is my function.

    It references [another function][package.submodule.function].
    It also references another object directly: [package.submodule.SuperClass][].
    """
    pass
```

Add some style in `docs/custom.css`:

```css
div.autodoc {
  padding-left: 25px;
  border-left: 4px solid rgba(230, 230, 230);
}
```

And add it to your configuration:

```yaml
extra_css:
  - custom.css
```

## Docstrings format
Your docstrings must follow a particular format, otherwise `mkdocstrings` will throw an exception.
This will be improved to be more robust over time.

```python
from typing import Optional

def my_function(param1: int, param2: Optional[str] = None) -> str:
    """
    A short description of this function.

    A longer description of this function.
    You can use more lines.

        This is code block,
        as usual.

    ```python
    s = "This is a Python code block :)"
    ```

    Arguments:
        param1: An integer?
        param2: A string? If you have a long description,
          you can split it on multiple lines.
          Just remember to indent those lines with at least two more spaces.
               They will all be concatenated in one line, so do not try to
             use complex markup here.

    Note:
        We omitted the type hints next to the parameters names.
        Usually you would write something like `param1 (int): ...`,
        but `mkdocstrings` gets the type information from the signature, so it's not needed here.

    Exceptions are written the same.

    Raises:
        OSError: Explain when this error is thrown.
        RuntimeError: Explain as well.
          Multi-line description, etc.

    Let's see the return value section now.

    Returns:
        A description of the value that is returned.
        Again multiple lines are allowed. They will also be concatenated to one line,
        so do not use complex markup here.

    Note:
        Other words are supported:

        - `Args`, `Arguments`, `Params` and `Parameters` for the parameters.
        - `Raise`, `Raises`, `Except`, and `Exceptions` for exceptions.
        - `Return` or `Returns` for return value.

        They are all case-insensitive, so you can write `RETURNS:` or `params:`.
    """
    return f"{param2}{param1}"
```

This docstring would be rendered like this (had to take two screenshots, so it's not perfectly aligned):

![image](https://user-images.githubusercontent.com/3999221/71548405-f41f6280-29ad-11ea-939e-d02a16232aa0.png)
![image](https://user-images.githubusercontent.com/3999221/71548413-ff728e00-29ad-11ea-95a5-d61e990be6c4.png)
