"""Plugin module docstring."""

from mkdocs.config.config_options import Type as MkType
from mkdocs.plugins import BasePlugin

from .documenter import Documenter
from .renderer import MarkdownRenderer, render_references

config = {
    "show_top_object_heading": False,
    "show_top_object_full_path": True,
    "group_by_categories": True,
    "show_groups_headings": False,
    "hide_no_doc": True,
    "add_source_details": True,
}


class MkdocstringsPlugin(BasePlugin):
    """The mkdocstrings plugin to use in your mkdocs configuration file."""

    config_scheme = (("global_filters", MkType(list, default=["!^_[^_]", "!^__weakref__$"])),)

    def __init__(self, *args, **kwargs) -> None:
        super(MkdocstringsPlugin, self).__init__()
        self.hide_no_doc = True
        self.documenter = None
        self.objects = {}
        self.pages_with_docstrings = []
        self.references = []

    def on_config(self, config, **kwargs):
        """Initializes a [Documenter][mkdocstrings.documenter.Documenter]."""
        self.documenter = Documenter(self.config["global_filters"])
        return config

    def on_nav(self, nav, **kwargs):
        for page in nav.pages:
            with open(page.file.abs_src_path, "r") as file:
                markdown = file.read()
            lines = markdown.split("\n")
            in_code_block = False
            for i, line in enumerate(lines):
                if line.startswith("```"):
                    in_code_block = not in_code_block
                elif line.startswith("::: ") and not in_code_block:
                    import_string = line.replace("::: ", "")
                    if import_string not in self.objects:
                        root_object = self.documenter.get_object_documentation(import_string)
                        self.references.append(render_references(root_object, page.abs_url))
                        mapping_value = {"object": root_object, "page": page.abs_url}
                        self.objects[import_string] = mapping_value
                        if import_string != root_object.path:
                            self.objects[root_object.path] = mapping_value
                        if page.abs_url not in self.pages_with_docstrings:
                            self.pages_with_docstrings.append(page.abs_url)
        return nav

    def on_page_markdown(self, markdown, page, **kwargs):
        if page.abs_url not in self.pages_with_docstrings:
            return markdown
        lines = markdown.split("\n")
        modified_lines = lines[::]
        for i, line in enumerate(lines):
            if line.startswith("::: "):
                renderer = MarkdownRenderer(dict(config))
                import_string = line.replace("::: ", "")
                root_object = self.objects[import_string]["object"]
                heading = 2 if config["show_top_object_heading"] else 1
                modified_lines[i] = "\n".join(renderer.render(root_object, heading))
        modified_lines.extend(self.references)
        return "\n".join(modified_lines)

    def on_page_content(self, html, page, **kwargs):
        if page.abs_url not in self.pages_with_docstrings:
            return html
        div = '<div class="autodoc">'
        end_div = "</div>"
        lines = html.split("\n")
        new_lines = lines[::]
        levels = [0]
        inserted = 0
        for i, line in enumerate(lines):
            if line.startswith("<h") and line[2].isnumeric():
                level = int(line[2])
                if level > levels[-1]:
                    new_lines.insert(i + 1 + inserted, div)
                    inserted += 1
                    levels.append(level)
                elif level == levels[-1]:
                    new_lines.insert(i + inserted, end_div)
                    inserted += 1
                    new_lines.insert(i + 1 + inserted, div)
                    inserted += 1
                else:
                    while level < levels[-1]:
                        new_lines.insert(i + inserted, end_div)
                        inserted += 1
                        levels.pop()
                    new_lines.insert(i + inserted, end_div)
                    inserted += 1
                    new_lines.insert(i + 1 + inserted, div)
                    inserted += 1
        while levels[-1] > 0:
            new_lines.append(end_div)
            levels.pop()
        new_html = "\n".join(new_lines)
        return new_html
