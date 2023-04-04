"""Tests for the extension module."""

from __future__ import annotations

import logging
import re
import sys
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from markdown import Markdown

    from mkdocstrings.plugin import MkdocstringsPlugin


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


@pytest.mark.skipif(sys.version_info < (3, 8), reason="typing.Literal requires Python 3.8")
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
                                {"level": 6, "id": "tests.fixtures.headings--baz", "name": "Baz", "children": []},
                            ],
                        },
                    ],
                },
            ],
        },
        {"level": 1, "id": "bb", "name": "bb", "children": []},
    ]


def test_use_custom_handler(ext_markdown: Markdown) -> None:
    """Assert that we use the custom handler declared in an individual autodoc instruction."""
    with pytest.raises(ModuleNotFoundError):
        ext_markdown.convert("::: tests.fixtures.headings\n    handler: not_here")


def test_dont_register_every_identifier_as_anchor(plugin: MkdocstringsPlugin, ext_markdown: Markdown) -> None:
    """Assert that we don't preemptively register all identifiers of a rendered object."""
    handler = plugin._handlers.get_handler("python")  # type: ignore[union-attr]
    ids = {"id1", "id2", "id3"}
    handler.get_anchors = lambda _: ids  # type: ignore[method-assign]
    ext_markdown.convert("::: tests.fixtures.headings")
    autorefs = ext_markdown.parser.blockprocessors["mkdocstrings"]._autorefs
    for identifier in ids:
        assert identifier not in autorefs._url_map
        assert identifier not in autorefs._abs_url_map


def test_use_deprecated_yaml_keys(ext_markdown: Markdown, caplog: pytest.LogCaptureFixture) -> None:
    """Check that using the deprecated 'selection' and 'rendering' YAML keys emits a deprecation warning."""
    caplog.set_level(logging.INFO)
    assert "h1" not in ext_markdown.convert("::: tests.fixtures.headings\n    rendering:\n      heading_level: 2")
    assert "single 'options' YAML key" in caplog.text


def test_use_new_options_yaml_key(ext_markdown: Markdown) -> None:
    """Check that using the new 'options' YAML key works as expected."""
    assert "h1" in ext_markdown.convert("::: tests.fixtures.headings\n    options:\n      heading_level: 1")
    assert "h1" not in ext_markdown.convert("::: tests.fixtures.headings\n    options:\n      heading_level: 2")
