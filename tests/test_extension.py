"""Tests for the extension module."""
import copy
from contextlib import contextmanager
from textwrap import dedent

import pytest
from markdown import Markdown

from mkdocstrings.extension import MkdocstringsExtension
from mkdocstrings.handlers.base import Handlers


@contextmanager
def ext_markdown(**kwargs):
    """Yield a Markdown instance with MkdocstringsExtension, with config adjustments from **kwargs.

    Arguments:
        **kwargs: Changes to apply to the config, on top of the default config.

    Yields:
        A `markdown.Markdown` instance.
    """
    config = {
        "theme_name": "material",
        "mdx": [],
        "mdx_configs": {},
        "mkdocstrings": {"default_handler": "python", "custom_templates": None, "watch": [], "handlers": {}},
    }
    config.update(kwargs)
    config["mdx"].append("toc")  # Guaranteed to be added by MkDocs.
    original_config = copy.deepcopy(config)

    handlers = Handlers(config)
    extension = MkdocstringsExtension(config, handlers)
    config["mdx"].append(extension)
    original_config["mdx"].append(extension)

    yield Markdown(extensions=config["mdx"], extension_configs=config["mdx_configs"])
    handlers.teardown()

    assert config == original_config  # Inadvertent mutations would propagate to the outer doc!


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
    assert ">Foo</h3>" in output
    assert ">Bar</h5>" in output
    assert ">Baz</h6>" in output


def test_keeps_preceding_text():
    """Assert that autodoc is recognized in the middle of a block and preceding text is kept."""
    with ext_markdown() as md:
        output = md.convert("**preceding**\n::: tests.fixtures.headings")
    assert "<strong>preceding</strong>" in output
    assert ">Foo</h2>" in output
    assert ":::" not in output


def test_reference_inside_autodoc():
    """Assert cross-reference Markdown extension works correctly."""
    with ext_markdown() as md:
        output = md.convert("::: tests.fixtures.cross_reference")
    snippet = 'Link to <span data-mkdocstrings-identifier="something.Else">something.Else</span>.'
    assert snippet in output


def test_html_inside_heading():
    """Assert that headings don't double-escape HTML."""
    with ext_markdown() as md:
        output = md.convert("::: tests.fixtures.builtin")
    assert "=&lt;" in output
    assert "&amp;" not in output


@pytest.mark.parametrize(
    ("permalink_setting", "expect_permalink"),
    [
        ("@@@", "@@@"),
        ("TeSt", "TeSt"),
        (True, "&para;"),
    ],
)
def test_no_double_toc(permalink_setting, expect_permalink):
    """
    Assert that the 'toc' extension doesn't apply its modification twice.

    Arguments:
        permalink_setting: The 'permalink' setting of 'toc' extension.
        expect_permalink: Text of the permalink to search for in the output.
    """
    with ext_markdown(mdx_configs={"toc": {"permalink": permalink_setting}}) as md:
        output = md.convert(
            dedent(
                """
                # aa

                ::: tests.fixtures.headings
                    rendering:
                        show_root_toc_entry: false

                # bb
                """
            )
        )
    assert output.count(expect_permalink) == 5
    assert 'id="tests.fixtures.headings--foo"' in output
    assert md.toc_tokens == [  # noqa: E1101 (the member gets populated only with 'toc' extension)
        {
            "level": 1,
            "id": "aa",
            "name": "aa",
            "children": [
                {
                    "level": 2,
                    "id": "tests.fixtures.headings--foo",
                    "name": "Foo",
                    "children": [
                        {
                            "level": 4,
                            "id": "tests.fixtures.headings--bar",
                            "name": "Bar",
                            "children": [
                                {"level": 6, "id": "tests.fixtures.headings--baz", "name": "Baz", "children": []}
                            ],
                        }
                    ],
                }
            ],
        },
        {"level": 1, "id": "bb", "name": "bb", "children": []},
    ]
