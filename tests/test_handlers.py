"""Tests for the handlers.base module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from jinja2.exceptions import TemplateNotFound
from markdown import Markdown

from mkdocstrings.handlers.base import Highlighter

if TYPE_CHECKING:
    from pathlib import Path

    from mkdocstrings.plugin import MkdocstringsPlugin


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
    handler = plugin._handlers.get_handler("python")  # type: ignore[union-attr]

    # monkeypatch Jinja env search path
    search_paths = [
        base_theme := tmp_path / "base_theme",
        base_fallback_theme := tmp_path / "base_fallback_theme",
        extended_theme := tmp_path / "extended_theme",
        extended_fallback_theme := tmp_path / "extended_fallback_theme",
    ]
    handler.env.loader.searchpath = search_paths  # type: ignore[union-attr]

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
