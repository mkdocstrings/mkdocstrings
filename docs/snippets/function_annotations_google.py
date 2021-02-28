from typing import Optional


def my_function(param1: int, param2: Optional[str] = None) -> str:
    """A short description of this function.

    Arguments:
        param1: An integer?
        param2: A string? If you have a long description,
            you can split it on multiple lines.
            Just remember to indent those lines consistently.

            Complex markup is supported in sections items.

                I'm a code block!
    """
    return f"{param2}{param1}"
