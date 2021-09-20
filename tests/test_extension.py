"""Tests for the extension module."""
import re
import sys
from collections import ChainMap
from textwrap import dedent

import pytest
from markdown import Markdown
from mkdocs import config

try:
    from mkdocs.config.defaults import get_schema
except ImportError:

    def get_schema():  # noqa: WPS440
        """Fallback for old versions of MkDocs."""
        return config.DEFAULT_SCHEMA


@pytest.fixture(name="ext_markdown")
def fixture_ext_markdown(request, tmp_path):
    """Yield a Markdown instance with MkdocstringsExtension, with config adjustments."""
    conf = config.Config(schema=get_schema())

    conf_dict = {
        "site_name": "foo",
        "site_url": "https://example.org/",
        "site_dir": str(tmp_path),
        "plugins": [{"mkdocstrings": {"default_handler": "python"}}],
        **getattr(request, "param", {}),
    }
    # Re-create it manually as a workaround for https://github.com/mkdocs/mkdocs/issues/2289
    mdx_configs = dict(ChainMap(*conf_dict.get("markdown_extensions", [])))

    conf.load_dict(conf_dict)
    assert conf.validate() == ([], [])

    conf["mdx_configs"] = mdx_configs
    conf["markdown_extensions"].insert(0, "toc")  # Guaranteed to be added by MkDocs.

    conf = conf["plugins"]["mkdocstrings"].on_config(conf)
    conf = conf["plugins"]["autorefs"].on_config(conf)
    md = Markdown(extensions=conf["markdown_extensions"], extension_configs=conf["mdx_configs"])
    yield md
    conf["plugins"]["mkdocstrings"].on_post_build(conf)


def test_render_html_escaped_sequences(ext_markdown):
    """Assert HTML-escaped sequences are correctly parsed as XML."""
    ext_markdown.convert("::: tests.fixtures.html_escaped_sequences")


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
    output = ext_markdown.convert("::: tests.fixtures.builtin")
    assert "=&lt;" in output
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
