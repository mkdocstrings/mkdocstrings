# Troubleshooting

## The generated documentation does not look good

Are you using the Material theme?

- "No": We do not support any other theme yet.
  Check the [bugtracker](https://github.com/pawamoy/mkdocstrings) to see if there is a feature request
  asking to support your theme. If you find one, vote with a thumbs up. If not, you can open a ticket.
- "Yes": Please open an ticket on the [bugtracker](https://github.com/pawamoy/mkdocstrings) with a detailed
  explanation and screenshots of the bad-looking parts.

## Some objects are not rendered (they do not appear in the generated docs)

- Make sure the configuration options of the handler for both selection and rendering are correct.
  Check the documentation for [Handlers](/handlers/overview) to see the available options for each handler.
- Also make sure your documentation in your source code is formatted correctly.
  For Python code, check the [docstring format](/handlers/python/#docstring-format) page.
- Check the output of the `mkdocs` command, and re-run it with `-v` if necessary.
  Warnings should appear, showing errors that happened during collection.

## Nothing is rendered at all

Python?

- "No": we only support Python right now.
- "Yes": is your package available in the Python path?
  If not, install it in your current virtualenv and try again.
  Make sure you don't have an old version of your package installed,
  shadowing your source code. 

## Python specifics

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
