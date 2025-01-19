# Troubleshooting

## Code blocks in admonitions (in docstrings or else) are not rendered correctly

To render code blocks in admonitions, you need to add the `pymdownx.superfences` extensions to the list of
Markdown extensions in `mkdocs.yml`. For example:

```markdown
!!! note
    Some text.

    ```bash
    echo "some code"
    ```
```

```yaml title="mkdocs.yml"
markdown_extensions:
- admonition
- codehilite
- pymdownx.superfences
```

For code blocks in docstrings, make sure to escape newlines (`\n` -> `\\n`),
or prefix the entire docstring with 'r' to make it a raw-docstring: `r"""`.
Indeed, docstrings are still strings and therefore subject to how Python parses strings.

## Footnotes are duplicated or overridden

Before version 0.14, footnotes could be duplicated over a page.
Please upgrade to version 0.14 or higher.

See also:

- [Issue #186](https://github.com/mkdocstrings/mkdocstrings/issues/186)
- [Tabs in docstrings (from `pymdownx.tabbed`) are not working properly](#tabs-in-docstrings-from-pymdownxtabbed-are-not-working-properly).

## MkDocs warns me about links to unfound documentation files

A warning like this one:

> WARNING -  Documentation file 'reference/parsers/docstrings.md'
  contains a link to 'reference/parsers/pytkdocs.parsers.docstrings.Section'
  which is not found in the documentation files.

...generally means you used parentheses `()` instead of brackets `[]` for a cross-reference.
Notice the dots in `reference/parsers/pytkdocs.parsers.docstrings.Section`?
It shows that it's probably a cross-reference, not a direct link.
It's probably written like `[Section](pytkdocs.parsers.docstrings.Section)` in the docs,
when it should be `[Section][pytkdocs.parsers.docstrings.Section]`.

## Some objects are not rendered (they do not appear in the generated docs)

- Make sure the configuration options of the handler are correct.
  Check the documentation for [Handlers](usage/handlers.md) to see the available options for each handler.
- Also make sure your documentation in your source code is formatted correctly.
  For Python code, check the [supported docstring styles](https://mkdocstrings.github.io/python/usage/#supported-docstrings-styles) page.
- Re-run the Mkdocs command with `-v`, and carefully read any traceback.

## Tabs in docstrings (from `pymdownx.tabbed`) are not working properly

Before version 0.14, multiple tab blocks injected on the same page
would result in broken links: clicking on a tab would bring the user to the wrong one.
Please upgrade to version 0.14 or higher.

See also:

- [Issue #193](https://github.com/mkdocstrings/mkdocstrings/issues/193)
- [Footnotes are duplicated or overridden](#footnotes-are-duplicated-or-overridden).

If you are stuck on a version before 0.14,
and want to use multiple tab blocks in one page,
use this workaround.

??? example "JavaScript workaround"

    Put the following code in a .js file,
    and list it in MkDocs' `extra_javascript`:

    ```javascript
    // Credits to Nikolaos Zioulis (@zuru on GitHub)
    function setID(){
        var tabs = document.getElementsByClassName("tabbed-set");
        for (var i = 0; i < tabs.length; i++) {
            children = tabs[i].children;
            var counter = 0;
            var iscontent = 0;
            for(var j = 0; j < children.length;j++){
                if(typeof children[j].htmlFor === 'undefined'){
                    if((iscontent + 1) % 2 == 0){
                        // check if it is content
                        if(iscontent == 1){
                            btn = children[j].childNodes[1].getElementsByTagName("button");
                        }
                    }
                    else{
                        // if not change the id
                        children[j].id = "__tabbed_" + String(i + 1) + "_" + String(counter + 1);
                        children[j].name = "__tabbed_" + String(i + 1);
                        // make default tab open
                        if(j == 0)
                            children[j].click();
                    }
                    iscontent++;
                }
                else{
                    // link to the correct tab
                    children[j].htmlFor = "__tabbed_" + String(i+1) + "_" + String(counter + 1);
                    counter ++;
                }
            }
        }
    }
    setID();
    ```

    This code will correctly reset the IDs for tabs on a same page.

## The generated documentation does not look good

Please open an ticket on the [bugtracker][bugtracker] with a detailed
explanation and screenshots of the bad-looking parts.
Note that you can always [customize the look](usage/theming.md) of *mkdocstrings* blocks -- through both HTML and CSS.

## Warning: could not find cross-reference target

TIP: **New in version 0.15.**  
Cross-linking used to include any Markdown heading, but now it's only for *mkdocstrings* identifiers by default.
See [Cross-references to any Markdown heading](usage/index.md#cross-references-to-any-markdown-heading) to opt back in.

Make sure the referenced object is properly rendered: verify your configuration options.

For false-positives, you can wrap the text in backticks (\`) to prevent `mkdocstrings` from trying to process it.

---

## Python specifics

### Nothing is rendered at all

Is your package available in the Python path?

See [Python handler: Finding modules](https://mkdocstrings.github.io/python/usage/#finding-modules).

### LaTeX in docstrings is not rendered correctly

If you are using a Markdown extension like
[Arithmatex Mathjax](https://squidfunk.github.io/mkdocs-material/setup/extensions/python-markdown-extensions/#arithmatex)
or [`markdown-katex`][markdown-katex] to render LaTeX,
add `r` in front of your docstring to make sure nothing is escaped.
You'll still maybe have to play with escaping to get things right.

Example:

```python
def math_function(x, y):
    r"""
    Look at these formulas:

    ```math
    f(x) = \int_{-\infty}^\infty
    \hat f(\xi)\,e^{2 \pi i \xi x}
    \,d\xi
    ```
    """
```

### My docstrings in comments (`#:`) are not picked up

We only support docstrings in comments through the [griffe-sphinx](https://mkdocstrings.github.io/griffe-sphinx) extension.

Alternatively, instead of:

```python
import enum


class MyEnum(enum.Enum):
    v1 = 1  #: The first choice.
    v2 = 2  #: The second choice.
```

You can use:

```python
import enum


class MyEnum(enum.Enum):
    v1 = 1
    """The first choice."""

    v2 = 2
    """The second choice."""
```

Or:

```python
import enum


class MyEnum(enum.Enum):
    """My enum.

    Attributes:
        v1: The first choice.
        v2: The second choice.
    """

    v1 = 1
    v2 = 2
```

### My wrapped function shows documentation/code for its wrapper instead of its own

Use [`functools.wraps()`](https://docs.python.org/3.6/library/functools.html#functools.wraps):

```python
from functools import wraps


def my_decorator(function):
    """The decorator docs."""

    @wraps(function)
    def wrapped_function(*args, **kwargs):
        print("hello")
        function(*args, **kwargs)
        print("bye")

    return wrapped_function


@my_decorator
def my_function(*args, **kwargs):
    """The function docs."""
    print(*args, **kwargs)
```

### Footnotes do not render

The library that parses docstrings, [Griffe](https://mkdocstrings.github.io/griffe/), splits docstrings in several "sections" (example: [Google-style sections syntax](https://mkdocstrings.github.io/griffe/reference/docstrings/#google-syntax)). If a footnote is used in a section, while referenced in another, mkdocstrings won't be able to render it correctly. The footnote and its reference must appear in the same section.

```python
def my_function():
    """Summary.

    This is the first section[^1].

    Note:
        This is the second section[^2].

    Note:
        This is the third section[^3].

    References at the end are part of yet another section (fourth here)[^4].

    [^1]: Some text.
    [^2]: Some text.
    [^3]: Some text.
    [^4]: Some text.
    """
```

Here only the fourth footnote will work, because it is the only one that appear in the same section as its reference. To fix this, make sure all footnotes appear in the same section as their references:

```python
def my_function():
    """Summary.

    This is the first section[^1].

    [^1]: Some text.

    Note:
        This is the second section[^2].

        [^2]: Some text.

    Note:
        This is the third section[^3].
    
        [^3]: Some text.

    References at the end are part of yet another section (fourth here)[^4].

    [^4]: Some text.
    """
```

### Submodules are not rendered

In previous versions of mkdocstrings-python, submodules were rendered by default. This was changed and you now need to set the following option:

```yaml title="mkdocs.yml"
plugins:
- mkdocstrings:
    handlers:
      python:
        options:
          show_submodules: true
```

[bugtracker]: https://github.com/mkdocstrings/mkdocstrings
[markdown-katex]: https://gitlab.com/mbarkhau/markdown-katex
