"""Configuration for the pytest test suite."""

from __future__ import annotations

from collections import ChainMap
from typing import TYPE_CHECKING, Any

import pytest
from markdown.core import Markdown
from mkdocs.config.defaults import MkDocsConfig

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from mkdocs import config

    from mkdocstrings._internal.plugin import MkdocstringsPlugin


@pytest.fixture(name="mkdocs_conf")
def fixture_mkdocs_conf(request: pytest.FixtureRequest, tmp_path: Path) -> Iterator[config.Config]:
    """Yield a MkDocs configuration object."""
    conf = MkDocsConfig()
    while hasattr(request, "_parent_request") and hasattr(request._parent_request, "_parent_request"):
        request = request._parent_request

    conf_dict = {
        "site_name": "foo",
        "site_url": "https://example.org/",
        "site_dir": str(tmp_path),
        "plugins": [{"mkdocstrings": {"default_handler": "python"}}],
        **getattr(request, "param", {}),
    }
    # Re-create it manually as a workaround for https://github.com/mkdocs/mkdocs/issues/2289
    mdx_configs: dict[str, Any] = dict(ChainMap(*conf_dict.get("markdown_extensions", [])))

    conf.load_dict(conf_dict)
    assert conf.validate() == ([], [])

    conf["mdx_configs"] = mdx_configs
    conf["markdown_extensions"].insert(0, "toc")  # Guaranteed to be added by MkDocs.

    conf = conf["plugins"]["mkdocstrings"].on_config(conf)
    conf = conf["plugins"]["autorefs"].on_config(conf)
    yield conf
    conf["plugins"]["mkdocstrings"].on_post_build(conf)


@pytest.fixture(name="plugin")
def fixture_plugin(mkdocs_conf: config.Config) -> MkdocstringsPlugin:
    """Return a plugin instance."""
    return mkdocs_conf["plugins"]["mkdocstrings"]


@pytest.fixture(name="ext_markdown")
def fixture_ext_markdown(mkdocs_conf: MkDocsConfig) -> Markdown:
    """Return a Markdown instance with MkdocstringsExtension."""
    return Markdown(extensions=mkdocs_conf["markdown_extensions"], extension_configs=mkdocs_conf["mdx_configs"])
