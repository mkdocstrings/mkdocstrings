"""Tests for the extension module."""
from contextlib import contextmanager
from textwrap import dedent

from markdown import Markdown

from mkdocstrings.extension import MkdocstringsExtension
from mkdocstrings.handlers.base import Handlers


@contextmanager
def ext_markdown(**kwargs):
    """Yield a Markdown instance with MkdocstringsExtension, with config adjustments from **kwargs."""
    config = {
        "theme_name": "material",
        "mdx": [],
        "mdx_configs": {},
        "mkdocstrings": {"default_handler": "python", "custom_templates": None, "watch": [], "handlers": {}},
    }
    config.update(kwargs)
    handlers = Handlers(config)
    config["mdx"].append(MkdocstringsExtension(config, handlers))
    yield Markdown(extensions=config["mdx"], extension_configs=config["mdx_configs"])
    handlers.teardown()


def test_render_html_escaped_sequences():
    """Assert HTML-escaped sequences are correctly parsed as XML."""
    with ext_markdown() as md:
        md.convert("::: tests.fixtures.html_escaped_sequences")


def test_multiple_footnotes():
    """Assert footnotes don't get added to subsequent docstrings."""
    with ext_markdown(mdx=["footnotes"]) as md:
        output = md.convert(
            dedent(
                """
                Top.[^aaa]

                ::: tests.fixtures.footnotes.func_a

                ::: tests.fixtures.footnotes.func_b

                ::: tests.fixtures.footnotes.func_c

                [^aaa]: Top footnote
                """,
            ),
        )
    assert output.count("Footnote A") == 1
    assert output.count("Footnote B") == 1
    assert output.count("Top footnote") == 1


def test_markdown_heading_level():
    """Assert that Markdown headings' level doesn't exceed heading_level."""
    with ext_markdown() as md:
        output = md.convert("::: tests.fixtures.headings\n    rendering:\n      show_root_heading: true")
    assert "<h3>Foo</h3>" in output
    assert "<h5>Bar</h5>" in output
    assert "<h6>Baz</h6>" in output


def test_keeps_preceding_text():
    """Assert that autodoc is recognized in the middle of a block and preceding text is kept."""
    with ext_markdown() as md:
        output = md.convert("**preceding**\n::: tests.fixtures.headings")
    assert "<strong>preceding</strong>" in output
    assert "<h2>Foo</h2>" in output
    assert ":::" not in output


def test_reference_inside_autodoc():
    """Assert cross-reference Markdown extension works correctly."""
    with ext_markdown() as md:
        output = md.convert("::: tests.fixtures.cross_reference")
    snippet = 'Link to <span data-mkdocstrings-identifier="something.Else">something.Else</span>.'
    assert snippet in output


def test_no_double_toc():
    """Asserts that the 'toc' extension doesn't apply its modification twice."""
    with ext_markdown(mdx=["toc"], mdx_configs={"toc": {"permalink": "@@@"}}) as md:
        output = md.convert("::: tests.fixtures.headings")
    assert 3 <= output.count("@@@") < 6
