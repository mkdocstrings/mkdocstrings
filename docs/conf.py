import os
from pathlib import Path

import toml
from recommonmark.transform import AutoStructify

metadata = toml.load(Path(__file__).parent.parent / "pyproject.toml")["tool"]["poetry"]
project = metadata["name"]
repository = metadata["repository"].rstrip("/")
year = "2019"
author = metadata["authors"][0]
copyright = "{0}, {1}".format(year, author)
version = release = metadata["version"]
master_doc = "index"

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx.ext.viewcode", "recommonmark"]

# Auto-documentation directives in RST files
autodoc_default_options = {"members": None, "special-members": "__init__", "exclude-members": "__weakref__"}

# ReadTheDocs theme for local builds
on_rtd = os.environ.get("READTHEDOCS", None) == "True"
if not on_rtd:
    html_theme = "sphinx_rtd_theme"

# Some rendering options
html_last_updated_fmt = "%b %d, %Y"
html_context = {"extra_css_files": ["_static/extra.css"]}
html_static_path = ["extra.css"]

# Google Style docstrings
napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False


# Documentation in Markdown
def setup(app):
    app.add_config_value(
        "recommonmark_config",
        {
            # "url_resolver": lambda url: repository + "/tree/master/docs/" + url,
            "auto_toc_tree_section": "Welcome to {}'s documentation!".format(metadata["name"])
        },
        True,
    )
    app.add_transform(AutoStructify)
