#!/usr/bin/env python

from pathlib import Path

import mkdocs_gen_files

for path in Path("src", "mkdocstrings").glob("**/*.py"):
    doc_path = Path("reference", path.relative_to("src", "mkdocstrings")).with_suffix(".md")

    with mkdocs_gen_files.open(doc_path, "w") as f:
        ident = ".".join(path.relative_to("src").with_suffix("").parts)
        print("::: " + ident, file=f)

    mkdocs_gen_files.set_edit_path(doc_path, Path("..", path))
