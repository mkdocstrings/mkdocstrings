"""Plugin module docstring."""

from mkdocs.config.config_options import Type as MkType
from mkdocs.plugins import BasePlugin

from .documenter import Documenter

# TODO: option to change initial heading level per autodoc instruction
# TODO: add a way to reference other objects in docstrings
#       build all references in an mkdocs event
#       append/fix all those references in a post action

# TODO: use type annotations
# TODO: get attributes types and signatures parameters types from type annotations or docstring

# TODO: steal code from mkautodoc to create a markdown extension (better to render HTML)

# TODO: parse google-style blocks
#       change to admonitions for simple blocks
#       parse Args, Raises and Returns to get types and messages

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


class MkdocstringsPlugin(BasePlugin):
    """The mkdocstrings plugin to use in your mkdocs configuration file."""

    config_scheme = (("global_filters", MkType(list, default=["!^_[^_]", "!^__weakref__$"])),)

    def __init__(self, *args, **kwargs) -> None:
        super(MkdocstringsPlugin, self).__init__()
        self.hide_no_doc = True
        self.documenter = None

    def on_config(self, config, **kwargs):
        self.documenter = Documenter(self.config["global_filters"])
        return config

    def on_page_markdown(self, markdown: str, page, **kwargs) -> str:
        lines = markdown.split("\n")
        modified_lines = lines[::]
        in_code_block = False
        for i, line in enumerate(lines):
            if line.startswith("```"):
                in_code_block = not in_code_block
            if line.startswith("::: ") and not in_code_block:
                import_string = line.replace("::: ", "")
                root_object = self.documenter.get_object_documentation(import_string)
                config = {
                    "show_top_object_heading": False,
                    "show_top_object_full_path": True,
                    "group_by_categories": True,
                    "show_groups_headings": False,
                    "hide_no_doc": True,
                    "add_source_details": True,
                }
                heading = 2 if config["show_top_object_heading"] else 1
                new_lines = root_object.render(heading, **config)
                modified_lines[i] = new_lines
        return "\n".join(modified_lines)
