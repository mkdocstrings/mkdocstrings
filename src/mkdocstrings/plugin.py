import ast
import importlib
import inspect
import os
import re
from functools import lru_cache

from mkdocs.config.config_options import Type
from mkdocs.plugins import BasePlugin

# TODO: option to display complete path instead of name for root_object
# TODO: option to change initial heading level per autodoc instruction
# TODO: option to group by category or not (if not grouped: alphabetical order)
# TODO: option to add category headers (if grouped)
# TODO: add a way to reference other objects in docstrings
# TODO: add source code pages (with links back to the documentation)

# TODO: use type annotations
# TODO: get classes and functions signatures (steal code from mkautodoc)
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


RECURSIVE_NODES = (ast.If, ast.IfExp, ast.Try, ast.With, ast.ExceptHandler)
"""The AST nodes that are recursively walked while searching for documented attributes in Python source."""

# exactly two leading underscores, exactly two trailing underscores
# since we enforce one non-underscore after the two leading underscores,
# we put the rest in an optional group
RE_SPECIAL = re.compile(r"^__[^_]([\w_]*[^_])?__$")
"""Regular expression to match special names like `__name__`."""

# at least two leading underscores, at most one trailing underscore
# since we enforce one non-underscore before the last,
# we make the previous characters optional with an asterisk
RE_CLASS_PRIVATE = re.compile(r"^__[\w_]*[^_]_?$")
"""Regular expression to match class-private names like `__name`."""

# at most one leading underscore, then whatever
RE_PRIVATE = re.compile(r"^_[^_][\w_]*$")
"""Regular expression to match private names like `_name`."""


def is_special_name(name: str) -> bool:
    """Check if name is a special name."""
    return bool(RE_SPECIAL.match(name))


def is_class_private_name(name: str) -> bool:
    """Check if name is a class-private name."""
    return bool(RE_CLASS_PRIVATE.match(name))


def is_private_name(name: str) -> bool:
    """Check if name is a private name."""
    return bool(RE_PRIVATE.match(name))


CATEGORY_ATTRIBUTE = "attribute"
CATEGORY_METHOD = "method"
CATEGORY_FUNCTION = "function"
CATEGORY_MODULE = "module"
CATEGORY_CLASS = "class"

NAME_SPECIAL = ("special", is_special_name)
NAME_CLASS_PRIVATE = ("class-private", is_class_private_name)
NAME_PRIVATE = ("private", is_private_name)

NAME_PROPERTIES = {
    CATEGORY_ATTRIBUTE: [NAME_SPECIAL, NAME_CLASS_PRIVATE, NAME_PRIVATE],
    CATEGORY_METHOD: [NAME_SPECIAL, NAME_PRIVATE],
    CATEGORY_FUNCTION: [NAME_PRIVATE],
    CATEGORY_CLASS: [NAME_PRIVATE],
    CATEGORY_MODULE: [NAME_SPECIAL, NAME_PRIVATE],
}


class Object:
    """
    Class to store information about a Python object.

    - the object category (ex: module, function, class, method or attribute)
    - the object path (ex: `package.submodule.class.inner_class.method`
    - the object name (ex: `__init__`)
    - the object docstring
    - the object properties, depending on its category (ex: special, classmethod, etc.)
    - the object signature (soon)

    Each instance additionally stores references to its children, grouped by category (see Attributes).
    """

    def __init__(self, category, name, path, docstring, properties, signature=None):
        self.category = category
        self.name = name
        self.signature = signature or ""
        self.path = path
        self.docstring = docstring or ""
        self.properties = properties
        self.parent = None

        self._path_map = {}

        self.attributes = []
        """List of all the object's attributes."""
        self.methods = []
        """List of all the object's methods."""
        self.functions = []
        """List of all the object's functions."""
        self.modules = []
        """List of all the object's submodules."""
        self.classes = []
        """List of all the object's classes."""
        self.children = []
        """List of all the object's children."""

    def __str__(self):
        return self.path

    @property
    def parent_path(self):
        """The parent's path, computed from the current path."""
        return self.path.rsplit(".", 1)[0]

    def add_child(self, obj):
        """Add an object as a child of this object."""
        if obj.parent_path != self.path:
            return

        self.children.append(obj)
        {
            CATEGORY_ATTRIBUTE: self.attributes,
            CATEGORY_METHOD: self.methods,
            CATEGORY_FUNCTION: self.functions,
            CATEGORY_MODULE: self.modules,
            CATEGORY_CLASS: self.classes,
        }.get(obj.category).append(obj)
        obj.parent = self

        self._path_map[obj.path] = obj

    def add_children(self, children):
        """Add a list of objects as children of this object."""
        for child in children:
            self.add_child(child)

    def dispatch_attributes(self, attributes):
        for attribute in attributes:
            try:
                attach_to = self._path_map[attribute.parent_path]
            except KeyError:
                pass
            else:
                attach_to.attributes.append(attribute)

    def render(self, heading=1, hide_no_doc=True):
        """
        Render this object as Markdown.

        This is dirty and will be refactored as a Markdown extension soon.
        """
        lines = []

        if self.docstring or not hide_no_doc:
            lines.append(f"{'#' * heading} `{self.name}`\n")

            properties = ", ".join(self.properties)
            if properties:
                lines.append(f"*({properties})*  ")

            lines.append(self.docstring)
            lines.append("")

        if self.attributes:
            lines.append(f"{'#' * (heading + 1)} Attributes")
            lines.append("")
            for attribute in sorted(self.attributes, key=lambda o: o.name.lower()):
                lines.append(attribute.render(heading + 2))
                lines.append("")
        if self.classes:
            lines.append(f"{'#' * (heading + 1)} Classes")
            lines.append("")
            for class_ in sorted(self.classes, key=lambda o: o.name.lower()):
                lines.append(class_.render(heading + 2))
                lines.append("")
        if self.methods:
            lines.append(f"{'#' * (heading + 1)} Methods")
            lines.append("")
            for method in sorted(self.methods, key=lambda o: o.name.lower()):
                lines.append(method.render(heading + 2))
                lines.append("")
        if self.functions:
            lines.append(f"{'#' * (heading + 1)} Functions")
            lines.append("")
            for function in sorted(self.functions, key=lambda o: o.name.lower()):
                lines.append(function.render(heading + 2))
                lines.append("")
        return "\n".join(lines)


class MkdocstringsPlugin(BasePlugin):
    """The mkdocstrings plugin to use in your mkdocs configuration file."""

    config_scheme = (
        ("global_filters", Type(list, default=["!^_[^_]", "!^__weakref__$"])),
        ("docstring_above_attribute", Type(bool, default=False)),
    )

    _testing_filters = 0
    """This should NOT appear."""

    def __init__(self, *args, **kwargs):
        super(MkdocstringsPlugin, self).__init__()
        self.type_node1 = None
        self.type_node2 = None
        self.get_attribute_names_and_docstring = None
        self._attributes_cache = {}
        self.hide_no_doc = True
        self.global_filters = []

    @staticmethod
    def node_is_docstring(node):
        return isinstance(node, ast.Expr) and isinstance(node.value, ast.Str)

    @staticmethod
    def node_to_docstring(node):
        return node.value.s

    @staticmethod
    def node_is_assignment(node):
        return isinstance(node, ast.Assign)

    @staticmethod
    def node_to_names(node):
        names = []
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                names.append(target.attr)
            elif isinstance(target, ast.Name):
                names.append(target.id)
        return names

    def on_config(self, config, **kwargs):
        self.global_filters = [(f, re.compile(f.lstrip("!"))) for f in self.config["global_filters"]]
        if self.config["docstring_above_attribute"]:

            def getter(node1, node2):
                if self.node_is_docstring(node1) and self.node_is_assignment(node2):
                    return self.node_to_names(node2), self.node_to_docstring(node1)
                raise ValueError

        else:

            def getter(node1, node2):
                if self.node_is_docstring(node2) and self.node_is_assignment(node1):
                    return self.node_to_names(node1), self.node_to_docstring(node2)
                raise ValueError

        self.get_attribute_names_and_docstring = getter
        return config

    @staticmethod
    def import_object(path):
        """
        Transform a path into an actual Python object.

        The path can be arbitrary long. You can pass the path to a package,
        a module, a class, a function or a global variable, as deep as you
        want, as long as the deepest module is importable through
        ``importlib.import_module`` and each object is obtainable through
        the ``getattr`` method. Local objects will not work.

        Args:
            path (str): the dot-separated path of the object.

        Returns:
            tuple: the imported module and obtained object.
        """
        if path is None or not path:
            return None

        obj_parent_modules = path.split(".")
        objects = []

        while True:
            try:
                parent_module_path = ".".join(obj_parent_modules)
                parent_module = importlib.import_module(parent_module_path)
                break
            except ImportError:
                if len(obj_parent_modules) == 1:
                    raise ImportError("No module named '%s'" % obj_parent_modules[0])
                objects.insert(0, obj_parent_modules.pop(-1))

        current_object = parent_module
        for obj in objects:
            current_object = getattr(current_object, obj)
        module = inspect.getmodule(current_object)
        return module, current_object

    @lru_cache(maxsize=None)
    def filter_name_out(self, name):
        keep = True
        for f, regex in self.global_filters:
            is_matching = bool(regex.match(name))
            if is_matching:
                if str(f).startswith("!"):
                    is_matching = not is_matching
                keep = is_matching
        return not keep

    def on_page_markdown(self, markdown, page, **kwargs):
        lines = markdown.split("\n")
        modified_lines = lines[::]
        for i, line in enumerate(lines):
            if line.startswith("::: "):
                import_string = line.replace("::: ", "")
                root_object = self.get_object_documentation(import_string)
                new_lines = root_object.render(heading=2)
                modified_lines[i] = new_lines
        return "\n".join(modified_lines)

    def get_object_documentation(self, import_string):
        module, obj = self.import_object(import_string)
        path = module.__name__
        if inspect.ismodule(obj):
            root_object = self.get_module_documentation(obj, path)
        elif inspect.isclass(obj):
            path = f"{path}.{obj.__name__}"
            root_object = self.get_class_documentation(obj, path)
        elif inspect.isfunction(obj):
            path = f"{path}.{obj.__name__}"
            root_object = self.get_function_documentation(obj, path)
        else:
            raise ValueError(f"{obj}:{type(obj)} not yet supported")
        attributes = self.get_attributes(module)
        root_object.dispatch_attributes([a for a in attributes if not self.filter_name_out(a.name)])
        return root_object

    def get_module_documentation(self, module, path):
        module_name = path.split(".")[-1]
        module_file_basename = os.path.splitext(os.path.basename(module.__file__))[0]
        properties = self.get_name_properties(module_file_basename, CATEGORY_MODULE)
        root_object = Object(
            category=CATEGORY_MODULE,
            name=module_name,
            path=path,
            docstring=inspect.getdoc(module),
            properties=properties,
        )
        for member_name, member in inspect.getmembers(module):
            if self.filter_name_out(member_name):
                continue
            member_path = f"{path}.{member_name}"
            if inspect.isclass(member) and inspect.getmodule(member) == module:
                root_object.add_child(self.get_class_documentation(member, member_path))
            elif inspect.isfunction(member) and inspect.getmodule(member) == module:
                root_object.add_child(self.get_function_documentation(member, member_path))
        return root_object

    def get_class_documentation(self, class_, path):
        class_name = class_.__name__
        root_object = Object(
            category=CATEGORY_CLASS,
            name=class_name,
            path=path,
            docstring=inspect.getdoc(class_),
            properties=self.get_name_properties(class_name, CATEGORY_CLASS),
        )
        for member_name, member in sorted(class_.__dict__.items()):
            if self.filter_name_out(member_name):
                continue
            member_path = f"{path}.{member_name}"
            if inspect.isclass(member):
                root_object.add_child(self.get_class_documentation(member, member_path))
                continue

            docstring = inspect.getdoc(getattr(class_, member_name))
            if isinstance(member, classmethod):
                root_object.add_child(
                    Object(
                        category=CATEGORY_METHOD,
                        name=member_name,
                        path=member_path,
                        docstring=docstring,
                        properties=self.get_name_properties(member_name, CATEGORY_METHOD) + ["classmethod"],
                    )
                )
            elif isinstance(member, staticmethod):
                root_object.add_child(
                    Object(
                        category=CATEGORY_METHOD,
                        name=member_name,
                        path=member_path,
                        docstring=docstring,
                        properties=self.get_name_properties(member_name, CATEGORY_METHOD) + ["staticmethod"],
                    )
                )
            elif isinstance(member, type(lambda: 0)):  # regular method
                root_object.add_child(
                    Object(
                        category=CATEGORY_METHOD,
                        name=member_name,
                        path=member_path,
                        docstring=docstring,
                        properties=self.get_name_properties(member_name, CATEGORY_METHOD),
                    )
                )
            elif isinstance(member, property):
                properties = ["property"]
                if member.fset is None:
                    properties.append("readonly")
                root_object.add_child(
                    Object(
                        category=CATEGORY_ATTRIBUTE,
                        name=member_name,
                        path=member_path,
                        docstring=docstring,
                        properties=properties + self.get_name_properties(member_name, CATEGORY_ATTRIBUTE),
                    )
                )
        return root_object

    def get_function_documentation(self, function, path):
        function_name = function.__name__
        return Object(
            category=CATEGORY_FUNCTION,
            name=function_name,
            path=path,
            docstring=inspect.getdoc(function),
            properties=self.get_name_properties(function_name, CATEGORY_FUNCTION),
        )

    @lru_cache(maxsize=None)
    def get_attributes(self, module):
        with open(module.__file__) as stream:
            code = stream.read()
        initial_ast_body = ast.parse(code).body

        # don't use module docstring (only useful if we allow docstrings above assignments)
        if self.node_is_docstring(initial_ast_body[0]):
            initial_ast_body = initial_ast_body[1:]

        return self._get_attributes(initial_ast_body, name_prefix=module.__name__)

    def _get_attributes(self, ast_body, name_prefix, properties=None):
        if not properties:
            properties = []
        documented_attributes = []
        previous_node = None
        for node in ast_body:
            try:
                names, docstring = self.get_attribute_names_and_docstring(previous_node, node)
            except ValueError:
                if isinstance(node, RECURSIVE_NODES):
                    documented_attributes.extend(self._get_attributes(node.body, name_prefix, properties))
                    if isinstance(node, ast.Try):
                        documented_attributes.extend(self._get_attributes(node.finalbody, name_prefix, properties))
                elif isinstance(node, ast.FunctionDef) and node.name == "__init__":
                    documented_attributes.extend(self._get_attributes(node.body, name_prefix))
                elif isinstance(node, ast.ClassDef):
                    documented_attributes.extend(
                        self._get_attributes(node.body, f"{name_prefix}.{node.name}", properties=["class"])
                    )
            else:
                for name in names:
                    documented_attributes.append(
                        Object(
                            category=CATEGORY_ATTRIBUTE,
                            path=f"{name_prefix}.{name}",
                            name=name,
                            docstring=docstring,
                            properties=properties + self.get_name_properties(name, CATEGORY_ATTRIBUTE),
                        )
                    )
            previous_node = node
        return documented_attributes

    def get_name_properties(self, name, category):
        properties = []
        for prop in NAME_PROPERTIES[category]:
            if prop[1](name):
                properties.append(prop[0])
        return properties
