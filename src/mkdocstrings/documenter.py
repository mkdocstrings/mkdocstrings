"""Documenter module docstring."""

import ast
import importlib
import inspect
import os
import re
import sys
import textwrap
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
    toc_signature = ""

    def __init__(
        self,
        name: str,
        path: str,
        file_path: str,
        docstring: "Docstring",
        properties: Optional[List[str]] = None,
        source: Optional[str] = None,
        file: Optional[str] = None,
    ) -> None:
        self.name = name
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

    def should_be_displayed(self):
        return bool(
            self.docstring.original_value or not self.parent or any(c.should_be_displayed() for c in self.children)
        )

    def render(self, heading: int = 1, config: Dict[str, Any] = None) -> str:
        """
        Render this object as Markdown.

        This is dirty and will be refactored as a Markdown extension soon.

        Parameters:
            heading: The initial level of heading to use.
            config: The rendering configuration dictionary.

        Returns:
            The rendered Markdown.
        """
        if not config:
            config = {}

        lines = []

        show_top_object_heading = config.pop("show_top_object_heading", True)

        if show_top_object_heading:
            lines.append(self.render_heading(heading, config) + "\n")

        if self.docstring:
            lines.append(self.render_docstring() + "\n")

        if config["group_by_categories"]:
            lines.append(self.render_categories(heading + 1, config))
        else:
            for child in sorted(self.children, key=lambda o: o.name.lower()):
                lines.append(child.render(heading + 1, config))
                lines.append("")

        return "\n".join(lines)

    def render_references(self, base_url: str):
        lines = [f"[{self.path}]: {base_url}#{self.path}"]
        for child in self.children:
            lines.append(child.render_references(base_url))
        return "\n".join(lines)

    def render_heading(self, heading, config):
        show_top_object_full_path = config.pop("show_top_object_full_path", False)

        lines = []

        if not config["hide_no_doc"] or self.should_be_displayed():
            signature = self.render_signature()
            object_heading = f"`:::python {self.path if show_top_object_full_path else self.name}{signature}`"
            object_permalink = self.path.replace("__", r"\_\_")
            object_toc = self.name.replace("__", r"\_\_") + self.toc_signature

            if self.properties:
                object_heading += f"*({', '.join(self.properties)})*"

            lines.append(f"{'#' * heading} {object_heading} {{: #{object_permalink} data-toc-label='{object_toc}' }}")

            lines.append(self.render_source(config))

        return "\n".join(lines)

    def render_signature(self):
        return ""

    def render_docstring(self):
        lines = []

        for block_type, block in self.docstring.blocks:
            if block_type == "markdown":
                lines.extend(block)
            elif block_type == "parameters":
                lines.append("**Parameters**\n")
                lines.append("| Name | Type | Description | Default |")
                lines.append("| ---- | ---- | ----------- | ------- |")
                for parameter in block:
                    default = parameter.default_string
                    default = f"`{default}`" if default else "*required*"
                    lines.append(
                        f"| `{parameter.name}` | `{parameter.annotation_string}` | {parameter.description} | {default} |"
                    )
                lines.append("")
            elif block_type == "exceptions":
                lines.append("**Exceptions**\n")
                lines.append("| Type | Description |")
                lines.append("| ---- | ----------- |")
                for exception in block:
                    lines.append(f"| `{exception.annotation_string}` | {exception.description} |")
                lines.append("")
            elif block_type == "return":
                lines.append("**Returns**\n")
                lines.append("| Type | Description |")
                lines.append("| ---- | ----------- |")
                lines.append(f"| `{block.annotation_string}` | {block.description} |")
                lines.append("")
            elif block_type == "admonition":
                lines.append(f"!!! {block[0]}")
                lines.extend(block[1:])

        return "\n".join(lines)

    def render_source(self, config):
        lines = []
        if config["add_source_details"] and self.source:
            lines.append("")
            lines.append(f'??? note "Show source code in {self.relative_file_path}"')
            lines.append(f'    ```python linenums="{self.source[1]}"')
            lines.append(textwrap.indent("".join(self.source[0]), "    "))
            lines.append("    ```")
            lines.append("")
        return "\n".join(lines)

    def render_categories(self, heading, config):
        extra_level = 1 if config["show_groups_headings"] else 0
        lines = []

        if self.attributes:
            if config["show_groups_headings"]:
                lines.append(f"{'#' * heading} Attributes")
                lines.append("")
            for attribute in sorted(self.attributes, key=lambda o: o.name.lower()):
                lines.append(attribute.render(heading + extra_level, config))
                lines.append("")
        if self.classes:
            if config["show_groups_headings"]:
                lines.append(f"{'#' * heading} Classes")
                lines.append("")
            for class_ in sorted(self.classes, key=lambda o: o.name.lower()):
                lines.append(class_.render(heading + extra_level, config))
                lines.append("")
        if self.methods:
            if config["show_groups_headings"]:
                lines.append(f"{'#' * heading} Methods")
                lines.append("")
            for method in sorted(self.methods, key=lambda o: o.name.lower()):
                lines.append(method.render(heading + extra_level, config))
                lines.append("")
        if self.functions:
            if config["show_groups_headings"]:
                lines.append(f"{'#' * heading} Functions")
                lines.append("")
            for function in sorted(self.functions, key=lambda o: o.name.lower()):
                lines.append(function.render(heading + extra_level, config))
                lines.append("")
        return "\n".join(lines)


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


class FunctionOrMethod(Object):
    toc_signature = "()"

    def render_signature(self):
        if self.docstring.signature:
            # credits to https://github.com/tomchristie/mkautodoc
            params = []
            render_pos_only_separator = True
            render_kw_only_separator = True
            for parameter in self.docstring.signature.parameters.values():
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
            return f"({', '.join(params)})"
        return ""


class Function(FunctionOrMethod):
    NAME_PROPERTIES = [NAME_PRIVATE]


class Method(FunctionOrMethod):
    NAME_PROPERTIES = [NAME_SPECIAL, NAME_PRIVATE]


class Attribute(Object):
    NAME_PROPERTIES = [NAME_SPECIAL, NAME_CLASS_PRIVATE, NAME_PRIVATE]

    def render_signature(self):
        if "property" in self.properties:
            try:
                return f": {self.docstring.return_object.annotation_string}"
            except AttributeError:
                return AnnotatedObject(self.docstring.signature.return_annotation, "").annotation_string
        return f": {self.docstring.signature}"


class AnnotatedObject:
    def __init__(self, annotation, description):
        self.annotation = annotation
        self.description = description

    @property
    def annotation_string(self):
        if inspect.isclass(self.annotation) and not isinstance(self.annotation, GenericMeta):
            return self.annotation.__name__
        return str(self.annotation).replace("typing.", "")


class Parameter(AnnotatedObject):
    def __init__(self, name, annotation, description, kind, default=inspect.Signature.empty):
        super().__init__(annotation, description)
        self.name = name
        self.kind = kind
        self.default = default

    @property
    def optional(self):
        return self.default is not inspect.Signature.empty

    @property
    def required(self):
        return not self.optional

    @property
    def annotation_string(self):
        s = AnnotatedObject.annotation_string.fget(self)
        optional_param = re.match(r"^Union\[([^,]+), NoneType\]$", s)
        if optional_param:
            s = f"Optional[{optional_param.group(1)}]"
        optional_union_param = re.match(r"^Union\[(.+), NoneType\]$", s)
        if optional_union_param:
            s = f"Optional[Union[{optional_union_param.group(1)}]]"
        return s

    @property
    def default_string(self):
        if self.default is inspect.Signature.empty:
            return ""
        return str(self.default)


class Docstring:
    def __init__(self, value, signature=None):
        self.original_value = value
        self.signature = signature
        self.return_object = None
        self.blocks = self.parse()

    # return a list of tuples of the form:
    # [("type", value), ...]
    # type being "markdown", "parameters", "exceptions", or "return"
    # and value respectively being a string, a list of Parameter, a list of AnnotatedObject, and an AnnotatedObject
    # This allows to respect the user's docstring order.
    # While rendering:
    # Sections like Note: and Warning: in markdown values should be regex-replaced by their admonition equivalent,
    # up to maximum 2 levels of indentation, and only if admonition is registered. Add a configuration option for this.
    # Then the markdown values are transformed by a Markdown transformation.
    def parse(self) -> List[Tuple[str, Union[List[str, AnnotatedObject, Parameter], AnnotatedObject]]]:
        """
        Parse a docstring!

        Note:
            to try notes.

        Returns:
            The docstring converted to a nice markdown text.
        """
        parameters = []
        exceptions = []
        blocks = []
        current_block = []

        lines = self.original_value.split("\n")
        i = 0

        while i < len(lines):
            line_lower = lines[i].lower()
            if line_lower in ("args:", "arguments:", "params:", "parameters:"):
                if current_block:
                    blocks.append(("markdown", current_block))
                    current_block = []
                block, i = self.read_block_items(lines, i + 1)
                for param_line in block:
                    name, description = param_line.lstrip(" ").split(": ")
                    try:
                        signature_param = self.signature.parameters[name]
                    except AttributeError:
                        print(f"no type annotation for parameter {name}", file=sys.stderr)
                    else:
                        parameters.append(
                            Parameter(
                                name=name,
                                annotation=signature_param.annotation,
                                description=description.lstrip(" "),
                                default=signature_param.default,
                                kind=signature_param.kind,
                            )
                        )
                blocks.append(("parameters", parameters))
                parameters = []
            elif line_lower in ("raise:", "raises:", "except:", "exceptions:"):
                if current_block:
                    blocks.append(("markdown", current_block))
                    current_block = []
                block, i = self.read_block_items(lines, i + 1)
                for exception_line in block:
                    annotation, description = exception_line.split(": ")
                    exceptions.append(AnnotatedObject(annotation, description.lstrip(" ")))
                blocks.append(("exceptions", exceptions))
                exceptions = []
            elif line_lower in ("return:", "returns:"):
                if current_block:
                    blocks.append(("markdown", current_block))
                    current_block = []
                block, i = self.read_block(lines, i + 1)
                try:
                    self.return_object = AnnotatedObject(self.signature.return_annotation, " ".join(block))
                    blocks.append(("return", self.return_object))
                except AttributeError:
                    print("no return type annotation", file=sys.stderr)
            elif line_lower in ADMONITIONS.keys():
                if current_block:
                    blocks.append(("markdown", current_block))
                    current_block = []
                admonition, i = self.read_block(lines, i + 1)
                admonition.insert(0, ADMONITIONS[line_lower])
                blocks.append(("admonition", admonition))
                # new_lines.append(f"!!! {ADMONITIONS[line_lower]}")
                # new_lines.append("\n".join(admonition))
                # new_lines.append("")
            else:
                current_block.append(lines[i])
            i += 1

        if current_block and any(current_block):
            blocks.append(("markdown", current_block))

        return blocks

    @staticmethod
    def read_block_items(lines, start_index):
        i = start_index
        block = []
        while i < len(lines) and lines[i].startswith("    "):
            if block and lines[i].startswith("      "):
                block[-1] += " " + lines[i].lstrip(" ")
            else:
                block.append(lines[i])
            i += 1
        return block, i - 1

    @staticmethod
    def read_block(lines, start_index):
        i = start_index
        block = []
        while i < len(lines) and (lines[i].startswith("    ") or lines[i] == ""):
            block.append(lines[i])
            i += 1
        return block, i - 1


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
        root_object = Module(
            name=name, path=path, file_path=module.__file__, docstring=Docstring(inspect.getdoc(module))
        )
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
            docstring=Docstring(textwrap.dedent(class_.__doc__ or ""), inspect.signature(class_)),
        )

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
