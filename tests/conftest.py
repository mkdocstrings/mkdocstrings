"""Configuration for the pytest test suite."""

from collections import ChainMap

import pytest
from markdown.core import Markdown
from mkdocs import config

try:
    from mkdocs.config.defaults import get_schema
except ImportError:

    def get_schema():  # noqa: WPS440
        """Fallback for old versions of MkDocs."""
        return config.DEFAULT_SCHEMA


@pytest.fixture(name="mkdocs_conf")
def fixture_mkdocs_conf(request, tmp_path):
    """Yield a MkDocs configuration object."""
    conf = config.Config(schema=get_schema())
    while hasattr(request, "_parent_request") and hasattr(request._parent_request, "_parent_request"):  # noqa: WPS437
        request = request._parent_request  # noqa: WPS437

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
    yield conf
    conf["plugins"]["mkdocstrings"].on_post_build(conf)


@pytest.fixture(name="plugin")
def fixture_plugin(mkdocs_conf):
    """Return a plugin instance."""
    plugin = mkdocs_conf["plugins"]["mkdocstrings"]
    plugin.md = Markdown(extensions=mkdocs_conf["markdown_extensions"], extension_configs=mkdocs_conf["mdx_configs"])
    return plugin


@pytest.fixture(name="ext_markdown")
def fixture_ext_markdown(plugin):
    """Return a Markdown instance with MkdocstringsExtension."""
    return plugin.md
