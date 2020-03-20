## Documentation collection
*This page is a work in progress.*

### Docstrings format
Your docstrings must follow a particular format, otherwise `mkdocstrings` will throw an exception.
This will be improved to be more robust over time.

```python
from typing import Optional

def my_function(param1: int, param2: Optional[str] = None) -> str:
    """
    A short description of this function.

    A longer description of this function.
    You can use more lines.

        This is a code block,
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
