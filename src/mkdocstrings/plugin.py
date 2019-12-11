import importlib
import inspect
import re
import ast
from pprint import pprint
import os
import json

from mkdocs.plugins import BasePlugin
from mkdocs.config.config_options import Type

# TODO: make sure to recurse correctly (module's modules, class' classes, etc.)
# TODO: filter elements based on configuration filters (see cli.should_keep)
# TODO: get classes and functions signatures
# TODO: get attributes types and signatures parameters types from type annotations or docstring
# TODO: parse google-style blocks
# TODO: support more properties: generators, coroutines, awaitable (see inspect.is...), decorators?
# FIXME: change append_name_property method and its usage, because it's ugly.
# TODO: create separate methods to check name properties (special, private, etc.)
#       as it makes no sense to declare a class or a module as "class-private", or a class as "special"
#       but maybe I'm wrong (check behavior with tests fixtures)
# TODO: pick attributes without docstrings?
# TODO: use a proper class for elements (type, name, path, doctring, properties)

RECURSIVE_NODES = (ast.If, ast.IfExp, ast.Try, ast.With, ast.ExceptHandler)
"""I'm the RECURSIVE_NODES docstring."""

NAMED_RECURSIVE_NODES = (ast.ClassDef, ast.FunctionDef)

# exactly two leading underscores, exactly two trailing underscores
# since we enforce one non-underscore after the two leading underscores,
# we put the rest in an optional group
RE_SPECIAL = re.compile(r"^__[^_]([\w_]*[^_])?__$")

# at least two leading underscores, at most one trailing underscore
# since we enforce one non-underscore before the last,
# we make the previous characters optional with an asterisk
RE_CLASS_PRIVATE = re.compile(r"^__[\w_]*[^_]_?$")

# at most one leading underscore, then whatever
RE_PRIVATE = re.compile(r"^_[^_][\w_]*$")


class Object:
    def __init__(self, object_type, name, path, docstring, properties, signature=None):
        self.object_type = object_type
        self.name = name
        self.signature = signature or ""
        self.path = path
        self.docstring = docstring or ""
        self.properties = properties
        self.parent = None

        self.attributes = []
        self.methods = []
        self.functions = []
        self.modules = []
        self.classes = []
        self.children = []

    def __str__(self):
        return self.path

    @property
    def parent_path(self):
        return self.path.rsplit(".", 1)[0]

    def add_child(self, obj):
        self.children.append(obj)
        {
            "attribute": self.attributes,
            "method": self.methods,
            "function": self.functions,
            "module": self.modules,
            "class": self.classes,
        }.get(obj.object_type).append(obj)
        obj.parent = self

    def add_children(self, children):
        for child in children:
            self.add_child(child)

    def render(self, heading=1, hide_nodoc=False):
        if hide_nodoc and not self.docstring:
            return
        print(f"{'#' * heading} {self.name}")
        print(self.docstring)
        print()
        if self.attributes:
            print(f"{'#' * (heading + 1)} Attributes")
            print()
            for attribute in self.attributes:
                attribute.render(heading + 2)
                print()
        if self.classes:
            print(f"{'#' * (heading + 1)} Classes")
            print()
            for class_ in self.classes:
                class_.render(heading + 2)
                print()
        if self.methods:
            print(f"{'#' * (heading + 1)} Methods")
            print()
            for method in self.methods:
                method.render(heading + 2)
                print()
        if self.functions:
            print(f"{'#' * (heading + 1)} Functions")
            print()
            for function in self.functions:
                function.render(heading + 2)
                print()


class MkdocstringsPlugin(BasePlugin):
    """Doc."""

    config_scheme = (
        ("global_classes_filters", Type(tuple, default=("!^_[^_]", "!^__weakref__$"))),
        ("global_modules_filters", Type(tuple, default=())),
        ("docstring_above_attribute", Type(bool, default=False)),
    )
    """A class attribute."""

    def __init__(self, *args, **kwargs):
        super(MkdocstringsPlugin, self).__init__()
        self.type_node1 = None
        self.type_node2 = None
        self.get_attribute_names_and_docstring = None
        self._attributes_cache = {}
        self.hide_nodoc = True
        self.group_by_type = True
        self.group_heading = {
            "attribute": "Attributes",
            "method": "Methods",
            "function": "Functions",
            "class": "Classes",
            "module": "Modules"
        }
        self.extra_heading = 1 if self.group_by_type else 0

        # TEST STUFF -----------------------------------------

        self.__class_private_var = 0
        """Class private var!"""

        self._MkdocstringsPlugin__false_class_private = 0
        """False class private var!"""

        self.some_varrrrr = 0
        """My varrrrr doc."""

        self.__special_var__ = 0
        """My special var."""

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

        module = parent_module
        current_object = parent_module
        for obj in objects:
            current_object = getattr(current_object, obj)
        module = inspect.getmodule(current_object)
        return module, current_object

    def on_page_markdown(self, markdown, page, **kwargs):
        lines = markdown.split("\n")
        for line in lines:
            if line.startswith("::: "):
                import_string = line.replace("::: ", "")
                root_object = self.get_object_documentation(import_string)
                root_object.render()
        print(flush=True)
        return markdown

    def get_or_set_cached_attribute_documentation(self, module):
        module_path = module.__file__
        if module_path not in self._attributes_cache:
            self._attributes_cache[module_path] = self.get_attributes(module)
        return self._attributes_cache[module_path]

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
        attributes = self.get_or_set_cached_attribute_documentation(module)
        attributes = list(filter(lambda x: x.path.startswith(path), attributes))
        root_object.add_children(attributes)
        return root_object

    def get_module_documentation(self, module, path):
        module_name = path.split(".")[-1]
        properties = []
        if os.path.splitext(os.path.basename(module.__file__))[0] == "__init__":
            properties.append("special")
        properties = self.append_name_property(module_name, properties)
        root_object = Object(object_type="module", name=module_name, path=path, docstring=inspect.getdoc(module), properties=properties)
        for member_name, member in inspect.getmembers(module):
            member_path = f"{path}.{member_name}"
            if inspect.isclass(member) and inspect.getmodule(member) == module:
                root_object.add_child(self.get_class_documentation(member, member_path))
            elif inspect.isfunction(member) and inspect.getmodule(member) == module:
                root_object.add_child(self.get_function_documentation(member, member_path))
        return root_object

    def get_class_documentation(self, class_, path):
        class_name = class_.__name__
        root_object = Object(object_type="class", name=class_name, path=path, docstring=inspect.getdoc(class_), properties=self.append_name_property(class_name))
        for member_name, member in sorted(class_.__dict__.items()):
            member_path = f"{path}.{member_name}"
            if inspect.isclass(member):
                root_object.add_child(self.get_class_documentation(member, member_path))
                continue

            docstring = inspect.getdoc(getattr(class_, member_name))
            properties = self.append_name_property(member_name)
            if isinstance(member, classmethod):
                root_object.add_child(
                    Object(object_type="method", name=member_name, path=member_path, docstring=docstring, properties=properties + ["classmethod"])
                )
            elif isinstance(member, staticmethod):
                root_object.add_child(
                    Object(object_type="method", name=member_name, path=member_path, docstring=docstring, properties=properties + ["staticmethod"])
                )
            elif isinstance(member, type(lambda: 0)):  # regular method
                root_object.add_child(Object(object_type="method", name=member_name, path=member_path, docstring=docstring, properties=properties))
            elif isinstance(member, property):
                properties.append("property")
                if member.fset is None:
                    properties.append("readonly")
                root_object.add_child(Object(object_type="attribute", name=member_name, path=member_path, docstring=docstring, properties=properties))
        return root_object

    def get_function_documentation(self, function, path):
        function_name = function.__name__
        return Object(
            object_type="function",
            name=function_name,
            path=path,
            docstring=inspect.getdoc(function),
            properties=self.append_name_property(function_name),
        )

    def get_attributes(self, module):
        with open(module.__file__) as stream:
            code = stream.read()
        initial_ast_body = ast.parse(code).body

        # don't use module docstring (only useful if allow docstrings above assignments
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
                            object_type="attribute",
                            path=f"{name_prefix}.{name}",
                            name=name,
                            docstring=docstring,
                            properties=self.append_name_property(name, properties),
                        )
                    )
            previous_node = node
        return documented_attributes

    @staticmethod
    def is_special_name(name):
        return bool(RE_SPECIAL.match(name))

    @staticmethod
    def is_class_private_name(name):
        return bool(RE_CLASS_PRIVATE.match(name))

    @staticmethod
    def is_private_name(name):
        return bool(RE_PRIVATE.match(name))

    def append_name_property(self, name, properties=None):
        if not properties:
            properties = []
        else:
            properties = properties[::]
        if self.is_special_name(name):
            properties.append("special")
        elif self.is_class_private_name(name):
            properties.append("class-private")
        elif self.is_private_name(name):
            properties.append("private")
        return properties

    # TEST STUFF ---------------------------------------------------------------

    class InnerClass:
        """I have some doc."""

        def hello(self):
            """I do nothing."""

    @classmethod
    def im_a_class_method(cls):
        pass

    @staticmethod
    def im_a_static_method():
        pass

    @property
    def im_a_property(self):
        return None

    @im_a_property.setter
    def im_a_property(self, value):
        pass

    @property
    def im_a_readonly_property(self):
        return None

    some_var = 0
    """I'm the some_var docstring."""

    __class_private_classvar = 0
    """Class class private var!"""

    _MkdocstringsPlugin__false_classclass_private = 0
    """False class class private var!"""
