import inspect
import re
import sys
from typing import List, Tuple, Union

from .utils import annotation_to_string

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


class AnnotatedObject:
    def __init__(self, annotation, description):
        self.annotation = annotation
        self.description = description

    @property
    def annotation_string(self):
        return annotation_to_string(self.annotation)


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
    def parse(self) -> List[Tuple[str, Union[List[Union[str, AnnotatedObject, Parameter]], AnnotatedObject]]]:
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

        in_code_block = False

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
                    name, description = param_line.lstrip(" ").split(":", 1)
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
            elif (
                not line_lower.startswith("     ")
                and line_lower.lstrip(" ") in ADMONITIONS.keys()
                and not in_code_block
            ):
                if current_block:
                    blocks.append(("markdown", current_block))
                    current_block = []
                admonition, i = self.read_block(lines, i + 1)
                key = line_lower.lstrip(" ")
                leading_spaces = len(line_lower) - len(key)
                admonition.insert(0, (leading_spaces, ADMONITIONS[key]))
                blocks.append(("admonition", admonition))
                # new_lines.append(f"!!! {ADMONITIONS[line_lower]}")
                # new_lines.append("\n".join(admonition))
                # new_lines.append("")
            elif line_lower.lstrip(" ").startswith("```"):
                in_code_block = not in_code_block
                current_block.append(lines[i])
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
