"""Plugin module docstring."""

from markdown import Markdown
from mkdocs.config.config_options import Type as MkType
from mkdocs.plugins import BasePlugin
from bs4 import BeautifulSoup

from .documenter import Documenter

# TODO: show source file in source code blocks titles

# TODO: option to change initial heading level per autodoc instruction

# TODO: use type annotations

# TODO: support more properties:
#       generators, coroutines, awaitable (see inspect.is...), decorators?
#       metaclass, dataclass
#       optional (parameters with default values)

# TODO: pick attributes without docstrings?

# TODO: write tests

# TODO: make sure to recurse correctly (module's modules, class' classes, etc.)
# TODO: discover package's submodules

# TODO: option to void special methods' docstrings
#       when they are equal to the built-in ones (ex: "Return str(self)." for __str__)

# TODO: option not to write root group header if it's the only group
# TODO: option to move __init__ docstring to class docstring

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
            with open(page.file.abs_src_path, 'r') as file:
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
                        self.references.append(root_object.render_references(page.abs_url))
                        mapping_value = {
                            "object": root_object,
                            "page": page.abs_url
                        }
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
            # if line.startswith("<p>::: ") or line.startswith("::: "):
            if line.startswith("::: "):
                import_string = line.replace("::: ", "")
                # import_string = line.replace("::: ", "").replace("<p>", "").replace("</p>", "")
                root_object = self.objects[import_string]["object"]
                heading = 2 if config["show_top_object_heading"] else 1
                new_lines = root_object.render(heading, **config)
                modified_lines[i] = new_lines
        modified_lines.extend(self.references)
        return "\n".join(modified_lines)

    def on_page_content(self, html, page, **kwargs):
        if page.abs_url not in self.pages_with_docstrings:
            return html
        lines = html.split("\n")
        new_lines = lines[::]
        levels = [0]
        inserted = 0
        for i, line in enumerate(lines):
            if line.startswith("<h"):
                level = int(line[2])
                if level > levels[-1]:
                    new_lines.insert(i + 1 + inserted, '<div class="autodoc">')
                    inserted += 1
                    levels.append(level)
                elif level == levels[-1]:
                    new_lines.insert(i + inserted, "</div>")
                    inserted += 1
                    new_lines.insert(i + 1 + inserted, '<div class="autodoc">')
                    inserted += 1
                else:
                    while level < levels[-1]:
                        new_lines.insert(i + inserted, "</div>")
                        inserted += 1
                        levels.pop()
                    new_lines.insert(i + inserted, "</div>")
                    inserted += 1
                    new_lines.insert(i + 1 + inserted, '<div class="autodoc">')
                    inserted += 1
        while levels[-1] > 0:
            new_lines.append("</div>")
            levels.pop()
        new_html = "\n".join(new_lines)
        return new_html

