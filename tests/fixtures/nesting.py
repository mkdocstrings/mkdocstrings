class Class:
    """A class.
    
    ## ::: tests.fixtures.nesting.Class.method
        options:
            show_root_heading: true
    """

    def method(self) -> None:
        """A method."""


class CodeExamples:
    """Code around a nested directive.

    ```python
    print("parent before")
    ```

    ::: tests.fixtures.nesting.CodeExamples.method
        options:
            show_source: false

    ```python
    print("parent after")
    ```
    """

    def method(self) -> None:
        """Code around another nested directive.

        ```python
        print("child before")
        ```

        ::: tests.fixtures.nesting.CodeExamples.leaf
            options:
                show_source: false

        ```python
        print("child after")
        ```
        """

    def leaf(self) -> None:
        """Code in the innermost directive.

        ```python
        print("leaf")
        ```
        """
