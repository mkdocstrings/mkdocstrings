"""
This module is responsible for loading the documentation from Python objects and rendering it to Markdown.

Here is how to use it:

1. instantiate a [`Documenter`][mkdocstrings.documenter.Documenter] instance with user configuration
    (currently only global filters).
2. get an instance of a subclass of [`Object`][mkdocstrings.documenter.Object]
    ([`Module`][mkdocstrings.documenter.Module], [`Class`][mkdocstrings.documenter.Class],
    [`Method`][mkdocstrings.documenter.Method], [`Function`][mkdocstrings.documenter.Function],
    or [`Attribute`][mkdocstrings.documenter.Attribute]) with the documenter's `get_object_documentation` method.
    The method takes the dotted-path to an object as argument.

Here is how we proceed:

1. The documentation for an object is obtained recursively, by walking through its children objects (module classes,
    module functions, class methods, class attributes, class nested classes, etc.). Each one of the object is
    instantiated using its correct category (Module, Class, Method, or Function). The children of an object
    are organized into these same categories: [`modules`][mkdocstrings.documenter.Object.modules],
    [`classes`][mkdocstrings.documenter.Object.classes], [`methods`][mkdocstrings.documenter.Object.methods],
    and [`functions`][mkdocstrings.documenter.Object.functions].
2. The attributes documentation is obtained by parsing the code with the `ast` module. We simply search for
    "assignment" or "annotated assignment" nodes followed by "docstring" nodes (expressions or strings). Attribute
    children are stored in an object's [`attributes`][mkdocstrings.documenter.Object.attributes] attribute by
    dispatching them onto the object thanks to their dotted-paths.
3. Each docstring is parsed to build a list of "docstring sections". Such a section can be a markdown block of lines,
    a block of parameters, a block of exceptions, an admonition, or the information about the return value.
    Exceptions and the return value are instances of [`AnnotatedObject`][mkdocstrings.docstrings.AnnotatedObject],
    while parameters are instances of the [`Parameter`][mkdocstrings.docstrings.Parameter] class, which is a subclass of
    `AnnotatedObject`. To build these sections, we search for blocks matching the
    [Google style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) for docstrings.

    For example:

    ```
    Note:
        This is a note.
    ```

    ...will be parsed as a "note" admonition, while:

    ```
    Arguments:
        param1: Description of param1.
        param2: Description of param2.

    Raises:
        OSError: When this exception is raised.
        RuntimeError: When this exception is raised.

    Returns:
        Description of the return value.
    ```

    ...will be parsed as "parameters", "exceptions" and "return" sections.

    Important:
        Note the absence of type hints in the arguments and returns section: in `mkdocstrings`, the types are
        obtained using type annotations (using the `typing` module and builtin types), and not from type hints.
        It means that you must use type annotations in the signature of your function/method, or add a type
        annotation to an attribute.

        For example:

        ```python
        def my_function(param1: int, param2: Optional[str] = None) -> typing.Dict[int, str]:
            pass
        ```
"""

import ast
import importlib
import inspect
import os
import pkgutil
import re
import textwrap
from functools import lru_cache
from types import ModuleType
from typing import Any, Callable, List, Optional, Pattern, Tuple, Type, Union

from .docstrings import Docstring

RECURSIVE_NODES = (ast.If, ast.IfExp, ast.Try, ast.With, ast.ExceptHandler)

# exactly two leading underscores, exactly two trailing underscores
# since we enforce one non-underscore after the two leading underscores,
# we put the rest in an optional group
RE_SPECIAL: Pattern = re.compile(r"^__[^_]([\w_]*[^_])?__$")

# at least two leading underscores, at most one trailing underscore
# since we enforce one non-underscore before the last,
# we make the previous characters optional with an asterisk
RE_CLASS_PRIVATE: Pattern = re.compile(r"^__[\w_]*[^_]_?$")

# at most one leading underscore, then whatever
RE_PRIVATE: Pattern = re.compile(r"^_[^_][\w_]*$")

CATEGORY_ATTRIBUTE = "attribute"
CATEGORY_METHOD = "method"
CATEGORY_FUNCTION = "function"
CATEGORY_MODULE = "module"
CATEGORY_CLASS = "class"

NAME_SPECIAL = ("special", lambda n: bool(RE_SPECIAL.match(n)))
NAME_CLASS_PRIVATE = ("class-private", lambda n: bool(RE_CLASS_PRIVATE.match(n)))
NAME_PRIVATE = ("private", lambda n: bool(RE_PRIVATE.match(n)))


class Object:
    """
    Generic class to store information about a Python object.

    Each instance additionally stores references to its children, grouped by category.
    """

    NAME_PROPERTIES = []
    TOC_SIGNATURE = ""

    def __init__(
        self,
        name: str,
        path: str,
        file_path: str,
        docstring: Optional["Docstring"] = None,
        properties: Optional[List[str]] = None,
        source: Optional[Tuple[int, List[str]]] = None,
    ) -> None:
        """

        Parameters:
            name: The object name, like `__init__` or `MyClass`.
            path: The object dotted-path, like `package.submodule.class.inner_class.method`.
            file_path: The full file path of the object's module, like `/full/path/to/package/submodule.py`.
            docstring: A `Docstring` instance
            properties: A list of properties like `special`, `classmethod`, etc.
            source: A tuple with the object source code lines as a list, and the starting line in the object's module.
        """
        self.name = name
        self.path = path
        self.file_path = file_path
        self.docstring = docstring
        self.properties = properties or []
        self.parent = None
        self.source = source

        self._path_map = {self.path: self}

        self.attributes: List[Attribute] = []
        """List of all the object's attributes."""
        self.methods: List[Method] = []
        """List of all the object's methods."""
        self.functions: List[Function] = []
        """List of all the object's functions."""
        self.modules: List[Module] = []
        """List of all the object's submodules."""
        self.classes: List[Class] = []
        """List of all the object's classes."""
        self.children: List[Union[Attribute, Method, Function, Module, Class]] = []
        """List of all the object's children."""

    def __str__(self):
        return self.path

    @property
    def is_module(self):
        return isinstance(self, Module)

    @property
    def is_class(self):
        return isinstance(self, Class)

    @property
    def is_function(self):
        return isinstance(self, Function)

    @property
    def is_method(self):
        return isinstance(self, Method)

    @property
    def is_attribute(self):
        return isinstance(self, Attribute)

    @property
    def relative_file_path(self):
        path_parts = self.path.split(".")
        file_path_parts = self.file_path.split("/")
        file_path_parts[-1] = file_path_parts[-1].split(".", 1)[0]
        while path_parts[-1] != file_path_parts[-1]:
            path_parts.pop()
        while path_parts and path_parts[-1] == file_path_parts[-1]:
            path_parts.pop()
            file_path_parts.pop()
        return self.file_path[len("/".join(file_path_parts)) + 1 :]

    @property
    def name_to_check(self):
        return self.name

    @property
    def name_properties(self) -> List[str]:
        properties = []
        for prop, predicate in self.NAME_PROPERTIES:
            if predicate(self.name_to_check):
                properties.append(prop)
        return properties

    @property
    def parent_path(self) -> str:
        """The parent's path, computed from the current path."""
        return self.path.rsplit(".", 1)[0]

    def add_child(self, obj: Union["Attribute", "Method", "Function", "Module", "Class"]) -> None:
        """
        Add an object as a child of this object.

        Parameters:
            obj: An instance of documented object.
        """
        if obj.parent_path != self.path:
            return

        self.children.append(obj)
        if obj.is_module:
            self.modules.append(obj)
        elif obj.is_class:
            self.classes.append(obj)
        elif obj.is_function:
            self.functions.append(obj)
        elif obj.is_method:
            self.methods.append(obj)
        elif obj.is_attribute:
            self.attributes.append(obj)
        obj.parent = self

        self._path_map[obj.path] = obj

    def add_children(self, children: List[Union["Attribute", "Method", "Function", "Module", "Class"]]) -> None:
        """Add a list of objects as children of this object."""
        for child in children:
            self.add_child(child)

    def dispatch_attributes(self, attributes: List["Attribute"]) -> None:
        for attribute in attributes:
            try:
                attach_to = self._path_map[attribute.parent_path]
            except KeyError:
                pass
            else:
                attach_to.attributes.append(attribute)
                attach_to.children.append(attribute)
                attribute.parent = attach_to

    def has_contents(self):
        return bool(self.docstring.original_value or not self.parent or any(c.has_contents() for c in self.children))


class Module(Object):
    NAME_PROPERTIES = [NAME_SPECIAL, NAME_PRIVATE]

    @property
    def file_name(self):
        return os.path.splitext(os.path.basename(self.file_path))[0]

    @property
    def name_to_check(self):
        return self.file_name


class Class(Object):
    NAME_PROPERTIES = [NAME_PRIVATE]


class Function(Object):
    NAME_PROPERTIES = [NAME_PRIVATE]


class Method(Object):
    NAME_PROPERTIES = [NAME_SPECIAL, NAME_PRIVATE]


class Attribute(Object):
    NAME_PROPERTIES = [NAME_SPECIAL, NAME_CLASS_PRIVATE, NAME_PRIVATE]


class Documenter:
    """Class that contains the object documentation loading mechanisms."""

    def __init__(self, global_filters=None):
        if not global_filters:
            global_filters = []
        self.global_filters = [(f, re.compile(f.lstrip("!"))) for f in global_filters]

    def get_object_documentation(self, import_string: str) -> Union[Attribute, Method, Function, Module, Class]:
        """
        Documenting to see return type.

        Return:
            The object with all its children populated.
        """
        module, obj = import_object(import_string)
        attributes = get_attributes(module)
        if inspect.ismodule(obj):
            root_object = self.get_module_documentation(obj)
        elif inspect.isclass(obj):
            root_object = self.get_class_documentation(obj, module)
        elif inspect.isfunction(obj):
            root_object = self.get_function_documentation(obj, module)
        else:
            raise ValueError(f"{obj}:{type(obj)} not yet supported")
        root_object.dispatch_attributes([a for a in attributes if not self.filter_name_out(a.name)])
        return root_object

    def get_module_documentation(self, module: ModuleType) -> Module:
        path = module.__name__
        name = path.split(".")[-1]
        root_object = Module(
            name=name, path=path, file_path=module.__file__, docstring=Docstring(inspect.getdoc(module))
        )
        for member_name, member in (m for m in inspect.getmembers(module) if not self.filter_name_out(m[0])):
            if inspect.isclass(member) and inspect.getmodule(member) == module:
                root_object.add_child(self.get_class_documentation(member, module))
            elif inspect.isfunction(member) and inspect.getmodule(member) == module:
                root_object.add_child(self.get_function_documentation(member, module))

        try:
            package_path = module.__path__
        except AttributeError:
            pass
        else:
            for _, modname, _ in pkgutil.iter_modules(package_path):
                if not self.filter_name_out(modname):
                    parent, submodule = import_object(f"{name}.{modname}")
                    root_object.add_child(self.get_module_documentation(submodule))

        return root_object

    def get_class_documentation(self, class_: Type[Any], module: Optional[ModuleType] = None) -> Class:
        if module is None:
            module = inspect.getmodule(class_)
        class_name = class_.__name__
        path = f"{module.__name__}.{class_name}"
        file_path = module.__file__
        try:
            signature = inspect.signature(class_)
        except ValueError:
            print(f"Failed to get signature for {class_name}")
            signature = inspect.Signature()
        docstring = Docstring(textwrap.dedent(class_.__doc__ or ""), signature)
        root_object = Class(name=class_name, path=path, file_path=file_path, docstring=docstring,)

        for member_name, member in sorted(filter(lambda m: not self.filter_name_out(m[0]), class_.__dict__.items())):
            if inspect.isclass(member):
                root_object.add_child(self.get_class_documentation(member))
                continue

            member_class = properties = signature = None
            member_path = f"{path}.{member_name}"
            actual_member = getattr(class_, member_name)
            docstring = inspect.getdoc(actual_member) or ""
            try:
                source = inspect.getsourcelines(actual_member)
            except TypeError:
                source = ""

            if isinstance(member, classmethod):
                properties = ["classmethod"]
                member_class = Method
                signature = inspect.signature(actual_member)
            elif isinstance(member, staticmethod):
                properties = ["staticmethod"]
                member_class = Method
                signature = inspect.signature(actual_member)
            elif isinstance(member, type(lambda: 0)):  # regular method
                if RE_SPECIAL.match(member_name):
                    parent_classes = class_.__mro__[1:]
                    for parent_class in parent_classes:
                        try:
                            parent_member = getattr(parent_class, member_name)
                        except AttributeError:
                            continue
                        else:
                            if docstring == inspect.getdoc(parent_member):
                                docstring = ""
                            break
                member_class = Method
                signature = inspect.signature(actual_member)
            elif isinstance(member, property):
                properties = ["property", "readonly" if member.fset is None else "writable"]
                signature = inspect.signature(actual_member.fget)
                member_class = Attribute

            if member_class:
                root_object.add_child(
                    member_class(
                        name=member_name,
                        path=member_path,
                        file_path=file_path,
                        docstring=Docstring(docstring, signature),
                        properties=properties,
                        source=source,
                    )
                )
        return root_object

    def get_function_documentation(self, function: Callable, module: Optional[ModuleType] = None) -> Function:
        if module is None:
            module = inspect.getmodule(function)
        function_name = function.__name__
        path = f"{module.__name__}.{function_name}"
        return Function(
            name=function_name,
            path=path,
            file_path=module.__file__,
            docstring=Docstring(inspect.getdoc(function) or "", inspect.signature(function)),
            source=inspect.getsourcelines(function),
        )

    @lru_cache(maxsize=None)
    def filter_name_out(self, name: str) -> bool:
        if not self.global_filters:
            return False
        keep = True
        for f, regex in self.global_filters:
            is_matching = bool(regex.match(name))
            if is_matching:
                if str(f).startswith("!"):
                    is_matching = not is_matching
                keep = is_matching
        return not keep


def node_is_docstring(node: ast.AST) -> bool:
    return isinstance(node, ast.Expr) and isinstance(node.value, ast.Str)


def node_to_docstring(node: Union[ast.Expr, ast.Str]) -> str:
    return node.value.s


def node_is_assignment(node: ast.AST) -> bool:
    return isinstance(node, ast.Assign)


def node_is_annotated_assignment(node: ast.AST) -> bool:
    return isinstance(node, ast.AnnAssign)


def node_to_names(node: ast.Assign) -> dict:
    names = []
    for target in node.targets:
        if isinstance(target, ast.Attribute):
            names.append(target.attr)
        elif isinstance(target, ast.Name):
            names.append(target.id)
    return {"names": names, "lineno": node.lineno, "signature": None}


def node_to_annotated_names(node: ast.AnnAssign) -> dict:
    try:
        name = node.target.id
    except AttributeError:
        name = node.target.attr
    lineno = node.lineno
    return {"names": [name], "lineno": lineno, "signature": node_to_annotation(node)}


def node_to_annotation(node) -> str:
    if isinstance(node, ast.AnnAssign):
        try:
            annotation = node.annotation.id
        except AttributeError:
            annotation = node.annotation.value.id
        if hasattr(node.annotation, "slice"):
            annotation += f"[{node_to_annotation(node.annotation.slice.value)}]"
        return annotation
    elif isinstance(node, ast.Subscript):
        return f"{node.value.id}[{node_to_annotation(node.slice.value)}]"
    elif isinstance(node, ast.Tuple):
        return ", ".join(node_to_annotation(n) for n in node.elts)
    elif isinstance(node, ast.Name):
        return node.id


def get_attribute_info(node1, node2):
    if node_is_docstring(node2):
        info = {"docstring": node_to_docstring(node2)}
        if node_is_assignment(node1):
            info.update(node_to_names(node1))
            return info
        elif node_is_annotated_assignment(node1):
            info.update(node_to_annotated_names(node1))
            return info
    raise ValueError(f"nodes must be assignment and docstring, not '{node1}' and '{node2}'")


@lru_cache(maxsize=None)
def get_attributes(module: ModuleType) -> List[Attribute]:
    file_path = module.__file__
    with open(file_path) as stream:
        code = stream.read()
    initial_ast_body = ast.parse(code).body
    return _get_attributes(initial_ast_body, name_prefix=module.__name__, file_path=file_path)


def _get_attributes(
    ast_body: list, name_prefix: str, file_path: str, properties: Optional[List[str]] = None
) -> List[Attribute]:
    if not properties:
        properties = []
    documented_attributes = []
    previous_node = None
    for node in ast_body:
        try:
            attr_info = get_attribute_info(previous_node, node)
        except ValueError:
            if isinstance(node, RECURSIVE_NODES):
                documented_attributes.extend(_get_attributes(node.body, name_prefix, file_path, properties))
                if isinstance(node, ast.Try):
                    documented_attributes.extend(_get_attributes(node.finalbody, name_prefix, file_path, properties))
            elif isinstance(node, ast.FunctionDef) and node.name == "__init__":
                documented_attributes.extend(_get_attributes(node.body, name_prefix, file_path))
            elif isinstance(node, ast.ClassDef):
                documented_attributes.extend(
                    _get_attributes(node.body, f"{name_prefix}.{node.name}", file_path, properties=["class"])
                )
        else:
            for name in attr_info["names"]:
                documented_attributes.append(
                    Attribute(
                        name=name,
                        path=f"{name_prefix}.{name}",
                        file_path=file_path,
                        docstring=Docstring(attr_info["docstring"], attr_info["signature"]),
                        properties=properties,
                    )
                )
        previous_node = node
    return documented_attributes


def import_object(path: str) -> Tuple[ModuleType, Any]:
    """
    Transform a path into an actual Python object.

    The path can be arbitrary long. You can pass the path to a package,
    a module, a class, a function or a global variable, as deep as you
    want, as long as the deepest module is importable through
    ``importlib.import_module`` and each object is obtainable through
    the ``getattr`` method. Local objects will not work.

    Args:
        path: the dot-separated path of the object.

    Returns:
        The imported module and obtained object.
    """
    if not path:
        raise ValueError(f"path must be a valid Python path, not {path}")

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
