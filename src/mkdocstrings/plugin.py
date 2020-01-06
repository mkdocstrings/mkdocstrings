"""Plugin module docstring."""
import sys

from markdown import Markdown
from mkdocs.config.config_options import Type as MkType
from mkdocs.plugins import BasePlugin
from mkdocs.structure.toc import get_toc
from mkdocs.utils import log

from .documenter import Documenter
from .renderer import MarkdownRenderer, insert_divs, render_references

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

    config_scheme = (
        ("global_filters", MkType(list, default=["!^_[^_]", "!^__weakref__$"])),
        ("watch", MkType(list, default=[])),
    )

    def __init__(self, *args, **kwargs) -> None:
        super(MkdocstringsPlugin, self).__init__()
        self.hide_no_doc = True
        self.documenter = None
        self.objects = {}
        self.pages_with_docstrings = []
        self._references = []
        self._main_config = None
        self._sys = set(sys.modules.keys())

    @property
    def references(self):
        return "\n\n" + "\n".join(self._references)

    def get_combined_extensions(self):
        extensions = self._main_config["markdown_extensions"]
        configs = self._main_config["mdx_configs"] or {}
        for ext, ext_config in {
            "admonition": {},
            "codehilite": {"guess_lang": False},
            "attr_list": {},
            "pymdownx.details": {},
            "pymdownx.superfences": {},
            "pymdownx.inlinehilite": {},
            "toc": {"permalink": True},
        }.items():
            if ext not in extensions:
                extensions.append(ext)
                configs[ext] = ext_config
            else:
                if ext not in configs:
                    configs[ext] = {}
                configs[ext].update(ext_config)
        return extensions, configs

    def clear(self):
        self.documenter = None
        self.objects = {}
        self.pages_with_docstrings = []
        self._references = []
        self._main_config = None
        self._sys = set(sys.modules.keys())

    def on_serve(self, server, config, **kwargs):
        builder = list(server.watcher._tasks.values())[0]["func"]

        def unload_and_rebuild():
            diff = set(sys.modules.keys()) - self._sys
            log.info(
                f"mkdocstrings: Unloading modules loaded after mkdocstrings plugin was instantiated ({len(diff)} modules)"
            )
            for module in diff:
                del sys.modules[module]
            self.clear()
            builder()

        for element in self.config["watch"]:
            log.info(f"mkdocstrings: Adding directory '{element}' to watcher")
            server.watch(element, unload_and_rebuild)
        return server

    def on_config(self, config, **kwargs):
        """Initializes a [Documenter][mkdocstrings.documenter.Documenter]."""
        self.documenter = Documenter(self.config["global_filters"])
        self._main_config = config
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
                        self._references.append(render_references(root_object, page.abs_url))
                        mapping_value = {"object": root_object, "page": page.abs_url}
                        self.objects[import_string] = mapping_value
                        if import_string != root_object.path:
                            self.objects[root_object.path] = mapping_value
                        if page.abs_url not in self.pages_with_docstrings:
                            self.pages_with_docstrings.append(page.abs_url)
        return nav

    def on_page_markdown(self, markdown, page, **kwargs):
        return f"{markdown}{self.references}"

    def on_page_content(self, html, page, **kwargs):
        if page.abs_url not in self.pages_with_docstrings:
            return html

        extensions, configs = self.get_combined_extensions()
        md = Markdown(extensions=extensions, extension_configs=configs)

        lines = page.markdown.split("\n")
        modified_lines = lines[::]
        for i, line in enumerate(lines):
            if line.startswith("::: "):
                renderer = MarkdownRenderer(dict(config))
                import_string = line.replace("::: ", "")
                root_object = self.objects[import_string]["object"]
                heading = 2 if config["show_top_object_heading"] else 1
                modified_lines[i] = "\n".join(renderer.render(root_object, heading))

        modified_lines.append(self.references)
        markdown_contents = "\n".join(modified_lines)
        html = insert_divs(md.convert(markdown_contents))
        page.toc = get_toc(getattr(md, "toc", ""))
        return html
