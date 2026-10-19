# SPDX-License-Identifier: ISC
#
# ISC License
#
# Copyright (c) 2019, Timothée Mazzucotelli and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""Tests for the handlers.base module."""

from __future__ import annotations

import re
from html import escape, unescape
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest
from dirty_equals import IsStr
from jinja2.exceptions import TemplateNotFound
from markdown import Markdown

from mkdocstrings import Highlighter, MkdocstringsInnerExtension

if TYPE_CHECKING:
    from pathlib import Path

    from mkdocstrings import MkdocstringsPlugin


@pytest.mark.parametrize("extension_name", ["codehilite", "pymdownx.highlight"])
def test_highlighter_without_pygments(extension_name: str) -> None:
    """Assert that it's possible to disable Pygments highlighting.

    Arguments:
        extension_name: The "user-chosen" Markdown extension for syntax highlighting.
    """
    configs = {extension_name: {"use_pygments": False, "css_class": "hiiii"}}
    md = Markdown(extensions=[extension_name], extension_configs=configs)
    hl = Highlighter(md)
    assert (
        hl.highlight("import foo", language="python")
        == '<pre class="hiiii"><code class="language-python">import foo</code></pre>'
    )
    assert (
        hl.highlight("import foo", language="python", inline=True)
        == f'<code class="{"" if extension_name == "codehilite" else "hiiii"} language-python">import foo</code>'
    )


@pytest.mark.parametrize("extension_name", [None, "codehilite", "pymdownx.highlight"])
@pytest.mark.parametrize("inline", [False, True])
def test_highlighter_basic(extension_name: str | None, inline: bool) -> None:
    """Assert that Pygments syntax highlighting works.

    Arguments:
        extension_name: The "user-chosen" Markdown extension for syntax highlighting.
        inline: Whether the highlighting was inline.
    """
    md = Markdown(extensions=[extension_name], extension_configs={extension_name: {}}) if extension_name else Markdown()
    hl = Highlighter(md)

    actual = hl.highlight("import foo", language="python", inline=inline)
    assert "import" in actual
    assert "import foo" not in actual  # Highlighting has split it up.


def test_extended_templates(tmp_path: Path, plugin: MkdocstringsPlugin) -> None:
    """Test the extended templates functionality.

    Parameters:
        tmp_path: Temporary folder.
        plugin: Instance of our plugin.
    """
    handler = plugin._handlers.get_handler("python")  # ty:ignore[unresolved-attribute]

    # monkeypatch Jinja env search path
    search_paths = [
        base_theme := tmp_path / "base_theme",
        base_fallback_theme := tmp_path / "base_fallback_theme",
        extended_theme := tmp_path / "extended_theme",
        extended_fallback_theme := tmp_path / "extended_fallback_theme",
    ]
    handler.env.loader.searchpath = search_paths  # ty:ignore[invalid-assignment]

    # assert "new" template is not found
    with pytest.raises(expected_exception=TemplateNotFound):
        handler.env.get_template("new.html")

    # check precedence: base theme, base fallback theme, extended theme, extended fallback theme
    # start with last one and go back up
    handler.env.cache = None

    extended_fallback_theme.mkdir()
    extended_fallback_theme.joinpath("new.html").write_text("extended fallback new")
    assert handler.env.get_template("new.html").render() == "extended fallback new"

    extended_theme.mkdir()
    extended_theme.joinpath("new.html").write_text("extended new")
    assert handler.env.get_template("new.html").render() == "extended new"

    base_fallback_theme.mkdir()
    base_fallback_theme.joinpath("new.html").write_text("base fallback new")
    assert handler.env.get_template("new.html").render() == "base fallback new"

    base_theme.mkdir()
    base_theme.joinpath("new.html").write_text("base new")
    assert handler.env.get_template("new.html").render() == "base new"


@pytest.mark.parametrize(
    "ext_markdown",
    [{"markdown_extensions": [{"toc": {"permalink": True}}]}],
    indirect=["ext_markdown"],
)
def test_nested_autodoc(ext_markdown: Markdown) -> None:
    """Assert that nested autodocs render well and do not mess up the TOC."""
    output = ext_markdown.convert(
        dedent(
            """
            # ::: tests.fixtures.nesting.Class
                options:
                    members: false
                    show_root_heading: true
            """,
        ),
    )
    assert 'id="tests.fixtures.nesting.Class"' in output
    assert 'id="tests.fixtures.nesting.Class.method"' in output
    assert ext_markdown.toc_tokens == [  # ty:ignore[unresolved-attribute]
        {
            "level": 1,
            "id": "tests.fixtures.nesting.Class",
            "html": IsStr(),
            "name": "Class",
            "data-toc-label": "Class",
            "children": [
                {
                    "level": 2,
                    "id": "tests.fixtures.nesting.Class.method",
                    "html": IsStr(),
                    "name": "method",
                    "data-toc-label": "method",
                    "children": [],
                },
            ],
        },
    ]


@pytest.mark.parametrize(("line_spans", "line_anchors"), [("__span", ""), ("custom-span", "custom-line")])
@pytest.mark.parametrize("linenums_style", ["table", "inline"])
@pytest.mark.parametrize("highlighted_html", [False, True])
def test_code_ids_are_prefixed(
    line_spans: str,
    line_anchors: str,
    linenums_style: str,
    highlighted_html: bool,
    plugin: MkdocstringsPlugin,
) -> None:
    """Prefix code line IDs and links in fenced examples and highlighted source HTML."""
    md = Markdown(
        extensions=["toc", "pymdownx.highlight", "pymdownx.superfences", MkdocstringsInnerExtension([])],
        extension_configs={
            "pymdownx.highlight": {
                "anchor_linenums": True,
                "line_spans": line_spans,
                "line_anchors": line_anchors,
                "linenums_style": linenums_style,
            },
        },
    )
    handler = plugin._handlers.get_handler("python")  # ty:ignore[unresolved-attribute]
    handler._md = md
    highlighter = Highlighter(md)
    code = "print('<a id=\"literal\"> & text')"

    # Reuse the converter and highlighter across objects, then render without a parent ID.
    for html_id in ("first", "second", 'object"&', ""):
        prefix = html_id and html_id + "--"
        if highlighted_html:
            html = str(highlighter.highlight(code, language="python", linenums=True, linestart=1, id_prefix=prefix))
        else:
            html = str(
                handler.do_convert_markdown(f'```python linenums="1"\n{code}\n```', heading_level=0, html_id=html_id),
            )

        # Span IDs, anchor IDs, legacy names, and links must all use the same object prefix.
        span_id = f"{prefix}{line_spans}-0-1"
        anchor_id = f"{prefix}{line_anchors or '__codelineno'}-0-1"
        assert f'id="{escape(span_id)}"' in html
        assert f'id="{escape(anchor_id)}"' in html
        assert f'name="{escape(anchor_id)}"' in html
        assert f'href="#{escape(anchor_id)}"' in html
        ids = re.findall(r' id="([^"]+)"', html)
        assert len(ids) == len(set(ids))

        # HTML-like strings inside code are text, even when they contain an ID attribute.
        assert code in unescape(re.sub(r"<[^>]+>", "", html))


def test_code_id_prefixing_preserves_raw_html(plugin: MkdocstringsPlugin) -> None:
    """Keep heading prefixes while leaving manually authored code HTML untouched."""
    md = Markdown(
        extensions=["toc", "pymdownx.highlight", "pymdownx.superfences", MkdocstringsInnerExtension([])],
        extension_configs={"pymdownx.highlight": {"anchor_linenums": True}},
    )
    handler = plugin._handlers.get_handler("python")  # ty:ignore[unresolved-attribute]
    handler._md = md
    markdown = dedent(
        """
        # Details

        [Details](#details).

        <pre><span title='a > b' id='line'><a id="anchor" name="anchor"></a><a href="#anchor">1</a><a href="https://example.org/#anchor">external</a></span></pre>
        """,
    )

    html = handler.do_convert_markdown(markdown, heading_level=0, html_id="object")

    assert 'id="object--details"' in html
    assert 'href="#object--details"' in html
    assert "<span title='a > b' id='line'>" in html
    assert 'id="anchor"' in html
    assert 'name="anchor"' in html
    assert 'href="#anchor"' in html
    assert 'href="https://example.org/#anchor"' in html


@pytest.mark.parametrize("highlighted_html", [False, True])
@pytest.mark.parametrize(
    "settings",
    [
        {},
        {"linenums": True},
        {"linenums": False},
        {"use_pygments": False, "line_spans": "span", "line_anchors": "line", "anchor_linenums": True},
    ],
)
def test_code_without_generated_ids_stays_without_ids(
    settings: dict[str, bool | str],
    highlighted_html: bool,
    plugin: MkdocstringsPlugin,
) -> None:
    """Keep disabled spans and anchors disabled when an object prefix is provided."""
    # Highlight settings work even when its extension is registered after the inner extension.
    md = Markdown(
        extensions=["toc", MkdocstringsInnerExtension([]), "pymdownx.highlight", "pymdownx.superfences"],
        extension_configs={"pymdownx.highlight": settings},
    )
    handler = plugin._handlers.get_handler("python")  # ty:ignore[unresolved-attribute]
    handler._md = md

    # A fence or highlight call can request line numbers without enabling line IDs.
    if highlighted_html:
        html = str(
            Highlighter(md).highlight("print(1)", language="python", linenums=True, linestart=1, id_prefix="object--"),
        )
    else:
        fence_options = ' linenums="1"' if settings.get("use_pygments", True) else ""
        html = str(
            handler.do_convert_markdown(f"```python{fence_options}\nprint(1)\n```", heading_level=0, html_id="object"),
        )

    assert "<pre" in html
    assert ' id="' not in html
    assert ' name="' not in html


def test_highlighter_restores_settings_after_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep prefixes and numbering from leaking out of a failed highlight call."""
    md = Markdown(
        extensions=["pymdownx.highlight"],
        extension_configs={"pymdownx.highlight": {"line_spans": "span", "anchor_linenums": True, "linenums": False}},
    )
    highlighter = Highlighter(md)

    # Fail after entering highlighting, while the object's temporary settings are active.
    def fail_to_load_lexer(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("lexer unavailable")

    with monkeypatch.context() as patch:
        patch.setattr(highlighter, "get_lexer", fail_to_load_lexer)
        with pytest.raises(RuntimeError, match="lexer unavailable"):
            highlighter.highlight("print(1)", language="python", linenums=True, id_prefix="failed--")

    # The same highlighter still uses its original IDs and invisible anchors on the next call.
    html = highlighter.highlight("print(1)", language="python")

    assert 'id="span-0-1"' in html
    assert 'id="__codelineno-0-1"' in html
    assert 'href="#__codelineno-0-1"' in html
    assert "failed--" not in html
    assert 'class="linenos"' not in html


@pytest.mark.parametrize(
    "ext_markdown",
    [
        {"markdown_extensions": [{"pymdownx.highlight": settings}, {"pymdownx.superfences": {}}]}
        for settings in (
            {"line_spans": "span"},
            {"line_anchors": "line"},
            {"anchor_linenums": True, "linenums": False},
            {"anchor_linenums": True, "linenums": True, "linenums_style": "table"},
            {"anchor_linenums": True, "linenums": True, "linenums_style": "inline"},
        )
    ],
    indirect=["ext_markdown"],
)
def test_nested_autodoc_code_ids(ext_markdown: Markdown) -> None:
    """Keep each object's code IDs and links through multiple nested directives."""
    output = ext_markdown.convert(
        dedent(
            """
            ::: tests.fixtures.nesting.CodeExamples
                options:
                    members: false
                    show_source: false
            """,
        ),
    )

    # Parent and child examples on both sides of a directive keep their own prefix.
    root_id = "tests.fixtures.nesting.CodeExamples"
    ids = re.findall(r' id="([^"]+)"', output)
    code_ids = [identifier for identifier in ids if "--" in identifier]
    assert len(code_ids) == 5
    assert sum(identifier.startswith(f"{root_id}--") for identifier in code_ids) == 2
    assert sum(identifier.startswith(f"{root_id}.method--") for identifier in code_ids) == 2
    assert sum(identifier.startswith(f"{root_id}.leaf--") for identifier in code_ids) == 1
    assert all(identifier.count("--") == 1 for identifier in code_ids)
    assert len(code_ids) == len(set(code_ids))

    # Both visible number links and invisible anchors still point at the matching line.
    for target in re.findall(r' href="#([^"]+)"', output):
        if "--" in target:
            assert target in code_ids
