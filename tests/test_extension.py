"""Tests for the extension module."""

from __future__ import annotations

import re
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from markdown import Markdown

    from mkdocstrings import MkdocstringsPlugin


@pytest.mark.parametrize("ext_markdown", [{"markdown_extensions": [{"footnotes": {}}]}], indirect=["ext_markdown"])
def test_multiple_footnotes(ext_markdown: Markdown) -> None:
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


def test_markdown_heading_level(ext_markdown: Markdown) -> None:
    """Assert that Markdown headings' level doesn't exceed heading_level."""
    output = ext_markdown.convert("::: tests.fixtures.headings\n    options:\n      show_root_heading: true")
    assert ">Foo</h3>" in output
    assert ">Bar</h5>" in output
    assert ">Baz</h6>" in output


def test_keeps_preceding_text(ext_markdown: Markdown) -> None:
    """Assert that autodoc is recognized in the middle of a block and preceding text is kept."""
    output = ext_markdown.convert("**preceding**\n::: tests.fixtures.headings")
    assert "<strong>preceding</strong>" in output
    assert ">Foo</h2>" in output
    assert ":::" not in output


def test_reference_inside_autodoc(ext_markdown: Markdown) -> None:
    """Assert cross-reference Markdown extension works correctly."""
    output = ext_markdown.convert("::: tests.fixtures.cross_reference")
    assert re.search(r"Link to <.*something\.Else.*>something\.Else<.*>\.", output)


def test_quote_inside_annotation(ext_markdown: Markdown) -> None:
    """Assert that inline highlighting doesn't double-escape HTML."""
    output = ext_markdown.convert("::: tests.fixtures.string_annotation.Foo")
    assert ";hi&" in output
    assert "&amp;" not in output


def test_html_inside_heading(ext_markdown: Markdown) -> None:
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
def test_no_double_toc(ext_markdown: Markdown, expect_permalink: str) -> None:
    """Assert that the 'toc' extension doesn't apply its modification twice."""
    output = ext_markdown.convert(
        dedent(
            """
            # aa

            ::: tests.fixtures.headings
                options:
                    show_root_toc_entry: false

            # bb
            """,
        ),
    )
    assert output.count(expect_permalink) == 5
    assert 'id="tests.fixtures.headings--foo"' in output
    assert ext_markdown.toc_tokens == [  # type: ignore[attr-defined]  # the member gets populated only with 'toc' extension
        {
            "level": 1,
            "id": "aa",
            "html": "aa",
            "name": "aa",
            "data-toc-label": "",
            "children": [
                {
                    "level": 2,
                    "id": "tests.fixtures.headings--foo",
                    "html": "Foo",
                    "name": "Foo",
                    "data-toc-label": "",
                    "children": [
                        {
                            "level": 4,
                            "id": "tests.fixtures.headings--bar",
                            "html": "Bar",
                            "name": "Bar",
                            "data-toc-label": "",
                            "children": [
                                {
                                    "level": 6,
                                    "id": "tests.fixtures.headings--baz",
                                    "html": "Baz",
                                    "name": "Baz",
                                    "data-toc-label": "",
                                    "children": [],
                                },
                            ],
                        },
                    ],
                },
            ],
        },
        {
            "level": 1,
            "id": "bb",
            "html": "bb",
            "name": "bb",
            "data-toc-label": "",
            "children": [],
        },
    ]


def test_use_custom_handler(ext_markdown: Markdown) -> None:
    """Assert that we use the custom handler declared in an individual autodoc instruction."""
    with pytest.raises(ModuleNotFoundError):
        ext_markdown.convert("::: tests.fixtures.headings\n    handler: not_here")


def test_register_every_identifier_alias(plugin: MkdocstringsPlugin, ext_markdown: Markdown) -> None:
    """Assert that we don't preemptively register all identifiers of a rendered object."""
    handler = plugin._handlers.get_handler("python")  # type: ignore[union-attr]
    ids = ("id1", "id2", "id3")
    handler.get_aliases = lambda _: ids  # type: ignore[method-assign]
    autorefs = ext_markdown.parser.blockprocessors["mkdocstrings"]._autorefs  # type: ignore[attr-defined]

    class Page:
        url = "foo"

    autorefs.current_page = Page()
    ext_markdown.convert("::: tests.fixtures.headings")
    for identifier in ids:
        assert identifier in autorefs._secondary_url_map


def test_use_options_yaml_key(ext_markdown: Markdown) -> None:
    """Check that using the 'options' YAML key works as expected."""
    assert "h1" in ext_markdown.convert("::: tests.fixtures.headings\n    options:\n      heading_level: 1")
    assert "h1" not in ext_markdown.convert("::: tests.fixtures.headings\n    options:\n      heading_level: 2")


def test_use_yaml_options_after_blank_line(ext_markdown: Markdown) -> None:
    """Check that YAML options are detected even after a blank line."""
    assert "h1" not in ext_markdown.convert("::: tests.fixtures.headings\n\n    options:\n      heading_level: 2")


@pytest.mark.parametrize("ext_markdown", [{"markdown_extensions": [{"admonition": {}}]}], indirect=["ext_markdown"])
def test_removing_duplicated_headings(ext_markdown: Markdown) -> None:
    """Assert duplicated headings are removed from the output."""
    output = ext_markdown.convert(
        dedent(
            """
            ::: tests.fixtures.headings_many.heading_1

            !!! note

                ::: tests.fixtures.headings_many.heading_2

            ::: tests.fixtures.headings_many.heading_3
            """,
        ),
    )
    assert output.count(">Heading one<") == 1
    assert output.count(">Heading two<") == 1
    assert output.count(">Heading three<") == 1


def _assert_contains_in_order(items: list[str], string: str) -> None:
    index = 0
    for item in items:
        assert item in string[index:]
        index = string.index(item, index) + len(item)


@pytest.mark.parametrize("ext_markdown", [{"markdown_extensions": [{"attr_list": {}}]}], indirect=["ext_markdown"])
def test_backup_of_anchors(ext_markdown: Markdown) -> None:
    """Anchors with empty `href` are backed up."""
    output = ext_markdown.convert("::: tests.fixtures.markdown_anchors")

    # Anchors with id and no href have been backed up and updated.
    _assert_contains_in_order(
        [
            'id="anchor"',
            'id="tests.fixtures.markdown_anchors--anchor"',
            'id="heading-anchor-1"',
            'id="tests.fixtures.markdown_anchors--heading-anchor-1"',
            'id="heading-anchor-2"',
            'id="tests.fixtures.markdown_anchors--heading-anchor-2"',
            'id="heading-anchor-3"',
            'id="tests.fixtures.markdown_anchors--heading-anchor-3"',
        ],
        output,
    )

    # Anchors with href and with or without id have been updated but not backed up.
    _assert_contains_in_order(
        [
            'id="tests.fixtures.markdown_anchors--with-id"',
        ],
        output,
    )
    assert 'id="with-id"' not in output

    _assert_contains_in_order(
        [
            'href="#tests.fixtures.markdown_anchors--has-href1"',
            'href="#tests.fixtures.markdown_anchors--has-href2"',
        ],
        output,
    )
    assert 'href="#has-href1"' not in output
    assert 'href="#has-href2"' not in output
