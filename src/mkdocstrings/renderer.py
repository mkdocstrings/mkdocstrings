import re
import textwrap

from markdown import Markdown
from markdown.util import etree
from pymdownx.highlight import Highlight

from .docstrings import Section
from .utils import annotation_to_string

Element = etree.Element
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
            signature = self.render_signature(obj)
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
            self.render_docstring(obj, lines)

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

    @staticmethod
    def render_references(obj, base_url: str):
        lines = [f"[{obj.path}]: {base_url}#{obj.path}"]
        for child in obj.children:
            lines.append(MarkdownRenderer.render_references(child, base_url))
        return "\n".join(lines)

    @staticmethod
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

    @staticmethod
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


class HTMLRenderer:
    def __init__(
        self,
        md,
        top_config,
        group_by_categories=True,
        show_groups_headings=False,
        hide_no_doc=True,
        add_source_details=True,
    ):
        self.md = md
        self.top_config = top_config
        self.group_by_categories = group_by_categories
        self.show_groups_headings = show_groups_headings
        self.hide_no_doc = hide_no_doc
        self.add_source_details = add_source_details

    def render(self, obj, heading_level, parent):
        elem = etree.SubElement(parent, "div", {"class": "autodoc"})
        self.render_object(obj, heading_level, elem)
        return elem

    def render_object(self, obj, heading_level, elem: etree.Element):
        show_top_object_heading = self.top_config.pop("show_top_object_heading", True)
        show_top_object_full_path = self.top_config.pop("show_top_object_full_path", False)

        if show_top_object_heading and (not self.hide_no_doc or obj.has_contents()):
            signature = self.render_signature(obj)
            object_heading = f"{obj.path if show_top_object_full_path else obj.name}{signature}"
            object_heading.replace("_", "\\_")
            object_heading = Highlight().highlight(src=object_heading, language="python", inline=True, css_class="codehilite")
            object_permalink = obj.path
            object_toc_title = obj.name
            if obj.is_method or obj.is_function:
                object_toc_title += "()"

            # if obj.properties:
            #     object_heading += f" <em>({', '.join(obj.properties)})</em>"

            elem_heading = etree.SubElement(elem, f"h{min(6, heading_level)}")
            elem_heading.set("class", "autodoc-signature")
            elem_heading.set("data-toc-label", object_toc_title)
            elem_heading.set("id", object_permalink)
            elem_heading.append(object_heading)
            permalink = Element("a", {"class": "headerlink", "href": f"#{object_permalink}", "title": "Permanent link"})
            permalink.text = "¶"
            elem_heading.append(permalink)

            if self.add_source_details and obj.source:
                elem_source = etree.SubElement(elem, "details")
                elem_source_summary = etree.SubElement(elem_source, "summary")
                elem_source_summary.text = f"Show source code in {obj.relative_file_path}"
                h = Highlight(guess_lang=False).highlight(
                    src=textwrap.dedent(textwrap.indent("".join(obj.source[0]), "    ")),
                    language="python",
                    linestart=obj.source[1]
                )
                elem_source.append(etree.XML(h))

        if obj.docstring:
            self.render_docstring(obj, elem)

        if self.group_by_categories:
            self.render_categories(obj, heading_level + 1, elem)
        else:
            for child in sorted(obj.children, key=lambda o: o.name.lower()):
                self.render_object(child, heading_level + 1, elem)

    def render_categories(self, obj, heading_level, elem: etree.Element):
        extra_level = 1 if self.show_groups_headings else 0
        if obj.attributes:
            if self.show_groups_headings:
                elem_group_heading = etree.SubElement(elem, f"h{min(6, heading_level)}")
                elem_group_heading.text = "Attributes"
            for attribute in sorted(obj.attributes, key=lambda o: o.name.lower()):
                self.render_object(attribute, heading_level + extra_level, elem)
        if obj.classes:
            if self.show_groups_headings:
                elem_group_heading = etree.SubElement(elem, f"h{min(6, heading_level)}")
                elem_group_heading.text = "Classes"
            for class_ in sorted(obj.classes, key=lambda o: o.name.lower()):
                self.render_object(class_, heading_level + extra_level, elem)
        if obj.methods:
            if self.show_groups_headings:
                elem_group_heading = etree.SubElement(elem, f"h{min(6, heading_level)}")
                elem_group_heading.text = "Methods"
            for method in sorted(obj.methods, key=lambda o: o.name.lower()):
                self.render_object(method, heading_level + extra_level, elem)
        if obj.functions:
            if self.show_groups_headings:
                elem_group_heading = etree.SubElement(elem, f"h{min(6, heading_level)}")
                elem_group_heading.text = "Functions"
            for function in sorted(obj.functions, key=lambda o: o.name.lower()):
                self.render_object(function, heading_level + extra_level, elem)
        if obj.modules:
            if self.show_groups_headings:
                elem_group_heading = etree.SubElement(elem, f"h{min(6, heading_level)}")
                elem_group_heading.text = "Modules"
            for module in sorted(obj.modules, key=lambda o: o.name.lower()):
                self.render_object(module, heading_level + extra_level, elem)

    def render_docstring(self, obj, elem: etree.Element):
        md = Markdown(extensions=self.md.registeredExtensions)
        for section in obj.docstring.blocks:
            if section.type == Section.Type.MARKDOWN:
                paragraph = etree.SubElement(elem, "p")
                paragraph.text = md.convert("\n".join(section.value))
            elif section.type == Section.Type.PARAMETERS:
                etree.SubElement(etree.SubElement(elem, "p"), "strong").text = "Parameters"
                table = etree.SubElement(elem, "table")
                thead_tr = etree.SubElement(etree.SubElement(table, "thead"), "tr")
                for column in "Name Type Description Default".split():
                    etree.SubElement(thead_tr, "th").text = column
                tbody = etree.SubElement(table, "tbody")
                for parameter in section.value:
                    tr = etree.SubElement(tbody, "tr")
                    name = parameter.name
                    if parameter.is_kwargs:
                        name = f"**{name}"
                    elif parameter.is_args:
                        name = f"*{name}"
                    default = parameter.default_string
                    default = f"<code>{default}</code>" if default else "<em>required</em>"
                    for cell in (
                        f"<code>{name}</code>",
                        f"<code>{parameter.annotation_string}</code>",
                        parameter.description,
                        default
                    ):
                        etree.SubElement(tr, "td").text = cell
            elif section.type == Section.Type.EXCEPTIONS:
                etree.SubElement(etree.SubElement(elem, "p"), "strong").text = "Exceptions"
                table = etree.SubElement(elem, "table")
                thead_tr = etree.SubElement(etree.SubElement(table, "thead"), "tr")
                for column in ("Type", "Description"):
                    etree.SubElement(thead_tr, "th").text = column
                tbody = etree.SubElement(table, "tbody")
                for exception in section.value:
                    tr = etree.SubElement(tbody, "tr")
                    etree.SubElement(tr, "td").text = f"<code>{exception.annotation_string}</code>"
                    etree.SubElement(tr, "td").text = exception.description
            elif section.type == Section.Type.RETURN:
                etree.SubElement(etree.SubElement(elem, "p"), "strong").text = "Returns"
                table = etree.SubElement(elem, "table")
                thead_tr = etree.SubElement(etree.SubElement(table, "thead"), "tr")
                for column in ("Type", "Description"):
                    etree.SubElement(thead_tr, "th").text = column
                tbody_tr = etree.SubElement(etree.SubElement(table, "tbody"), "tr")
                etree.SubElement(tbody_tr, "td").text = f"<code>{section.value.annotation_string}</code>"
                etree.SubElement(tbody_tr, "td").text = section.value.description
            elif section.type == Section.Type.ADMONITION:
                admonition = etree.SubElement(elem, "details")
                admonition.set("open", "")
                etree.SubElement(admonition, "summary").text = section.value[0][1]
                admonition.set("class", section.value[0][1])
                content = textwrap.dedent("\n".join(section.value[1:]))
                converted = md.convert(content)
                etree.SubElement(admonition, "p").text = converted

    @staticmethod
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
