"""Tests for the extension module."""
import re
import sys
from textwrap import dedent

import pytest


@pytest.mark.parametrize("ext_markdown", [{"markdown_extensions": [{"footnotes": {}}]}], indirect=["ext_markdown"])
def test_multiple_footnotes(ext_markdown):
    """Assert footnotes don't get added to subsequent docstrings."""
    output = ext_markdown.convert(
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


def test_markdown_heading_level(ext_markdown):
    """Assert that Markdown headings' level doesn't exceed heading_level."""
    output = ext_markdown.convert("::: tests.fixtures.headings\n    rendering:\n      show_root_heading: true")
    assert ">Foo</h3>" in output
    assert ">Bar</h5>" in output
    assert ">Baz</h6>" in output


def test_keeps_preceding_text(ext_markdown):
    """Assert that autodoc is recognized in the middle of a block and preceding text is kept."""
    output = ext_markdown.convert("**preceding**\n::: tests.fixtures.headings")
    assert "<strong>preceding</strong>" in output
    assert ">Foo</h2>" in output
    assert ":::" not in output


def test_reference_inside_autodoc(ext_markdown):
    """Assert cross-reference Markdown extension works correctly."""
    output = ext_markdown.convert("::: tests.fixtures.cross_reference")
    assert re.search(r"Link to <.*something\.Else.*>something\.Else<.*>\.", output)


@pytest.mark.skipif(sys.version_info < (3, 8), reason="typing.Literal requires Python 3.8")
def test_quote_inside_annotation(ext_markdown):
    """Assert that inline highlighting doesn't double-escape HTML."""
    output = ext_markdown.convert("::: tests.fixtures.string_annotation.Foo")
    assert ";hi&" in output
    assert "&amp;" not in output


def test_html_inside_heading(ext_markdown):
    """Assert that headings don't double-escape HTML."""
    output = ext_markdown.convert("::: tests.fixtures.html_tokens")
    assert "&#39;&lt;" in output
    assert "&amp;" not in output


@pytest.mark.parametrize(
    ("ext_markdown", "expect_permalink"),
    [
        ({"markdown_extensions": [{"toc": {"permalink": "@@@"}}]}, "@@@"),
        ({"markdown_extensions": [{"toc": {"permalink": "TeSt"}}]}, "TeSt"),
        ({"markdown_extensions": [{"toc": {"permalink": True}}]}, "&para;"),
    ],
    indirect=["ext_markdown"],
)
def test_no_double_toc(ext_markdown, expect_permalink):
    """Assert that the 'toc' extension doesn't apply its modification twice."""
    output = ext_markdown.convert(
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
    assert ext_markdown.toc_tokens == [  # noqa: E1101 (the member gets populated only with 'toc' extension)
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


def test_use_custom_handler(ext_markdown):
    """Assert that we use the custom handler declared in an individual autodoc instruction."""
    with pytest.raises(ModuleNotFoundError):
        ext_markdown.convert("::: tests.fixtures.headings\n    handler: not_here")


def test_dont_register_every_identifier_as_anchor(plugin):
    """Assert that we don't preemptively register all identifiers of a rendered object."""
    renderer = plugin._handlers.get_handler("python").renderer  # noqa: WPS437
    ids = {"id1", "id2", "id3"}
    renderer.get_anchors = lambda _: ids
    plugin.md.convert("::: tests.fixtures.headings")
    autorefs = plugin.md.parser.blockprocessors["mkdocstrings"]._autorefs  # noqa: WPS219,WPS437
    for identifier in ids:
        assert identifier not in autorefs._url_map  # noqa: WPS437
        assert identifier not in autorefs._abs_url_map  # noqa: WPS437
