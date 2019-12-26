"""Documenter module docstring."""

import ast
import importlib
import inspect
import os
import re
import textwrap
from collections import namedtuple
from functools import lru_cache
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Pattern, Tuple, Type, Union

try:
    from typing import GenericMeta  # python 3.6
except ImportError:
    # in 3.7, GenericMeta doesn't exist but we don't need it
    class GenericMeta(type):
        pass


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

ADMONITIONS = {
    "note:": "note",
    "see also:": "seealso",
    "abstract:": "abstract",
    "summary:": "summary",
    "tldr:": "tldr",
    "info:": "info",
    "information:": "info",
    "todo:": "todo",
    "tip:": "tip",
    "hint:": "hint",
    "important:": "important",
    "success:": "success",
    "check:": "check",
    "done:": "done",
    "question:": "question",
    "help:": "help",
    "faq:": "faq",
    "warning:": "warning",
    "caution:": "caution",
    "attention:": "attention",
    "failure:": "failure",
    "fail:": "fail",
    "missing:": "missing",
    "danger:": "danger",
    "error:": "error",
    "bug:": "bug",
    "example:": "example",
    "snippet:": "snippet",
    "quote:": "quote",
    "cite:": "cite",
}


class Object:
    """
    Class to store information about a Python object.

    - the object category (ex: module, function, class, method or attribute)
    - the object path (ex: `package.submodule.class.inner_class.method`)
    - the object name (ex: `__init__`)
    - the object docstring
    - the object properties, depending on its category (ex: special, classmethod, etc.)
    - the object signature (soon)

    Each instance additionally stores references to its children, grouped by category (see Attributes).
    """

    NAME_PROPERTIES = []

    def __init__(
        self,
        name: str,
        path: str,
        file_path: str,
        docstring: str,
        properties: Optional[List[str]] = None,
        signature: Optional[inspect.Signature] = None,
        source: Optional[str] = None,
        file: Optional[str] = None,
    ) -> None:
        self.name = name
        self.signature = signature or ""
        self.path = path
        self.file_path = file_path
        self.docstring = docstring or ""
        self.properties = properties or []
        self.parent = None
        self.source = source or ""
        self.file = file or ""

        self._path_map = {}

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
        return False

    @property
    def is_class(self):
        return False

    @property
    def is_function(self):
        return False

    @property
    def is_method(self):
        return False

    @property
    def is_attribute(self):
        return False

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
        """Add an object as a child of this object."""
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

    def render_references(self, base_url: str):
        lines = [f"[{self.path}]: {base_url}#{self.path}"]
        for child in self.children:
            lines.append(child.render_references(base_url))
        return "\n".join(lines)

    def render(self, heading: int = 1, **config: Dict[str, Any]) -> str:
        """
        Render this object as Markdown.

        This is dirty and will be refactored as a Markdown extension soon.

        Parameters:
            heading: The initial level of heading to use.
            config: The rendering configuration dictionary.

        Returns:
            The rendered Markdown.
        """
        lines = []

        show_top_object_heading = config.pop("show_top_object_heading", True)
        show_top_object_full_path = config.pop("show_top_object_full_path", False)
        if show_top_object_heading:
            if self.docstring or not config["hide_no_doc"] or not self.parent:
                signature = ""
                toc_signature = ""
                if self.is_function or self.is_method:
                    if self.signature:
                        signature = f"({render_signature(self.signature)})"
                    toc_signature = "()"
                elif self.is_attribute:
                    if "property" in self.properties:
                        signature = f": {get_return_type(self.signature)}"
                    else:
                        signature = f": {self.signature}"
                object_heading = f"`:::python {self.path if show_top_object_full_path else self.name}{signature}`"
                object_permalink = self.path.replace("__", r"\_\_")
                object_toc = self.name.replace("__", r"\_\_") + toc_signature

                properties = ", ".join(self.properties)
                if properties:
                    object_heading += f"*({properties})*"

                lines.append(
                    f"{'#' * heading} {object_heading} {{: #{object_permalink} data-toc-label='{object_toc}' }}"
                )

                if config["add_source_details"] and self.source:
                    lines.append("")
                    lines.append(f'??? note "Show source code"')
                    lines.append(f'    ```python linenums="{self.source[1]}"')
                    lines.append(textwrap.indent("".join(self.source[0]), "    "))
                    lines.append("    ```")
                    lines.append("")

        if self.docstring:
            lines.append(parse_docstring(self.docstring, self.signature))
            lines.append("")

        if config["group_by_categories"]:
            lines.append(self.render_categories(heading + 1, **config,))
        else:
            for child in sorted(self.children, key=lambda o: o.name.lower()):
                lines.append(child.render(heading + 1, **config,))
                lines.append("")

        return "\n".join(lines)

    def render_categories(self, heading: int, **config):
        extra_level = 1 if config["show_groups_headings"] else 0
        lines = []

        if self.attributes:
            if config["show_groups_headings"]:
                lines.append(f"{'#' * heading} Attributes")
                lines.append("")
            for attribute in sorted(self.attributes, key=lambda o: o.name.lower()):
                lines.append(attribute.render(heading + extra_level, **config))
                lines.append("")
        if self.classes:
            if config["show_groups_headings"]:
                lines.append(f"{'#' * heading} Classes")
                lines.append("")
            for class_ in sorted(self.classes, key=lambda o: o.name.lower()):
                lines.append(class_.render(heading + extra_level, **config))
                lines.append("")
        if self.methods:
            if config["show_groups_headings"]:
                lines.append(f"{'#' * heading} Methods")
                lines.append("")
            for method in sorted(self.methods, key=lambda o: o.name.lower()):
                lines.append(method.render(heading + extra_level, **config))
                lines.append("")
        if self.functions:
            if config["show_groups_headings"]:
                lines.append(f"{'#' * heading} Functions")
                lines.append("")
            for function in sorted(self.functions, key=lambda o: o.name.lower()):
                lines.append(function.render(heading + extra_level, **config))
                lines.append("")
        return "\n".join(lines)


class Module(Object):
    NAME_PROPERTIES = [NAME_SPECIAL, NAME_PRIVATE]

    @property
    def is_module(self):
        return True

    @property
    def file_name(self):
        return os.path.splitext(os.path.basename(self.file_path))[0]

    @property
    def name_to_check(self):
        return self.file_name


class Class(Object):
    NAME_PROPERTIES = [NAME_PRIVATE]

    @property
    def is_class(self):
        return True


class Function(Object):
    NAME_PROPERTIES = [NAME_PRIVATE]

    @property
    def is_function(self):
        return True


class Method(Object):
    NAME_PROPERTIES = [NAME_SPECIAL, NAME_PRIVATE]

    @property
    def is_method(self):
        return True


class Attribute(Object):
    NAME_PROPERTIES = [NAME_SPECIAL, NAME_CLASS_PRIVATE, NAME_PRIVATE]

    @property
    def is_attribute(self):
        return True


class Documenter:
    """Class that contains the object documentation loading mechanisms."""

    def __init__(self, global_filters):
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
        root_object = Module(name=name, path=path, file_path=module.__file__, docstring=inspect.getdoc(module),)
        for member_name, member in filter(lambda m: not self.filter_name_out(m[0]), inspect.getmembers(module)):
            if inspect.isclass(member) and inspect.getmodule(member) == module:
                root_object.add_child(self.get_class_documentation(member, module))
            elif inspect.isfunction(member) and inspect.getmodule(member) == module:
                root_object.add_child(self.get_function_documentation(member, module))
        return root_object

    def get_class_documentation(self, class_: Type[Any], module: Optional[ModuleType] = None) -> Class:
        if module is None:
            module = inspect.getmodule(class_)
        class_name = class_.__name__
        path = f"{module.__name__}.{class_name}"
        file_path = module.__file__
        root_object = Class(
            name=class_name,
            path=path,
            file_path=file_path,
            docstring=textwrap.dedent(class_.__doc__ or ""),
            signature=inspect.signature(class_),
        )

        for member_name, member in sorted(filter(lambda m: not self.filter_name_out(m[0]), class_.__dict__.items())):
            if inspect.isclass(member):
                root_object.add_child(self.get_class_documentation(member))
                continue

            member_class = properties = signature = None
            member_path = f"{path}.{member_name}"
            actual_member = getattr(class_, member_name)
            docstring = inspect.getdoc(actual_member)
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
                        docstring=docstring,
                        properties=properties,
                        source=source,
                        signature=signature,
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
            docstring=inspect.getdoc(function),
            source=inspect.getsourcelines(function),
            signature=inspect.signature(function),
        )

    @lru_cache(maxsize=None)
    def filter_name_out(self, name: str) -> bool:
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
    name = node.target.attr
    lineno = node.lineno
    return {"names": [name], "lineno": lineno, "signature": node_to_annotation(node)}


def node_to_annotation(node) -> str:
    if isinstance(node, ast.AnnAssign):
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
                        docstring=attr_info["docstring"],
                        properties=properties,
                        signature=attr_info["signature"],
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
        tuple: the imported module and obtained object.
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


def render_signature(signature):
    # credits to https://github.com/tomchristie/mkautodoc
    params = []
    render_pos_only_separator = True
    render_kw_only_separator = True
    for parameter in signature.parameters.values():
        value = parameter.name
        if parameter.default is not parameter.empty:
            value = f"{value}={parameter.default!r}"
        if parameter.kind is parameter.VAR_POSITIONAL:
            render_kw_only_separator = False
            value = f"*{value}"
        elif parameter.kind is parameter.VAR_KEYWORD:
            value = f"**{value}"
        elif parameter.kind is parameter.POSITIONAL_ONLY:
            if render_pos_only_separator:
                render_pos_only_separator = False
                params.append("/")
        elif parameter.kind is parameter.KEYWORD_ONLY:
            if render_kw_only_separator:
                render_kw_only_separator = False
                params.append("*")
        params.append(value)
    return ", ".join(params)


def get_param_info(signature, param_name):
    parameter = signature.parameters[param_name]
    param_default = param_type = ""
    if parameter.annotation is not parameter.empty:
        if inspect.isclass(parameter.annotation) and not isinstance(parameter.annotation, GenericMeta):
            param_type = parameter.annotation.__name__
        else:
            param_type = str(parameter.annotation).replace("typing.", "")
        optional_param = re.match(r"^Union\[([^,]+), NoneType\]$", param_type)
        if optional_param:
            param_type = f"Optional[{optional_param.group(1)}]"
    if parameter.kind is parameter.VAR_KEYWORD:
        param_name = f"**{param_name}"
    if parameter.default is not parameter.empty:
        param_default = str(parameter.default)
    return namedtuple("Param", "name default type")(param_name, param_default, param_type)


def get_return_type(signature):
    ret = signature.return_annotation
    if ret is not signature.empty:
        if inspect.isclass(ret) and not isinstance(ret, GenericMeta):
            ret_type = ret.__name__
        else:
            ret_type = str(ret).replace("typing.", "")
    else:
        ret_type = ""
    return ret_type


def parse_docstring(docstring: str, signature: inspect.Signature) -> str:
    """
    Parse a docstring!

    Note:
        to try notes.

    Args:
        docstring: This is the docstring to parse.
        signature: The signature returned by inspect.

    Raises:
        OSError: no it doesn't lol.

    Returns:
        markdown: the docstring converted to a nice markdown text.
    """
    params = {}
    exceptions = {}
    returns = ""
    lines = docstring.split("\n")
    new_lines = []
    i = 0
    while i < len(lines):
        if lines[i].lower() in ("args:", "arguments:", "params:", "parameters:"):
            j = i + 1
            name = None
            while j < len(lines) and lines[j].startswith("    "):
                if lines[j].startswith("      ") and params[name]:
                    params[name] += " " + lines[j].lstrip(" ")
                else:
                    name, description = lines[j].lstrip(" ").split(":", 1)
                    params[name] = description.lstrip(" ")
                j += 1
            new_lines.append("**Parameters**\n")
            new_lines.append("| Name | Type | Description | Default |")
            new_lines.append("| ---- | ---- | ----------- | ------- |")
            for param_name, param_description in params.items():
                param_name, param_default, param_type = get_param_info(signature, param_name)
                if param_default:
                    param_default = f"`{param_default}`"
                else:
                    param_default = "*required*"
                new_lines.append(f"| `{param_name}` | `{param_type}` | {param_description} | {param_default} |")
            new_lines.append("")
            i = j - 1
        elif lines[i].lower() in ("raise:", "raises:", "except:", "exceptions:"):
            j = i + 1
            name = None
            while j < len(lines) and lines[j].startswith("    "):
                if lines[j].startswith("      ") and exceptions[name]:
                    exceptions[name] += " " + lines[j].lstrip(" ")
                else:
                    name, description = lines[j].lstrip(" ").split(":", 1)
                    exceptions[name] = description.lstrip(" ")
                j += 1
            new_lines.append("**Exceptions**\n")
            new_lines.append("| Type | Description |")
            new_lines.append("| ---- | ----------- |")
            for exception_name, exception_description in exceptions.items():
                new_lines.append(f"| `{exception_name}` | {exception_description} |")
            new_lines.append("")
            i = j - 1
        elif lines[i].lower() in ("return:", "returns:"):
            j = i + 1
            while j < len(lines) and lines[j].startswith("    "):
                description = lines[j].lstrip(" ")
                returns += " " + description
                j += 1
            new_lines.append("**Returns**\n")
            new_lines.append("| Type | Description |")
            new_lines.append("| ---- | ----------- |")
            new_lines.append(f"| `{get_return_type(signature)}` | {returns} |")
            new_lines.append("")
            i = j - 1
        elif lines[i].lower() in ADMONITIONS.keys():
            j = i + 1
            admonition = []
            while j < len(lines) and (lines[j].startswith("    ") or lines[j] == ""):
                admonition.append(lines[j])
                j += 1
            new_lines.append(f"!!! {ADMONITIONS[lines[i].lower()]}")
            new_lines.append("\n".join(admonition))
            new_lines.append("")
            i = j - 1
        else:
            new_lines.append(lines[i])
        i += 1

    return "\n".join(new_lines)
