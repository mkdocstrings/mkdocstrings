#!/usr/bin/env python

from pathlib import Path

import mkdocs_gen_files


def build_nav(data, indentation=""):
    for key, value in data.items():
        if isinstance(value, dict):
            yield f"{indentation}* {key}\n"
            yield from build_nav(value, indentation + "    ")
        else:
            yield f"{indentation}* [{key}.py]({value})\n"


nav_data = {
    "mkdocstrings": {},
    "mkdocs_autorefs": {
        "references": "autorefs/references.md",
        "plugin": "autorefs/plugin.md",
    },
}

for path in sorted(Path("src").glob("**/*.py")):
    module_path = path.relative_to("src").with_suffix("")
    doc_path = path.relative_to("src", "mkdocstrings").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    current_dict = nav_data
    for part in module_path.parent.parts:
        current_dict = current_dict.setdefault(part, {})
    current_dict[module_path.name] = doc_path

    with mkdocs_gen_files.open(full_doc_path, "w") as f:
        ident = ".".join(module_path.parts)
        print("::: " + ident, file=f)

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(build_nav(nav_data))
