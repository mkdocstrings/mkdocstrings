import re
import textwrap

from .docstrings import Section
from .utils import annotation_to_string

RE_AUTODOC_TITLE = re.compile(r'<h[1-6] id="([\w.]+)"><code class="codehilite">')


class MarkdownRenderer:
    def __init__(
        self,
        top_config,
        group_by_categories=True,
        show_groups_headings=False,
        hide_no_doc=True,
        add_source_details=True,
    ):
        self.top_config = top_config
        self.group_by_categories = group_by_categories
        self.show_groups_headings = show_groups_headings
        self.hide_no_doc = hide_no_doc
        self.add_source_details = add_source_details

    def render(self, obj, heading_level):
        lines = []
        self.render_object(obj, heading_level, lines)
        return lines

    def render_object(self, obj, heading_level, lines):
        show_top_object_heading = self.top_config.pop("show_top_object_heading", True)
        show_top_object_full_path = self.top_config.pop("show_top_object_full_path", False)

        if show_top_object_heading and (not self.hide_no_doc or obj.has_contents()):
            signature = render_signature(obj)
            module_heading = f"`:::python {obj.path if show_top_object_full_path else obj.name}{signature}`"
            module_permalink = obj.path.replace("__", r"\_\_")
            module_toc_title = obj.name.replace("__", r"\_\_")
            if obj.is_method or obj.is_function:
                module_toc_title += "()"

            if obj.properties:
                module_heading += f" *({', '.join(obj.properties)})*"

            lines.append(
                f"{'#' * heading_level} {module_heading} {{: #{module_permalink} data-toc-label='{module_toc_title}' }}"
            )

            if self.add_source_details and obj.source:
                lines.append(f'\n??? note "Show source code in {obj.relative_file_path}"')
                lines.append(f'    ```python linenums="{obj.source[1]}"')
                lines.append(textwrap.indent("".join(obj.source[0]), "    "))
                lines.append("    ```\n")

        if obj.docstring:
            render_docstring(obj, lines)

        if self.group_by_categories:
            self.render_categories(obj, heading_level + 1, lines)
        else:
            for child in sorted(obj.children, key=lambda o: o.name.lower()):
                self.render_object(child, heading_level + 1, lines)

    def render_categories(self, obj, heading_level, lines):
        extra_level = 1 if self.show_groups_headings else 0
        if obj.attributes:
            if self.show_groups_headings:
                lines.append(f"{'#' * heading_level} Attributes\n")
            for attribute in sorted(obj.attributes, key=lambda o: o.name.lower()):
                self.render_object(attribute, heading_level + extra_level, lines)
        if obj.classes:
            if self.show_groups_headings:
                lines.append(f"{'#' * heading_level} Classes\n")
            for class_ in sorted(obj.classes, key=lambda o: o.name.lower()):
                self.render_object(class_, heading_level + extra_level, lines)
        if obj.methods:
            if self.show_groups_headings:
                lines.append(f"{'#' * heading_level} Methods\n")
            for method in sorted(obj.methods, key=lambda o: o.name.lower()):
                self.render_object(method, heading_level + extra_level, lines)
        if obj.functions:
            if self.show_groups_headings:
                lines.append(f"{'#' * heading_level} Functions\n")
            for function in sorted(obj.functions, key=lambda o: o.name.lower()):
                self.render_object(function, heading_level + extra_level, lines)
        if obj.modules:
            if self.show_groups_headings:
                lines.append(f"{'#' * heading_level} Modules\n")
            for module in sorted(obj.modules, key=lambda o: o.name.lower()):
                self.render_object(module, heading_level + extra_level, lines)


def render_references(obj, base_url: str):
    lines = [f"[{obj.path}]: {base_url}#{obj.path}"]
    for child in obj.children:
        lines.append(render_references(child, base_url))
    return "\n".join(lines)


def render_docstring(obj, lines):
    for section in obj.docstring.blocks:
        if section.type == Section.Type.MARKDOWN:
            lines.extend(section.value)
        elif section.type == Section.Type.PARAMETERS:
            lines.append("**Parameters**\n")
            lines.append("| Name | Type | Description | Default |")
            lines.append("| ---- | ---- | ----------- | ------- |")
            for parameter in section.value:
                name = parameter.name
                if parameter.is_kwargs:
                    name = f"**{name}"
                elif parameter.is_args:
                    name = f"*{name}"
                default = parameter.default_string
                default = f"`{default}`" if default else "*required*"
                lines.append(f"| `{name}` | `{parameter.annotation_string}` | {parameter.description} | {default} |")
            lines.append("")
        elif section.type == Section.Type.EXCEPTIONS:
            lines.append("**Exceptions**\n")
            lines.append("| Type | Description |")
            lines.append("| ---- | ----------- |")
            for exception in section.value:
                lines.append(f"| `{exception.annotation_string}` | {exception.description} |")
            lines.append("")
        elif section.type == Section.Type.RETURN:
            lines.append("**Returns**\n")
            lines.append("| Type | Description |")
            lines.append("| ---- | ----------- |")
            lines.append(f"| `{section.value.annotation_string}` | {section.value.description} |")
            lines.append("")
        elif section.type == Section.Type.ADMONITION:
            lines.append(f"{' ' * section.value[0][0]}!!! {section.value[0][1]}")
            lines.extend(section.value[1:])
    lines.append("")


def render_signature(obj):
    if obj.is_attribute:
        if "property" in obj.properties:
            return f": {annotation_to_string(obj.docstring.signature.return_annotation)}"
        return f": {obj.docstring.signature}"
    elif obj.is_function or obj.is_method:
        if obj.docstring.signature:
            # credits to https://github.com/tomchristie/mkautodoc
            params = []
            render_pos_only_separator = True
            render_kw_only_separator = True
            for parameter in obj.docstring.signature.parameters.values():
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
                        value = "/"
                elif parameter.kind is parameter.KEYWORD_ONLY:
                    if render_kw_only_separator:
                        render_kw_only_separator = False
                        value = "*"
                params.append(value)
            return f"({', '.join(params)})"
    return ""


def insert_divs(html):
    div = '<div class="autodoc">'
    end_div = "</div>"
    lines = html.split("\n")
    new_lines = lines[::]
    levels = [0]
    inserted = 0
    for i, line in enumerate(lines):
        if RE_AUTODOC_TITLE.match(line):
            level = int(line[2])
            if level > levels[-1]:
                new_lines.insert(i + 1 + inserted, div)
                inserted += 1
                levels.append(level)
            elif level == levels[-1]:
                new_lines.insert(i + inserted, end_div)
                inserted += 1
                new_lines.insert(i + 1 + inserted, div)
                inserted += 1
            else:
                while level < levels[-1]:
                    new_lines.insert(i + inserted, end_div)
                    inserted += 1
                    levels.pop()
                new_lines.insert(i + inserted, end_div)
                inserted += 1
                new_lines.insert(i + 1 + inserted, div)
                inserted += 1
    while levels[-1] > 0:
        new_lines.append(end_div)
        levels.pop()
    new_html = "\n".join(new_lines)
    return new_html
