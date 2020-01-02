from mkdocstrings.documenter import Documenter


def test_getattr_dunder():
    class Base:
        def __init__(self):
            pass

        def __getitem__(self, item):
            """Written docstring."""
            return item

    class Child(Base):
        def __init__(self):
            super().__init__()

        def __getitem__(self, item):
            return item

    doc = Documenter()
    class_doc = doc.get_class_documentation(Child)
    for child in class_doc.children:
        if child.name == "__getitem__":
            assert child.docstring.original_value == ""


def test_no_filter():
    doc = Documenter()
    assert not doc.filter_name_out("hello")


def test_filter():
    doc = Documenter(["!^_[^_]", "!^__C$"])
    assert doc.filter_name_out("_B")
    assert doc.filter_name_out("__C")
    assert not doc.filter_name_out("__A")
