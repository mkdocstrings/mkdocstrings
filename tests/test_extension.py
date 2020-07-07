from markdown import Markdown

from mkdocstrings.extension import MkdocstringsExtension


def test_render_html_escaped_sequences():
    config = {
        "theme_name": "material",
        "mdx": [],
        "mdx_configs": {},
        "mkdocstrings": {"default_handler": "python", "custom_templates": None, "watch": [], "handlers": {}},
    }
    md = Markdown(extensions=[MkdocstringsExtension(config)])
    md.convert("::: tests.fixtures.html_escaped_sequences")
