from typing import Optional


def my_function(param1: int, param2: Optional[str] = None) -> str:
    """A short description of this function.

    Complex markup is supported in the main description section.

        I'm a code block!

    :param param1: An integer?
    :param param2: A string? If you have a long description,
        you can split it on multiple lines.
    """
    return f"{param2}{param1}"
