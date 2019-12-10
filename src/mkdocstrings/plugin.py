import importlib
import inspect
import re
import ast

from mkdocs.plugins import BasePlugin
from mkdocs.config.config_options import Type

RECURSIVE_NODES = (ast.If, ast.IfExp, ast.Try, ast.With, ast.ExceptHandler)
"""I'm the RECURSIVE_NODES doctring."""

NAMED_RECURSIVE_NODES = (ast.ClassDef, ast.FunctionDef)


class MkdocstringsPlugin(BasePlugin):

    config_scheme = (
        ("global_classes_filters",  Type(tuple, default=("!^_[^_]", "!^__weakref__$"))),
        ("global_modules_filters",  Type(tuple, default=())),
        ("docstring_above_attribute", Type(bool, default=False))
    )
    """I'm the config_scheme docstring."""

    def __init__(self, *args, **kwargs):
        super(MkdocstringsPlugin, self).__init__()
        self.type_node1 = None
        self.type_node2 = None
        """I'm the type_node2 docstring."""
        self.get_attribute_names_and_docstring = None
        self._attributes_cache = {}

    def node_is_docstring(self, node):
        return isinstance(node, ast.Expr) and isinstance(node.value, ast.Str)

    def node_to_docstring(self, node):
        return node.value.s

    def node_is_assignment(self, node):
        return isinstance(node, ast.Assign)

    def node_to_names(self, node):
        targets = node.targets
        names = []
        for target in targets:
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
        return module, current_object

    def on_page_markdown(self, markdown, page, **kwargs):
        lines = markdown.split("\n")
        for line in lines:
            if line.startswith("::: "):
                import_string = line.replace("::: ", "")
                module, obj = self.import_object(import_string)
                module_path = module.__file__
                if module_path not in self._attributes_cache:
                    self._attributes_cache[module_path] = self.get_attributes(module)
                    print(self._attributes_cache[module_path])
                all_attributes = self._attributes_cache[module_path]

                if inspect.ismodule(obj):
                    attributes = []
                    functions = []
                    classes = []

                elif inspect.isclass(obj):
                    attributes = []
                    methods = []
                    classes = []
                    for key, value in sorted(obj.__dict__.items()):
                        types = []
                        docstring = inspect.getdoc(getattr(obj, key))
                        if re.match(r"^__\w+__$", key):
                            types.append("special")
                        if isinstance(value, classmethod):
                            types.append("class")
                            methods.append((key, docstring, types))
                        elif isinstance(value, staticmethod):
                            types.append("static")
                            methods.append((key, docstring, types))
                        elif isinstance(value, type(lambda: 0)):
                            methods.append((key, docstring, types))
                        elif isinstance(value, property):
                            types.append("property")
                            if value.fset is None:
                                types.append("readonly")
                            attributes.append((key, docstring, types))
                        elif isinstance(value, type):
                            classes.append((key, docstring, types))

                    print("attributes")
                    for attribute in attributes:
                        print(f"  {attribute[0]} ({', '.join(attribute[2])})\n    {attribute[1]}")
                    print()
                    print("methods")
                    for method in methods:
                        print(f"  {method[0]} ({', '.join(method[2])})\n    {method[1]}")
                    print()
                    print("classes")
                    for class_ in classes:
                        print(f"  {class_[0]} ({', '.join(class_[2])})\n    {class_[1]}")
                    print()

                elif callable(obj):
                    pass
        print(flush=True)
        return markdown

    def get_attributes(self, module):
        module_path = module.__file__

        def _get_attributes(ast_body, name_prefix, properties=None):
            if not properties:
                properties = []
            documented_attributes = []
            previous_node = None
            for node in ast_body:
                try:
                    names, docstring = self.get_attribute_names_and_docstring(previous_node, node)
                except ValueError:
                    if isinstance(node, RECURSIVE_NODES):
                        documented_attributes.extend(_get_attributes(node.body, name_prefix, properties))
                        if isinstance(node, ast.Try):
                            documented_attributes.extend(_get_attributes(node.finalbody, name_prefix, properties))
                    elif isinstance(node, ast.FunctionDef) and node.name == "__init__":
                        documented_attributes.extend(_get_attributes(node.body, name_prefix))
                    elif isinstance(node, ast.ClassDef):
                        documented_attributes.extend(_get_attributes(node.body, f"{name_prefix}.{node.name}", properties=["class"]))
                else:
                    for name in names:
                        # copy properties in name_props to avoid modifying original properties
                        name_props = properties[::]
                        # exactly two leading underscores, exactly two trailing underscores
                        # since we enforce one non-underscore after the two leading underscores,
                        # we put the rest in an optional group
                        if re.match(r"^__[^_]([\w_]*[^_])?__$", name):
                            name_props.append("special")
                        # at least two leading underscores, at most one trailing underscore
                        # since we enforce one non-underscore before the last,
                        # we make the previous characters optional with an asterisk
                        # FIXME: we access the name via __dict__, so it's already mangled as _MyClass__my_variable
                        elif re.match(r"^__[\w_]*[^_]_?$", name):
                            name_props.append("class-private")
                        # at most one leading underscore, then whatever
                        elif re.match(r"^_[^_][\w_]*$", name):
                            name_props.append("private")
                        documented_attributes.append({
                            "names": f"{name_prefix}.{name}",
                            "docstring": docstring,
                            "properties": name_props
                        })
                previous_node = node
            return documented_attributes

        with open(module_path) as stream:
            code = stream.read()
        ast_body = ast.parse(code).body

        # don't use module docstring
        if self.node_is_docstring(ast_body[0]):
            ast_body = ast_body[1:]

        return _get_attributes(ast_body, name_prefix=module.__name__)

    class InnerClass:
        pass

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
