from typing import Literal


class Foo:
    @property
    def foo() -> Literal["hi"]:
        "hi"
        return "hi"
