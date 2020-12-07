"""Tests for the extension module."""
from markdown import Markdown

from mkdocstrings.extension import MkdocstringsExtension
from mkdocstrings.handlers.base import Handlers

_DEFAULT_CONFIG = {  # noqa: WPS407 (mutable constant)
    "theme_name": "material",
    "mdx": [],
    "mdx_configs": {},
    "mkdocstrings": {"default_handler": "python", "custom_templates": None, "watch": [], "handlers": {}},
}


def test_render_html_escaped_sequences():
    """Assert HTML-escaped sequences are correctly parsed as XML."""
    config = _DEFAULT_CONFIG
    md = Markdown(extensions=[MkdocstringsExtension(config, Handlers(config))])
    md.convert("::: tests.fixtures.html_escaped_sequences")


def test_reference_inside_autodoc():
    """Assert cross-reference Markdown extension works correctly."""
    config = dict(_DEFAULT_CONFIG)
    ext = MkdocstringsExtension(config, Handlers(config))
    config["mdx"].append(ext)

    md = Markdown(extensions=[ext])

    output = md.convert("::: tests.fixtures.cross_reference")
    snippet = 'Link to <span data-mkdocstrings-identifier="something.Else">something.Else</span>.'
    assert snippet in output
