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

```yaml
# mkdocs.yml
markdown_extensions:
  - admonition
  - codehilite
  - pymdownx.superfences
```

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

- Make sure the configuration options of the handler for both selection and rendering are correct.
  Check the documentation for [Handlers](handlers/overview.md) to see the available options for each handler.
- Also make sure your documentation in your source code is formatted correctly.
  For Python code, check the [supported docstring styles](handlers/python.md#supported-docstrings-styles) page.
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

Are you using the Material theme?

- "No": We do not support any other theme yet.
  Check the [bugtracker][bugtracker] to see if there is a feature request
  asking to support your theme. If you find one, vote with a thumbs up. If not, you can open a ticket.
- "Yes": Please open an ticket on the [bugtracker][bugtracker] with a detailed
  explanation and screenshots of the bad-looking parts.

Note that you can always [customize the look](theming.md) of *mkdocstrings* blocks -- through both HTML and CSS.

## Warning: could not find cross-reference target

!!! important "New in version 0.15"
    Cross-linking used to include any Markdown heading, but now it's only for *mkdocstrings* identifiers by default.
    See [Cross-references to any Markdown heading](usage.md#cross-references-to-any-markdown-heading) to opt back in.

Make sure the referenced object was both collected and rendered: verify your selection and rendering options.

For false-positives, you can wrap the text in backticks (\`) to prevent `mkdocstrings` from trying to process it.

## WindowsPath object is not iterable

If you get a traceback like this one:

```
...
File "c:\users\me\appdata\local\continuum\anaconda3\lib\site-packages\mkdocstrings\handlers\python.py", line 244, in get_handler
  return PythonHandler(collector=PythonCollector(), renderer=PythonRenderer("python", theme))
File "c:\users\me\appdata\local\continuum\anaconda3\lib\site-packages\mkdocstrings\handlers\__init__.py", line 124, in __init__
  self.env = Environment(autoescape=True, loader=FileSystemLoader(theme_dir))
File "c:\users\me\appdata\local\continuum\anaconda3\lib\site-packages\jinja2\loaders.py", line 163, in __init__
  self.searchpath = list(searchpath)
TypeError: 'WindowsPath' object is not iterable
```

Try upgrading your installed version of Jinja2:

```
pip install -U jinja2
```

Version 2.11.1 seems to be working fine.

---

## Python specifics

### Nothing is rendered at all

Is your package available in the Python path?

See [Python handler: Finding modules](handlers/python.md#finding-modules).

### LaTeX in docstrings is not rendered correctly

If you are using a Markdown extension like
[Arithmatex Mathjax](https://squidfunk.github.io/mkdocs-material/extensions/pymdown/#arithmatex-mathjax)
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

It's because [`pytkdocs`][pytkdocs] does not pick up documentation in comments.
To load documentation for modules, classes, methods and functions, it uses [`inspect`][inspect].
To load documentation for attributes, it uses [`ast`][ast] to parse the source code,
searching for pairs of nodes like `assignment`-`string`, and [`ast`][ast] does not parse comments.

So instead of:

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
    """My enum.
    
    Attributes:
        v1: The first choice.
        v2: The second choice.
    """
    v1 = 1
    v2 = 2
```

Or:

```python
import enum

class MyEnum(enum.Enum):
    v1 = 1
    """The first choice."""

    v2 = 2
    """The second choice."""
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

[bugtracker]: https://github.com/mkdocstrings/mkdocstrings
[pytkdocs]: https://github.com/pawamoy/pytkdocs
[inspect]: https://docs.python.org/3/library/inspect.html
[ast]: https://docs.python.org/3/library/ast.html
[markdown-katex]: https://gitlab.com/mbarkhau/markdown-katex
