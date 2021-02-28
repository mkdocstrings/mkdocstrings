"""Tests for the handlers.base module."""

import pytest
from markdown import Markdown

from mkdocstrings.handlers.base import Highlighter


@pytest.mark.parametrize("extension_name", ["codehilite", "pymdownx.highlight"])
def test_highlighter_without_pygments(extension_name):
    """Assert that it's possible to disable Pygments highlighting.

    Arguments:
        extension_name: The "user-chosen" Markdown extension for syntax highlighting.
    """
    configs = {extension_name: {"use_pygments": False, "css_class": "hiiii"}}
    md = Markdown(extensions=configs, extension_configs=configs)
    hl = Highlighter(md)
    assert (
        hl.highlight("import foo", language="python")
        == '<pre class="hiiii"><code class="language-python">import foo</code></pre>'
    )
    assert (
        hl.highlight("import foo", language="python", inline=True)
        == '<code class="hiiii language-python">import foo</code>'
    )


@pytest.mark.parametrize("extension_name", [None, "codehilite", "pymdownx.highlight"])
@pytest.mark.parametrize("inline", [False, True])
def test_highlighter_basic(extension_name, inline):
    """Assert that Pygments syntax highlighting works.

    Arguments:
        extension_name: The "user-chosen" Markdown extension for syntax highlighting.
        inline: Whether the highlighting was inline.
    """
    configs = {}
    if extension_name:
        configs[extension_name] = {}
    md = Markdown(extensions=configs, extension_configs=configs)
    hl = Highlighter(md)

    actual = hl.highlight("import foo", language="python", inline=inline)
    assert "import" in actual
    assert "import foo" not in actual  # Highlighting has split it up.
