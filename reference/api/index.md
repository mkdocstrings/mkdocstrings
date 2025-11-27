# mkdocstrings

mkdocstrings package.

Automatic documentation from sources, for MkDocs.

Classes:

- **`AutoDocProcessor`** – Our "autodoc" Markdown block processor.
- **`BaseHandler`** – The base handler class.
- **`CollectionError`** – An exception raised when some collection of data failed.
- **`Handlers`** – A collection of handlers.
- **`HeadingShiftingTreeprocessor`** – Shift levels of all Markdown headings according to the configured base level.
- **`Highlighter`** – Code highlighter that tries to match the Markdown configuration.
- **`IdPrependingTreeprocessor`** – Prepend the configured prefix to IDs of all HTML elements.
- **`Inventory`** – Inventory of collected and rendered objects.
- **`InventoryItem`** – Inventory item.
- **`LoggerAdapter`** – A logger adapter to prefix messages.
- **`MkdocstringsExtension`** – Our Markdown extension.
- **`MkdocstringsInnerExtension`** – Extension that should always be added to Markdown sub-documents that handlers request (and only them).
- **`MkdocstringsPlugin`** – An mkdocs plugin.
- **`ParagraphStrippingTreeprocessor`** – Unwraps the <p> element around the whole output.
- **`PluginConfig`** – The configuration options of mkdocstrings, written in mkdocs.yml.
- **`TemplateLogger`** – A wrapper class to allow logging in templates.
- **`ThemeNotSupported`** – An exception raised to tell a theme is not supported.

Functions:

- **`do_any`** – Check if at least one of the item in the sequence evaluates to true.
- **`get_logger`** – Return a pre-configured logger.
- **`get_template_logger`** – Return a logger usable in templates.
- **`get_template_logger_function`** – Create a wrapper function that automatically receives the Jinja template context.
- **`get_template_path`** – Return the path to the template currently using the given context.
- **`makeExtension`** – Create the extension instance.

Attributes:

- **`CollectorItem`** – The type of the item returned by the collect method of a handler.
- **`HandlerConfig`** – The type of the configuration of a handler.
- **`HandlerOptions`** – The type of the options passed to a handler.
- **`TEMPLATES_DIRS`** (`Sequence[Path]`) – The directories where the handler templates are located.

## CollectorItem

```python
CollectorItem = Any
```

The type of the item returned by the `collect` method of a handler.

## HandlerConfig

```python
HandlerConfig = Any
```

The type of the configuration of a handler.

## HandlerOptions

```python
HandlerOptions = Any
```

The type of the options passed to a handler.

## TEMPLATES_DIRS

```python
TEMPLATES_DIRS: Sequence[Path] = tuple(__path__)
```

The directories where the handler templates are located.

## AutoDocProcessor

```python
AutoDocProcessor(
    md: Markdown,
    *,
    handlers: Handlers,
    autorefs: AutorefsPlugin,
)
```

Bases: `BlockProcessor`

Our "autodoc" Markdown block processor.

It has a test method that tells if a block matches a criterion, and a run method that processes it.

It also has utility methods allowing to get handlers and their configuration easily, useful when processing a matched block.

Parameters:

- ### **`md`**

  (`Markdown`) – A markdown.Markdown instance.

- ### **`handlers`**

  (`Handlers`) – The handlers container.

- ### **`autorefs`**

  (`AutorefsPlugin`) – The autorefs plugin instance.

Methods:

- **`run`** – Run code on the matched blocks.
- **`test`** – Match our autodoc instructions.

Attributes:

- **`md`** – The Markdown instance.
- **`regex`** – The regular expression to match our autodoc instructions.

Source code in `src/mkdocstrings/_internal/extension.py`

```python
def __init__(
    self,
    md: Markdown,
    *,
    handlers: Handlers,
    autorefs: AutorefsPlugin,
) -> None:
    """Initialize the object.

    Arguments:
        md: A `markdown.Markdown` instance.
        handlers: The handlers container.
        autorefs: The autorefs plugin instance.
    """
    super().__init__(parser=md.parser)
    self.md = md
    """The Markdown instance."""
    self._handlers = handlers
    self._autorefs = autorefs
    self._updated_envs: set = set()
```

### md

```python
md = md
```

The Markdown instance.

### regex

```python
regex = compile(
    "^(?P<heading>#{1,6} *|)::: ?(?P<name>.+?) *$",
    flags=MULTILINE,
)
```

The regular expression to match our autodoc instructions.

### run

```python
run(parent: Element, blocks: MutableSequence[str]) -> None
```

Run code on the matched blocks.

The identifier and configuration lines are retrieved from a matched block and used to collect and render an object.

Parameters:

- #### **`parent`**

  (`Element`) – The parent element in the XML tree.

- #### **`blocks`**

  (`MutableSequence[str]`) – The rest of the blocks to be processed.

Source code in `src/mkdocstrings/_internal/extension.py`

```python
def run(self, parent: Element, blocks: MutableSequence[str]) -> None:
    """Run code on the matched blocks.

    The identifier and configuration lines are retrieved from a matched block
    and used to collect and render an object.

    Arguments:
        parent: The parent element in the XML tree.
        blocks: The rest of the blocks to be processed.
    """
    block = blocks.pop(0)
    match = self.regex.search(block)

    if match:
        if match.start() > 0:
            self.parser.parseBlocks(parent, [block[: match.start()]])
        # removes the first line
        block = block[match.end() :]

    block, the_rest = self.detab(block)

    if not block and blocks and blocks[0].startswith(("    handler:", "    options:")):
        # YAML options were separated from the `:::` line by a blank line.
        block = blocks.pop(0)

    if match:
        identifier = match["name"]
        heading_level = match["heading"].count("#")
        _logger.debug("Matched '::: %s'", identifier)

        html, handler, _ = self._process_block(identifier, block, heading_level)
        el = Element("div", {"class": "mkdocstrings"})
        # The final HTML is inserted as opaque to subsequent processing, and only revealed at the end.
        el.text = self.md.htmlStash.store(html)

        if handler.outer_layer:
            self._process_headings(handler, el)

        parent.append(el)

    if the_rest:
        # This block contained unindented line(s) after the first indented
        # line. Insert these lines as the first block of the master blocks
        # list for future processing.
        blocks.insert(0, the_rest)
```

### test

```python
test(parent: Element, block: str) -> bool
```

Match our autodoc instructions.

Parameters:

- #### **`parent`**

  (`Element`) – The parent element in the XML tree.

- #### **`block`**

  (`str`) – The block to be tested.

Returns:

- `bool` – Whether this block should be processed or not.

Source code in `src/mkdocstrings/_internal/extension.py`

```python
def test(self, parent: Element, block: str) -> bool:  # noqa: ARG002
    """Match our autodoc instructions.

    Arguments:
        parent: The parent element in the XML tree.
        block: The block to be tested.

    Returns:
        Whether this block should be processed or not.
    """
    return bool(self.regex.search(block))
```

## BaseHandler

```python
BaseHandler(
    *,
    theme: str,
    custom_templates: str | None,
    mdx: Sequence[str | Extension],
    mdx_config: Mapping[str, Any],
)
```

The base handler class.

Inherit from this class to implement a handler.

You will have to implement the `collect` and `render` methods. You can also implement the `teardown` method, and override the `update_env` method, to add more filters to the Jinja environment, making them available in your Jinja templates.

To define a fallback theme, add a `fallback_theme` class-variable. To add custom CSS, add an `extra_css` variable or create an 'style.css' file beside the templates.

If the given theme is not supported (it does not exist), it will look for a `fallback_theme` attribute in `self` to use as a fallback theme.

Other Parameters:

- **`theme`** (`str`) – The theme to use.
- **`custom_templates`** (`str | None`) – The path to custom templates.
- **`mdx`** (`list[str | Extension]`) – A list of Markdown extensions to use.
- **`mdx_config`** (`Mapping[str, Mapping[str, Any]]`) – Configuration for the Markdown extensions.

Methods:

- **`collect`** – Collect data given an identifier and user configuration.
- **`do_convert_markdown`** – Render Markdown text; for use inside templates.
- **`do_heading`** – Render an HTML heading and register it for the table of contents. For use inside templates.
- **`get_aliases`** – Return the possible aliases for a given identifier.
- **`get_extended_templates_dirs`** – Load template extensions for the given handler, return their templates directories.
- **`get_headings`** – Return and clear the headings gathered so far.
- **`get_inventory_urls`** – Return the URLs (and configuration options) of the inventory files to download.
- **`get_options`** – Get combined options.
- **`get_templates_dir`** – Return the path to the handler's templates directory.
- **`load_inventory`** – Yield items and their URLs from an inventory file streamed from in_file.
- **`render`** – Render a template using provided data and configuration options.
- **`render_backlinks`** – Render backlinks.
- **`teardown`** – Teardown the handler.
- **`update_env`** – Update the Jinja environment.

Attributes:

- **`custom_templates`** – The path to custom templates.
- **`domain`** (`str`) – The handler's domain, used to register objects in the inventory, for example "py".
- **`enable_inventory`** (`bool`) – Whether the inventory creation is enabled.
- **`env`** – The Jinja environment.
- **`extra_css`** (`str`) – Extra CSS.
- **`fallback_theme`** (`str`) – Fallback theme to use when a template isn't found in the configured theme.
- **`md`** (`Markdown`) – The Markdown instance.
- **`mdx`** – The Markdown extensions to use.
- **`mdx_config`** – The configuration for the Markdown extensions.
- **`name`** (`str`) – The handler's name, for example "python".
- **`outer_layer`** (`bool`) – Whether we're in the outer Markdown conversion layer.
- **`theme`** – The selected theme.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def __init__(
    self,
    *,
    theme: str,
    custom_templates: str | None,
    mdx: Sequence[str | Extension],
    mdx_config: Mapping[str, Any],
) -> None:
    """Initialize the object.

    If the given theme is not supported (it does not exist), it will look for a `fallback_theme` attribute
    in `self` to use as a fallback theme.

    Keyword Arguments:
        theme (str): The theme to use.
        custom_templates (str | None): The path to custom templates.
        mdx (list[str | Extension]): A list of Markdown extensions to use.
        mdx_config (Mapping[str, Mapping[str, Any]]): Configuration for the Markdown extensions.
    """
    self.theme = theme
    """The selected theme."""
    self.custom_templates = custom_templates
    """The path to custom templates."""
    self.mdx = mdx
    """The Markdown extensions to use."""
    self.mdx_config = mdx_config
    """The configuration for the Markdown extensions."""
    self._md: Markdown | None = None
    self._headings: list[Element] = []

    paths = []

    # add selected theme templates
    themes_dir = self.get_templates_dir(self.name)
    paths.append(themes_dir / self.theme)

    # add extended theme templates
    extended_templates_dirs = self.get_extended_templates_dirs(self.name)
    for templates_dir in extended_templates_dirs:
        paths.append(templates_dir / self.theme)

    # add fallback theme templates
    if self.fallback_theme and self.fallback_theme != self.theme:
        paths.append(themes_dir / self.fallback_theme)

        # add fallback theme of extended templates
        for templates_dir in extended_templates_dirs:
            paths.append(templates_dir / self.fallback_theme)

    for path in paths:
        css_path = path / "style.css"
        if css_path.is_file():
            self.extra_css += "\n" + css_path.read_text(encoding="utf-8")
            break

    if self.custom_templates is not None:
        paths.insert(0, Path(self.custom_templates) / self.name / self.theme)

    self.env = Environment(
        autoescape=True,
        loader=FileSystemLoader(paths),
        auto_reload=False,  # Editing a template in the middle of a build is not useful.
    )
    """The Jinja environment."""

    self.env.filters["convert_markdown"] = self.do_convert_markdown
    self.env.filters["heading"] = self.do_heading
    self.env.filters["any"] = do_any
    self.env.globals["log"] = get_template_logger(self.name)
```

### custom_templates

```python
custom_templates = custom_templates
```

The path to custom templates.

### domain

```python
domain: str
```

The handler's domain, used to register objects in the inventory, for example "py".

### enable_inventory

```python
enable_inventory: bool = False
```

Whether the inventory creation is enabled.

### env

```python
env = Environment(
    autoescape=True,
    loader=FileSystemLoader(paths),
    auto_reload=False,
)
```

The Jinja environment.

### extra_css

```python
extra_css: str = ''
```

Extra CSS.

### fallback_theme

```python
fallback_theme: str = ''
```

Fallback theme to use when a template isn't found in the configured theme.

### md

```python
md: Markdown
```

The Markdown instance.

Raises:

- `RuntimeError` – When the Markdown instance is not set yet.

### mdx

```python
mdx = mdx
```

The Markdown extensions to use.

### mdx_config

```python
mdx_config = mdx_config
```

The configuration for the Markdown extensions.

### name

```python
name: str
```

The handler's name, for example "python".

### outer_layer

```python
outer_layer: bool
```

Whether we're in the outer Markdown conversion layer.

### theme

```python
theme = theme
```

The selected theme.

### collect

```python
collect(
    identifier: str, options: HandlerOptions
) -> CollectorItem
```

Collect data given an identifier and user configuration.

In the implementation, you typically call a subprocess that returns JSON, and load that JSON again into a Python dictionary for example, though the implementation is completely free.

Parameters:

- #### **`identifier`**

  (`str`) – An identifier for which to collect data. For example, in Python, it would be 'mkdocstrings.handlers' to collect documentation about the handlers module. It can be anything that you can feed to the tool of your choice.

- #### **`options`**

  (`HandlerOptions`) – The final configuration options.

Returns:

- `CollectorItem` – Anything you want, as long as you can feed it to the handler's render method.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def collect(self, identifier: str, options: HandlerOptions) -> CollectorItem:
    """Collect data given an identifier and user configuration.

    In the implementation, you typically call a subprocess that returns JSON, and load that JSON again into
    a Python dictionary for example, though the implementation is completely free.

    Arguments:
        identifier: An identifier for which to collect data. For example, in Python,
            it would be 'mkdocstrings.handlers' to collect documentation about the handlers module.
            It can be anything that you can feed to the tool of your choice.
        options: The final configuration options.

    Returns:
        Anything you want, as long as you can feed it to the handler's `render` method.
    """
    raise NotImplementedError
```

### do_convert_markdown

```python
do_convert_markdown(
    text: str,
    heading_level: int,
    html_id: str = "",
    *,
    strip_paragraph: bool = False,
    autoref_hook: AutorefsHookInterface | None = None,
) -> Markup
```

Render Markdown text; for use inside templates.

Parameters:

- #### **`text`**

  (`str`) – The text to convert.

- #### **`heading_level`**

  (`int`) – The base heading level to start all Markdown headings from.

- #### **`html_id`**

  (`str`, default: `''` ) – The HTML id of the element that's considered the parent of this element.

- #### **`strip_paragraph`**

  (`bool`, default: `False` ) – Whether to exclude the <p> tag from around the whole output.

Returns:

- `Markup` – An HTML string.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def do_convert_markdown(
    self,
    text: str,
    heading_level: int,
    html_id: str = "",
    *,
    strip_paragraph: bool = False,
    autoref_hook: AutorefsHookInterface | None = None,
) -> Markup:
    """Render Markdown text; for use inside templates.

    Arguments:
        text: The text to convert.
        heading_level: The base heading level to start all Markdown headings from.
        html_id: The HTML id of the element that's considered the parent of this element.
        strip_paragraph: Whether to exclude the `<p>` tag from around the whole output.

    Returns:
        An HTML string.
    """
    global _markdown_conversion_layer  # noqa: PLW0603
    _markdown_conversion_layer += 1
    treeprocessors = self.md.treeprocessors
    treeprocessors[HeadingShiftingTreeprocessor.name].shift_by = heading_level  # type: ignore[attr-defined]
    treeprocessors[IdPrependingTreeprocessor.name].id_prefix = html_id and html_id + "--"  # type: ignore[attr-defined]
    treeprocessors[ParagraphStrippingTreeprocessor.name].strip = strip_paragraph  # type: ignore[attr-defined]
    if BacklinksTreeProcessor.name in treeprocessors:
        treeprocessors[BacklinksTreeProcessor.name].initial_id = html_id  # type: ignore[attr-defined]
    if autoref_hook and AutorefsInlineProcessor.name in self.md.inlinePatterns:
        self.md.inlinePatterns[AutorefsInlineProcessor.name].hook = autoref_hook  # type: ignore[attr-defined]

    try:
        return Markup(self.md.convert(text))
    finally:
        treeprocessors[HeadingShiftingTreeprocessor.name].shift_by = 0  # type: ignore[attr-defined]
        treeprocessors[IdPrependingTreeprocessor.name].id_prefix = ""  # type: ignore[attr-defined]
        treeprocessors[ParagraphStrippingTreeprocessor.name].strip = False  # type: ignore[attr-defined]
        if BacklinksTreeProcessor.name in treeprocessors:
            treeprocessors[BacklinksTreeProcessor.name].initial_id = None  # type: ignore[attr-defined]
        if AutorefsInlineProcessor.name in self.md.inlinePatterns:
            self.md.inlinePatterns[AutorefsInlineProcessor.name].hook = None  # type: ignore[attr-defined]
        self.md.reset()
        _markdown_conversion_layer -= 1
```

### do_heading

```python
do_heading(
    content: Markup,
    heading_level: int,
    *,
    role: str | None = None,
    hidden: bool = False,
    toc_label: str | None = None,
    skip_inventory: bool = False,
    **attributes: str,
) -> Markup
```

Render an HTML heading and register it for the table of contents. For use inside templates.

Parameters:

- #### **`content`**

  (`Markup`) – The HTML within the heading.

- #### **`heading_level`**

  (`int`) – The level of heading (e.g. 3 -> h3).

- #### **`role`**

  (`str | None`, default: `None` ) – An optional role for the object bound to this heading.

- #### **`hidden`**

  (`bool`, default: `False` ) – If True, only register it for the table of contents, don't render anything.

- #### **`toc_label`**

  (`str | None`, default: `None` ) – The title to use in the table of contents ('data-toc-label' attribute).

- #### **`skip_inventory`**

  (`bool`, default: `False` ) – Flag element to not be registered in the inventory (by setting a data-skip-inventory attribute).

- #### **`**attributes`**

  (`str`, default: `{}` ) – Any extra HTML attributes of the heading.

Returns:

- `Markup` – An HTML string.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def do_heading(
    self,
    content: Markup,
    heading_level: int,
    *,
    role: str | None = None,
    hidden: bool = False,
    toc_label: str | None = None,
    skip_inventory: bool = False,
    **attributes: str,
) -> Markup:
    """Render an HTML heading and register it for the table of contents. For use inside templates.

    Arguments:
        content: The HTML within the heading.
        heading_level: The level of heading (e.g. 3 -> `h3`).
        role: An optional role for the object bound to this heading.
        hidden: If True, only register it for the table of contents, don't render anything.
        toc_label: The title to use in the table of contents ('data-toc-label' attribute).
        skip_inventory: Flag element to not be registered in the inventory (by setting a `data-skip-inventory` attribute).
        **attributes: Any extra HTML attributes of the heading.

    Returns:
        An HTML string.
    """
    # Produce a heading element that will be used later, in `AutoDocProcessor.run`, to:
    # - register it in the ToC: right now we're in the inner Markdown conversion layer,
    #   so we have to bubble up the information to the outer Markdown conversion layer,
    #   for the ToC extension to pick it up.
    # - register it in autorefs: right now we don't know what page is being rendered,
    #   so we bubble up the information again to where autorefs knows the page,
    #   and can correctly register the heading anchor (id) to its full URL.
    # - register it in the objects inventory: same as for autorefs,
    #   we don't know the page here, or the handler (and its domain),
    #   so we bubble up the information to where the mkdocstrings extension knows that.
    el = Element(f"h{heading_level}", attributes)
    if toc_label is None:
        toc_label = content.unescape() if isinstance(content, Markup) else content
    el.set("data-toc-label", toc_label)
    if skip_inventory:
        el.set("data-skip-inventory", "true")
    if role:
        el.set("data-role", role)
    if content:
        el.text = str(content).strip()
    self._headings.append(el)

    if hidden:
        return Markup('<a id="{0}"></a>').format(attributes["id"])

    # Now produce the actual HTML to be rendered. The goal is to wrap the HTML content into a heading.
    # Start with a heading that has just attributes (no text), and add a placeholder into it.
    el = Element(f"h{heading_level}", attributes)
    el.append(Element("mkdocstrings-placeholder"))
    # Tell the inner 'toc' extension to make its additions if configured so.
    toc = cast("TocTreeprocessor", self.md.treeprocessors["toc"])
    if toc.use_anchors:
        toc.add_anchor(el, attributes["id"])
    if toc.use_permalinks:
        toc.add_permalink(el, attributes["id"])

    # The content we received is HTML, so it can't just be inserted into the tree. We had marked the middle
    # of the heading with a placeholder that can never occur (text can't directly contain angle brackets).
    # Now this HTML wrapper can be "filled" by replacing the placeholder.
    html_with_placeholder = tostring(el, encoding="unicode")
    assert (  # noqa: S101
        html_with_placeholder.count("<mkdocstrings-placeholder />") == 1
    ), f"Bug in mkdocstrings: failed to replace in {html_with_placeholder!r}"
    html = html_with_placeholder.replace("<mkdocstrings-placeholder />", content)
    return Markup(html)
```

### get_aliases

```python
get_aliases(identifier: str) -> tuple[str, ...]
```

Return the possible aliases for a given identifier.

Parameters:

- #### **`identifier`**

  (`str`) – The identifier to get the aliases of.

Returns:

- `tuple[str, ...]` – A tuple of strings - aliases.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def get_aliases(self, identifier: str) -> tuple[str, ...]:  # noqa: ARG002
    """Return the possible aliases for a given identifier.

    Arguments:
        identifier: The identifier to get the aliases of.

    Returns:
        A tuple of strings - aliases.
    """
    return ()
```

### get_extended_templates_dirs

```python
get_extended_templates_dirs(handler: str) -> list[Path]
```

Load template extensions for the given handler, return their templates directories.

Parameters:

- #### **`handler`**

  (`str`) – The name of the handler to get the extended templates directory of.

Returns:

- `list[Path]` – The extensions templates directories.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def get_extended_templates_dirs(self, handler: str) -> list[Path]:
    """Load template extensions for the given handler, return their templates directories.

    Arguments:
        handler: The name of the handler to get the extended templates directory of.

    Returns:
        The extensions templates directories.
    """
    discovered_extensions = entry_points(group=f"mkdocstrings.{handler}.templates")
    return [extension.load()() for extension in discovered_extensions]
```

### get_headings

```python
get_headings() -> Sequence[Element]
```

Return and clear the headings gathered so far.

Returns:

- `Sequence[Element]` – A list of HTML elements.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def get_headings(self) -> Sequence[Element]:
    """Return and clear the headings gathered so far.

    Returns:
        A list of HTML elements.
    """
    result = list(self._headings)
    self._headings.clear()
    return result
```

### get_inventory_urls

```python
get_inventory_urls() -> list[tuple[str, dict[str, Any]]]
```

Return the URLs (and configuration options) of the inventory files to download.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def get_inventory_urls(self) -> list[tuple[str, dict[str, Any]]]:
    """Return the URLs (and configuration options) of the inventory files to download."""
    return []
```

### get_options

```python
get_options(
    local_options: Mapping[str, Any],
) -> HandlerOptions
```

Get combined options.

Override this method to customize how options are combined, for example by merging the global options with the local options. By combining options here, you don't have to do it twice in `collect` and `render`.

Parameters:

- #### **`local_options`**

  (`Mapping[str, Any]`) – The local options.

Returns:

- `HandlerOptions` – The combined options.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def get_options(self, local_options: Mapping[str, Any]) -> HandlerOptions:
    """Get combined options.

    Override this method to customize how options are combined,
    for example by merging the global options with the local options.
    By combining options here, you don't have to do it twice in `collect` and `render`.

    Arguments:
        local_options: The local options.

    Returns:
        The combined options.
    """
    return local_options
```

### get_templates_dir

```python
get_templates_dir(handler: str | None = None) -> Path
```

Return the path to the handler's templates directory.

Override to customize how the templates directory is found.

Parameters:

- #### **`handler`**

  (`str | None`, default: `None` ) – The name of the handler to get the templates directory of.

Raises:

- `ModuleNotFoundError` – When no such handler is installed.
- `FileNotFoundError` – When the templates directory cannot be found.

Returns:

- `Path` – The templates directory path.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def get_templates_dir(self, handler: str | None = None) -> Path:
    """Return the path to the handler's templates directory.

    Override to customize how the templates directory is found.

    Arguments:
        handler: The name of the handler to get the templates directory of.

    Raises:
        ModuleNotFoundError: When no such handler is installed.
        FileNotFoundError: When the templates directory cannot be found.

    Returns:
        The templates directory path.
    """
    handler = handler or self.name
    try:
        import mkdocstrings_handlers  # noqa: PLC0415
    except ModuleNotFoundError as error:
        raise ModuleNotFoundError(f"Handler '{handler}' not found, is it installed?") from error

    for path in mkdocstrings_handlers.__path__:
        theme_path = Path(path, handler, "templates")
        if theme_path.exists():
            return theme_path

    raise FileNotFoundError(f"Can't find 'templates' folder for handler '{handler}'")
```

### load_inventory

```python
load_inventory(
    in_file: BinaryIO,
    url: str,
    base_url: str | None = None,
    **kwargs: Any,
) -> Iterator[tuple[str, str]]
```

Yield items and their URLs from an inventory file streamed from `in_file`.

Parameters:

- #### **`in_file`**

  (`BinaryIO`) – The binary file-like object to read the inventory from.

- #### **`url`**

  (`str`) – The URL that this file is being streamed from (used to guess base_url).

- #### **`base_url`**

  (`str | None`, default: `None` ) – The URL that this inventory's sub-paths are relative to.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Ignore additional arguments passed from the config.

Yields:

- `tuple[str, str]` – Tuples of (item identifier, item URL).

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
@classmethod
def load_inventory(
    cls,
    in_file: BinaryIO,  # noqa: ARG003
    url: str,  # noqa: ARG003
    base_url: str | None = None,  # noqa: ARG003
    **kwargs: Any,  # noqa: ARG003
) -> Iterator[tuple[str, str]]:
    """Yield items and their URLs from an inventory file streamed from `in_file`.

    Arguments:
        in_file: The binary file-like object to read the inventory from.
        url: The URL that this file is being streamed from (used to guess `base_url`).
        base_url: The URL that this inventory's sub-paths are relative to.
        **kwargs: Ignore additional arguments passed from the config.

    Yields:
        Tuples of (item identifier, item URL).
    """
    yield from ()
```

### render

```python
render(
    data: CollectorItem,
    options: HandlerOptions,
    *,
    locale: str | None = None,
) -> str
```

Render a template using provided data and configuration options.

Parameters:

- #### **`data`**

  (`CollectorItem`) – The collected data to render.

- #### **`options`**

  (`HandlerOptions`) – The final configuration options.

- #### **`locale`**

  (`str | None`, default: `None` ) – The locale to use for translations, if any.

Returns:

- `str` – The rendered template as HTML.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def render(self, data: CollectorItem, options: HandlerOptions, *, locale: str | None = None) -> str:
    """Render a template using provided data and configuration options.

    Arguments:
        data: The collected data to render.
        options: The final configuration options.
        locale: The locale to use for translations, if any.

    Returns:
        The rendered template as HTML.
    """
    raise NotImplementedError
```

### render_backlinks

```python
render_backlinks(
    backlinks: Mapping[str, Iterable[Backlink]],
    *,
    locale: str | None = None,
) -> str
```

Render backlinks.

Parameters:

- #### **`backlinks`**

  (`Mapping[str, Iterable[Backlink]]`) – A mapping of identifiers to backlinks.

- #### **`locale`**

  (`str | None`, default: `None` ) – The locale to use for translations, if any.

Returns:

- `str` – The rendered backlinks as HTML.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def render_backlinks(self, backlinks: Mapping[str, Iterable[Backlink]], *, locale: str | None = None) -> str:  # noqa: ARG002
    """Render backlinks.

    Parameters:
        backlinks: A mapping of identifiers to backlinks.
        locale: The locale to use for translations, if any.

    Returns:
        The rendered backlinks as HTML.
    """
    return ""
```

### teardown

```python
teardown() -> None
```

Teardown the handler.

This method should be implemented to, for example, terminate a subprocess that was started when creating the handler instance.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def teardown(self) -> None:
    """Teardown the handler.

    This method should be implemented to, for example, terminate a subprocess
    that was started when creating the handler instance.
    """
```

### update_env

```python
update_env(config: Any) -> None
```

Update the Jinja environment.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def update_env(self, config: Any) -> None:
    """Update the Jinja environment."""
```

## CollectionError

Bases: `Exception`

An exception raised when some collection of data failed.

## Handlers

```python
Handlers(
    *,
    theme: str,
    default: str,
    inventory_project: str,
    inventory_version: str = "0.0.0",
    handlers_config: dict[str, HandlerConfig] | None = None,
    custom_templates: str | None = None,
    mdx: Sequence[str | Extension] | None = None,
    mdx_config: Mapping[str, Any] | None = None,
    locale: str = "en",
    tool_config: Any,
)
```

A collection of handlers.

Do not instantiate this directly. The plugin will keep one instance of this for the purpose of caching. Use mkdocstrings.MkdocstringsPlugin.get_handler for convenient access.

Parameters:

- ### **`theme`**

  (`str`) – The theme to use.

- ### **`default`**

  (`str`) – The default handler to use.

- ### **`inventory_project`**

  (`str`) – The project name to use in the inventory.

- ### **`inventory_version`**

  (`str`, default: `'0.0.0'` ) – The project version to use in the inventory.

- ### **`handlers_config`**

  (`dict[str, HandlerConfig] | None`, default: `None` ) – The handlers configuration.

- ### **`custom_templates`**

  (`str | None`, default: `None` ) – The path to custom templates.

- ### **`mdx`**

  (`Sequence[str | Extension] | None`, default: `None` ) – A list of Markdown extensions to use.

- ### **`mdx_config`**

  (`Mapping[str, Any] | None`, default: `None` ) – Configuration for the Markdown extensions.

- ### **`locale`**

  (`str`, default: `'en'` ) – The locale to use for translations.

- ### **`tool_config`**

  (`Any`) – Tool configuration to pass down to handlers.

Methods:

- **`get_handler`** – Get a handler thanks to its name.
- **`get_handler_config`** – Return the global configuration of the given handler.
- **`get_handler_name`** – Return the handler name defined in an "autodoc" instruction YAML configuration, or the global default handler.
- **`teardown`** – Teardown all cached handlers and clear the cache.

Attributes:

- **`inventory`** (`Inventory`) – The objects inventory.
- **`seen_handlers`** (`Iterable[BaseHandler]`) – Get the handlers that were encountered so far throughout the build.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def __init__(
    self,
    *,
    theme: str,
    default: str,
    inventory_project: str,
    inventory_version: str = "0.0.0",
    handlers_config: dict[str, HandlerConfig] | None = None,
    custom_templates: str | None = None,
    mdx: Sequence[str | Extension] | None = None,
    mdx_config: Mapping[str, Any] | None = None,
    locale: str = "en",
    tool_config: Any,
) -> None:
    """Initialize the object.

    Arguments:
        theme: The theme to use.
        default: The default handler to use.
        inventory_project: The project name to use in the inventory.
        inventory_version: The project version to use in the inventory.
        handlers_config: The handlers configuration.
        custom_templates: The path to custom templates.
        mdx: A list of Markdown extensions to use.
        mdx_config: Configuration for the Markdown extensions.
        locale: The locale to use for translations.
        tool_config: Tool configuration to pass down to handlers.
    """
    self._theme = theme
    self._default = default
    self._handlers_config = handlers_config or {}
    self._custom_templates = custom_templates
    self._mdx = mdx or []
    self._mdx_config = mdx_config or {}
    self._handlers: dict[str, BaseHandler] = {}
    self._locale = locale
    self._tool_config = tool_config

    self.inventory: Inventory = Inventory(project=inventory_project, version=inventory_version)
    """The objects inventory."""

    self._inv_futures: dict[futures.Future, tuple[BaseHandler, str, Any]] = {}
```

### inventory

```python
inventory: Inventory = Inventory(
    project=inventory_project, version=inventory_version
)
```

The objects inventory.

### seen_handlers

```python
seen_handlers: Iterable[BaseHandler]
```

Get the handlers that were encountered so far throughout the build.

Returns:

- `Iterable[BaseHandler]` – An iterable of instances of BaseHandler
- `Iterable[BaseHandler]` – (usable only to loop through it).

### get_handler

```python
get_handler(
    name: str, handler_config: dict | None = None
) -> BaseHandler
```

Get a handler thanks to its name.

This function dynamically imports a module named "mkdocstrings.handlers.NAME", calls its `get_handler` method to get an instance of a handler, and caches it in dictionary. It means that during one run (for each reload when serving, or once when building), a handler is instantiated only once, and reused for each "autodoc" instruction asking for it.

Parameters:

- #### **`name`**

  (`str`) – The name of the handler. Really, it's the name of the Python module holding it.

- #### **`handler_config`**

  (`dict | None`, default: `None` ) – Configuration passed to the handler.

Returns:

- `BaseHandler` – An instance of a subclass of BaseHandler, as instantiated by the get_handler method of the handler's module.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def get_handler(self, name: str, handler_config: dict | None = None) -> BaseHandler:
    """Get a handler thanks to its name.

    This function dynamically imports a module named "mkdocstrings.handlers.NAME", calls its
    `get_handler` method to get an instance of a handler, and caches it in dictionary.
    It means that during one run (for each reload when serving, or once when building),
    a handler is instantiated only once, and reused for each "autodoc" instruction asking for it.

    Arguments:
        name: The name of the handler. Really, it's the name of the Python module holding it.
        handler_config: Configuration passed to the handler.

    Returns:
        An instance of a subclass of [`BaseHandler`][mkdocstrings.BaseHandler],
            as instantiated by the `get_handler` method of the handler's module.
    """
    if name not in self._handlers:
        if handler_config is None:
            handler_config = self._handlers_config.get(name, {})
        module = importlib.import_module(f"mkdocstrings_handlers.{name}")

        self._handlers[name] = module.get_handler(
            theme=self._theme,
            custom_templates=self._custom_templates,
            mdx=self._mdx,
            mdx_config=self._mdx_config,
            handler_config=handler_config,
            tool_config=self._tool_config,
        )
    return self._handlers[name]
```

### get_handler_config

```python
get_handler_config(name: str) -> dict
```

Return the global configuration of the given handler.

Parameters:

- #### **`name`**

  (`str`) – The name of the handler to get the global configuration of.

Returns:

- `dict` – The global configuration of the given handler. It can be an empty dictionary.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def get_handler_config(self, name: str) -> dict:
    """Return the global configuration of the given handler.

    Arguments:
        name: The name of the handler to get the global configuration of.

    Returns:
        The global configuration of the given handler. It can be an empty dictionary.
    """
    return self._handlers_config.get(name, None) or {}
```

### get_handler_name

```python
get_handler_name(config: dict) -> str
```

Return the handler name defined in an "autodoc" instruction YAML configuration, or the global default handler.

Parameters:

- #### **`config`**

  (`dict`) – A configuration dictionary, obtained from YAML below the "autodoc" instruction.

Returns:

- `str` – The name of the handler to use.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def get_handler_name(self, config: dict) -> str:
    """Return the handler name defined in an "autodoc" instruction YAML configuration, or the global default handler.

    Arguments:
        config: A configuration dictionary, obtained from YAML below the "autodoc" instruction.

    Returns:
        The name of the handler to use.
    """
    return config.get("handler", self._default)
```

### teardown

```python
teardown() -> None
```

Teardown all cached handlers and clear the cache.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def teardown(self) -> None:
    """Teardown all cached handlers and clear the cache."""
    for future in self._inv_futures:
        future.cancel()
    for handler in self.seen_handlers:
        handler.teardown()
    self._handlers.clear()
```

## HeadingShiftingTreeprocessor

```python
HeadingShiftingTreeprocessor(md: Markdown, shift_by: int)
```

Bases: `Treeprocessor`

Shift levels of all Markdown headings according to the configured base level.

Parameters:

- ### **`md`**

  (`Markdown`) – A markdown.Markdown instance.

- ### **`shift_by`**

  (`int`) – The number of heading "levels" to add to every heading.

Methods:

- **`run`** – Shift the levels of all headings in the document.

Attributes:

- **`name`** (`str`) – The name of the treeprocessor.
- **`regex`** (`Pattern`) – The regex to match heading tags.
- **`shift_by`** (`int`) – The number of heading "levels" to add to every heading. <h2> with shift_by = 3 becomes <h5>.

Source code in `src/mkdocstrings/_internal/handlers/rendering.py`

```python
def __init__(self, md: Markdown, shift_by: int):
    """Initialize the object.

    Arguments:
        md: A `markdown.Markdown` instance.
        shift_by: The number of heading "levels" to add to every heading.
    """
    super().__init__(md)
    self.shift_by = shift_by
```

### name

```python
name: str = 'mkdocstrings_headings'
```

The name of the treeprocessor.

### regex

```python
regex: Pattern = compile('([Hh])([1-6])')
```

The regex to match heading tags.

### shift_by

```python
shift_by: int = shift_by
```

The number of heading "levels" to add to every heading. `<h2>` with `shift_by = 3` becomes `<h5>`.

### run

```python
run(root: Element) -> None
```

Shift the levels of all headings in the document.

Source code in `src/mkdocstrings/_internal/handlers/rendering.py`

```python
def run(self, root: Element) -> None:
    """Shift the levels of all headings in the document."""
    if not self.shift_by:
        return
    for el in root.iter():
        match = self.regex.fullmatch(el.tag)
        if match:
            level = int(match[2]) + self.shift_by
            level = max(1, min(level, 6))
            el.tag = f"{match[1]}{level}"
```

## Highlighter

```python
Highlighter(md: Markdown)
```

Bases: `Highlight`

Code highlighter that tries to match the Markdown configuration.

Picking up the global config and defaults works only if you use the `codehilite` or `pymdownx.highlight` (recommended) Markdown extension.

- If you use `pymdownx.highlight`, highlighting settings are picked up from it, and the default CSS class is `.highlight`. This also means the default of `guess_lang: false`.
- Otherwise, if you use the `codehilite` extension, settings are picked up from it, and the default CSS class is `.codehilite`. Also consider setting `guess_lang: false`.
- If neither are added to `markdown_extensions`, highlighting is enabled anyway. This is for backwards compatibility. If you really want to disable highlighting even in *mkdocstrings*, add one of these extensions anyway and set `use_pygments: false`.

The underlying implementation is `pymdownx.highlight` regardless.

Parameters:

- ### **`md`**

  (`Markdown`) – The Markdown instance to read configs from.

Methods:

- **`highlight`** – Highlight a code-snippet.

Source code in `src/mkdocstrings/_internal/handlers/rendering.py`

```python
def __init__(self, md: Markdown):
    """Configure to match a `markdown.Markdown` instance.

    Arguments:
        md: The Markdown instance to read configs from.
    """
    config: dict[str, Any] = {}
    self._highlighter: str | None = None
    for ext in md.registeredExtensions:
        if isinstance(ext, HighlightExtension) and (ext.enabled or not config):
            self._highlighter = "highlight"
            config = ext.getConfigs()
            break  # This one takes priority, no need to continue looking
        if isinstance(ext, CodeHiliteExtension) and not config:
            self._highlighter = "codehilite"
            config = ext.getConfigs()
            config["language_prefix"] = config["lang_prefix"]
    self._css_class = config.pop("css_class", "highlight")
    super().__init__(**{name: opt for name, opt in config.items() if name in self._highlight_config_keys})
```

### highlight

```python
highlight(
    src: str,
    language: str | None = None,
    *,
    inline: bool = False,
    dedent: bool = True,
    linenums: bool | None = None,
    **kwargs: Any,
) -> str
```

Highlight a code-snippet.

Parameters:

- #### **`src`**

  (`str`) – The code to highlight.

- #### **`language`**

  (`str | None`, default: `None` ) – Explicitly tell what language to use for highlighting.

- #### **`inline`**

  (`bool`, default: `False` ) – Whether to highlight as inline.

- #### **`dedent`**

  (`bool`, default: `True` ) – Whether to dedent the code before highlighting it or not.

- #### **`linenums`**

  (`bool | None`, default: `None` ) – Whether to add line numbers in the result.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Pass on to pymdownx.highlight.Highlight.highlight.

Returns:

- `str` – The highlighted code as HTML text, marked safe (not escaped for HTML).

Source code in `src/mkdocstrings/_internal/handlers/rendering.py`

```python
def highlight(
    self,
    src: str,
    language: str | None = None,
    *,
    inline: bool = False,
    dedent: bool = True,
    linenums: bool | None = None,
    **kwargs: Any,
) -> str:
    """Highlight a code-snippet.

    Arguments:
        src: The code to highlight.
        language: Explicitly tell what language to use for highlighting.
        inline: Whether to highlight as inline.
        dedent: Whether to dedent the code before highlighting it or not.
        linenums: Whether to add line numbers in the result.
        **kwargs: Pass on to `pymdownx.highlight.Highlight.highlight`.

    Returns:
        The highlighted code as HTML text, marked safe (not escaped for HTML).
    """
    if isinstance(src, Markup):
        src = src.unescape()
    if dedent:
        src = textwrap.dedent(src)

    kwargs.setdefault("css_class", self._css_class)
    old_linenums = self.linenums  # type: ignore[has-type]
    if linenums is not None:
        self.linenums = linenums
    try:
        result = super().highlight(src, language, inline=inline, **kwargs)
    finally:
        self.linenums = old_linenums

    if inline:
        # From the maintainer of codehilite, the codehilite CSS class, as defined by the user,
        # should never be added to inline code, because codehilite does not support inline code.
        # See https://github.com/Python-Markdown/markdown/issues/1220#issuecomment-1692160297.
        css_class = "" if self._highlighter == "codehilite" else kwargs["css_class"]
        return Markup(f'<code class="{css_class} language-{language}">{result.text}</code>')
    return Markup(result)
```

## IdPrependingTreeprocessor

```python
IdPrependingTreeprocessor(md: Markdown, id_prefix: str)
```

Bases: `Treeprocessor`

Prepend the configured prefix to IDs of all HTML elements.

Parameters:

- ### **`md`**

  (`Markdown`) – A markdown.Markdown instance.

- ### **`id_prefix`**

  (`str`) – The prefix to add to every ID. It is prepended without any separator.

Methods:

- **`run`** – Prepend the configured prefix to all IDs in the document.

Attributes:

- **`id_prefix`** (`str`) – The prefix to add to every ID. It is prepended without any separator; specify your own separator if needed.
- **`name`** (`str`) – The name of the treeprocessor.

Source code in `src/mkdocstrings/_internal/handlers/rendering.py`

```python
def __init__(self, md: Markdown, id_prefix: str):
    """Initialize the object.

    Arguments:
        md: A `markdown.Markdown` instance.
        id_prefix: The prefix to add to every ID. It is prepended without any separator.
    """
    super().__init__(md)
    self.id_prefix = id_prefix
```

### id_prefix

```python
id_prefix: str = id_prefix
```

The prefix to add to every ID. It is prepended without any separator; specify your own separator if needed.

### name

```python
name: str = 'mkdocstrings_ids'
```

The name of the treeprocessor.

### run

```python
run(root: Element) -> None
```

Prepend the configured prefix to all IDs in the document.

Source code in `src/mkdocstrings/_internal/handlers/rendering.py`

```python
def run(self, root: Element) -> None:
    """Prepend the configured prefix to all IDs in the document."""
    if self.id_prefix:
        self._prefix_ids(root)
```

## Inventory

```python
Inventory(
    items: list[InventoryItem] | None = None,
    project: str = "project",
    version: str = "0.0.0",
)
```

Bases: `dict`

Inventory of collected and rendered objects.

Parameters:

- ### **`items`**

  (`list[InventoryItem] | None`, default: `None` ) – A list of items.

- ### **`project`**

  (`str`, default: `'project'` ) – The project name.

- ### **`version`**

  (`str`, default: `'0.0.0'` ) – The project version.

Methods:

- **`format_sphinx`** – Format this inventory as a Sphinx objects.inv file.
- **`parse_sphinx`** – Parse a Sphinx v2 inventory file and return an Inventory from it.
- **`register`** – Create and register an item.

Attributes:

- **`project`** – The project name.
- **`version`** – The project version.

Source code in `src/mkdocstrings/_internal/inventory.py`

```python
def __init__(self, items: list[InventoryItem] | None = None, project: str = "project", version: str = "0.0.0"):
    """Initialize the object.

    Arguments:
        items: A list of items.
        project: The project name.
        version: The project version.
    """
    super().__init__()
    items = items or []
    for item in items:
        self[item.name] = item
    self.project = project
    """The project name."""
    self.version = version
    """The project version."""
```

### project

```python
project = project
```

The project name.

### version

```python
version = version
```

The project version.

### format_sphinx

```python
format_sphinx() -> bytes
```

Format this inventory as a Sphinx `objects.inv` file.

Returns:

- `bytes` – The inventory as bytes.

Source code in `src/mkdocstrings/_internal/inventory.py`

```python
def format_sphinx(self) -> bytes:
    """Format this inventory as a Sphinx `objects.inv` file.

    Returns:
        The inventory as bytes.
    """
    header = (
        dedent(
            f"""
            # Sphinx inventory version 2
            # Project: {self.project}
            # Version: {self.version}
            # The remainder of this file is compressed using zlib.
            """,
        )
        .lstrip()
        .encode("utf8")
    )

    lines = [
        item.format_sphinx().encode("utf8")
        for item in sorted(self.values(), key=lambda item: (item.domain, item.name))
    ]
    return header + zlib.compress(b"\n".join(lines) + b"\n", 9)
```

### parse_sphinx

```python
parse_sphinx(
    in_file: BinaryIO,
    *,
    domain_filter: Collection[str] = (),
) -> Inventory
```

Parse a Sphinx v2 inventory file and return an `Inventory` from it.

Parameters:

- #### **`in_file`**

  (`BinaryIO`) – The binary file-like object to read from.

- #### **`domain_filter`**

  (`Collection[str]`, default: `()` ) – A collection of domain values to allow (and filter out all other ones).

Returns:

- `Inventory` – An inventory containing the collected items.

Source code in `src/mkdocstrings/_internal/inventory.py`

```python
@classmethod
def parse_sphinx(cls, in_file: BinaryIO, *, domain_filter: Collection[str] = ()) -> Inventory:
    """Parse a Sphinx v2 inventory file and return an `Inventory` from it.

    Arguments:
        in_file: The binary file-like object to read from.
        domain_filter: A collection of domain values to allow (and filter out all other ones).

    Returns:
        An inventory containing the collected items.
    """
    for _ in range(4):
        in_file.readline()
    lines = zlib.decompress(in_file.read()).splitlines()
    items: list[InventoryItem] = [
        item for line in lines if (item := InventoryItem.parse_sphinx(line.decode("utf8"), return_none=True))
    ]
    if domain_filter:
        items = [item for item in items if item.domain in domain_filter]
    return cls(items)
```

### register

```python
register(
    name: str,
    domain: str,
    role: str,
    uri: str,
    priority: int = 1,
    dispname: str | None = None,
) -> None
```

Create and register an item.

Parameters:

- #### **`name`**

  (`str`) – The item name.

- #### **`domain`**

  (`str`) – The item domain, like 'python' or 'crystal'.

- #### **`role`**

  (`str`) – The item role, like 'class' or 'method'.

- #### **`uri`**

  (`str`) – The item URI.

- #### **`priority`**

  (`int`, default: `1` ) – The item priority. Only used internally by mkdocstrings and Sphinx.

- #### **`dispname`**

  (`str | None`, default: `None` ) – The item display name.

Source code in `src/mkdocstrings/_internal/inventory.py`

```python
def register(
    self,
    name: str,
    domain: str,
    role: str,
    uri: str,
    priority: int = 1,
    dispname: str | None = None,
) -> None:
    """Create and register an item.

    Arguments:
        name: The item name.
        domain: The item domain, like 'python' or 'crystal'.
        role: The item role, like 'class' or 'method'.
        uri: The item URI.
        priority: The item priority. Only used internally by mkdocstrings and Sphinx.
        dispname: The item display name.
    """
    self[name] = InventoryItem(
        name=name,
        domain=domain,
        role=role,
        uri=uri,
        priority=priority,
        dispname=dispname,
    )
```

## InventoryItem

```python
InventoryItem(
    name: str,
    domain: str,
    role: str,
    uri: str,
    priority: int = 1,
    dispname: str | None = None,
)
```

Inventory item.

Parameters:

- ### **`name`**

  (`str`) – The item name.

- ### **`domain`**

  (`str`) – The item domain, like 'python' or 'crystal'.

- ### **`role`**

  (`str`) – The item role, like 'class' or 'method'.

- ### **`uri`**

  (`str`) – The item URI.

- ### **`priority`**

  (`int`, default: `1` ) – The item priority. Only used internally by mkdocstrings and Sphinx.

- ### **`dispname`**

  (`str | None`, default: `None` ) – The item display name.

Methods:

- **`format_sphinx`** – Format this item as a Sphinx inventory line.
- **`parse_sphinx`** – Parse a line from a Sphinx v2 inventory file and return an InventoryItem from it.

Attributes:

- **`dispname`** (`str`) – The item display name.
- **`domain`** (`str`) – The item domain.
- **`name`** (`str`) – The item name.
- **`priority`** (`int`) – The item priority.
- **`role`** (`str`) – The item role.
- **`sphinx_item_regex`** – Regex to parse a Sphinx v2 inventory line.
- **`uri`** (`str`) – The item URI.

Source code in `src/mkdocstrings/_internal/inventory.py`

```python
def __init__(
    self,
    name: str,
    domain: str,
    role: str,
    uri: str,
    priority: int = 1,
    dispname: str | None = None,
):
    """Initialize the object.

    Arguments:
        name: The item name.
        domain: The item domain, like 'python' or 'crystal'.
        role: The item role, like 'class' or 'method'.
        uri: The item URI.
        priority: The item priority. Only used internally by mkdocstrings and Sphinx.
        dispname: The item display name.
    """
    self.name: str = name
    """The item name."""
    self.domain: str = domain
    """The item domain."""
    self.role: str = role
    """The item role."""
    self.uri: str = uri
    """The item URI."""
    self.priority: int = priority
    """The item priority."""
    self.dispname: str = dispname or name
    """The item display name."""
```

### dispname

```python
dispname: str = dispname or name
```

The item display name.

### domain

```python
domain: str = domain
```

The item domain.

### name

```python
name: str = name
```

The item name.

### priority

```python
priority: int = priority
```

The item priority.

### role

```python
role: str = role
```

The item role.

### sphinx_item_regex

```python
sphinx_item_regex = compile(
    "^(.+?)\\s+(\\S+):(\\S+)\\s+(-?\\d+)\\s+(\\S+)\\s*(.*)$"
)
```

Regex to parse a Sphinx v2 inventory line.

### uri

```python
uri: str = uri
```

The item URI.

### format_sphinx

```python
format_sphinx() -> str
```

Format this item as a Sphinx inventory line.

Returns:

- `str` – A line formatted for an objects.inv file.

Source code in `src/mkdocstrings/_internal/inventory.py`

```python
def format_sphinx(self) -> str:
    """Format this item as a Sphinx inventory line.

    Returns:
        A line formatted for an `objects.inv` file.
    """
    dispname = self.dispname
    if dispname == self.name:
        dispname = "-"
    uri = self.uri
    if uri.endswith(self.name):
        uri = uri[: -len(self.name)] + "$"
    return f"{self.name} {self.domain}:{self.role} {self.priority} {uri} {dispname}"
```

### parse_sphinx

```python
parse_sphinx(
    line: str, *, return_none: Literal[False]
) -> InventoryItem
```

```python
parse_sphinx(
    line: str, *, return_none: Literal[True]
) -> InventoryItem | None
```

```python
parse_sphinx(
    line: str, *, return_none: bool = False
) -> InventoryItem | None
```

Parse a line from a Sphinx v2 inventory file and return an `InventoryItem` from it.

Source code in `src/mkdocstrings/_internal/inventory.py`

```python
@classmethod
def parse_sphinx(cls, line: str, *, return_none: bool = False) -> InventoryItem | None:
    """Parse a line from a Sphinx v2 inventory file and return an `InventoryItem` from it."""
    match = cls.sphinx_item_regex.search(line)
    if not match:
        if return_none:
            return None
        raise ValueError(line)
    name, domain, role, priority, uri, dispname = match.groups()
    if uri.endswith("$"):
        uri = uri[:-1] + name
    if dispname == "-":
        dispname = name
    return cls(name, domain, role, uri, int(priority), dispname)
```

## LoggerAdapter

```python
LoggerAdapter(prefix: str, logger: Logger)
```

Bases: `LoggerAdapter`

A logger adapter to prefix messages.

This adapter also adds an additional parameter to logging methods called `once`: if `True`, the message will only be logged once.

Examples:

In Python code:

```pycon
>>> logger = get_logger("myplugin")
>>> logger.debug("This is a debug message.")
>>> logger.info("This is an info message.", once=True)
```

In Jinja templates (logger available in context as `log`):

```jinja
{{ log.debug("This is a debug message.") }}
{{ log.info("This is an info message.", once=True) }}
```

Parameters:

- ### **`prefix`**

  (`str`) – The string to insert in front of every message.

- ### **`logger`**

  (`Logger`) – The logger instance.

Methods:

- **`log`** – Log a message.
- **`process`** – Process the message.

Attributes:

- **`prefix`** – The prefix to insert in front of every message.

Source code in `src/mkdocstrings/_internal/loggers.py`

```python
def __init__(self, prefix: str, logger: logging.Logger):
    """Initialize the object.

    Arguments:
        prefix: The string to insert in front of every message.
        logger: The logger instance.
    """
    super().__init__(logger, {})
    self.prefix = prefix
    """The prefix to insert in front of every message."""
    self._logged: set[tuple[LoggerAdapter, str]] = set()
```

### prefix

```python
prefix = prefix
```

The prefix to insert in front of every message.

### log

```python
log(
    level: int, msg: object, *args: object, **kwargs: object
) -> None
```

Log a message.

Parameters:

- #### **`level`**

  (`int`) – The logging level.

- #### **`msg`**

  (`object`) – The message.

- #### **`*args`**

  (`object`, default: `()` ) – Additional arguments passed to parent method.

- #### **`**kwargs`**

  (`object`, default: `{}` ) – Additional keyword arguments passed to parent method.

Source code in `src/mkdocstrings/_internal/loggers.py`

```python
def log(self, level: int, msg: object, *args: object, **kwargs: object) -> None:
    """Log a message.

    Arguments:
        level: The logging level.
        msg: The message.
        *args: Additional arguments passed to parent method.
        **kwargs: Additional keyword arguments passed to parent method.
    """
    if kwargs.pop("once", False):
        if (key := (self, str(msg))) in self._logged:
            return
        self._logged.add(key)
    super().log(level, msg, *args, **kwargs)  # type: ignore[arg-type]
```

### process

```python
process(
    msg: str, kwargs: MutableMapping[str, Any]
) -> tuple[str, Any]
```

Process the message.

Parameters:

- #### **`msg`**

  (`str`) – The message:

- #### **`kwargs`**

  (`MutableMapping[str, Any]`) – Remaining arguments.

Returns:

- `tuple[str, Any]` – The processed message.

Source code in `src/mkdocstrings/_internal/loggers.py`

```python
def process(self, msg: str, kwargs: MutableMapping[str, Any]) -> tuple[str, Any]:
    """Process the message.

    Arguments:
        msg: The message:
        kwargs: Remaining arguments.

    Returns:
        The processed message.
    """
    return f"{self.prefix}: {msg}", kwargs
```

## MkdocstringsExtension

```python
MkdocstringsExtension(
    handlers: Handlers,
    autorefs: AutorefsPlugin,
    **kwargs: Any,
)
```

Bases: `Extension`

Our Markdown extension.

It cannot work outside of `mkdocstrings`.

Parameters:

- ### **`handlers`**

  (`Handlers`) – The handlers container.

- ### **`autorefs`**

  (`AutorefsPlugin`) – The autorefs plugin instance.

- ### **`**kwargs`**

  (`Any`, default: `{}` ) – Keyword arguments used by markdown.extensions.Extension.

Methods:

- **`extendMarkdown`** – Register the extension.

Source code in `src/mkdocstrings/_internal/extension.py`

```python
def __init__(self, handlers: Handlers, autorefs: AutorefsPlugin, **kwargs: Any) -> None:
    """Initialize the object.

    Arguments:
        handlers: The handlers container.
        autorefs: The autorefs plugin instance.
        **kwargs: Keyword arguments used by `markdown.extensions.Extension`.
    """
    super().__init__(**kwargs)
    self._handlers = handlers
    self._autorefs = autorefs
```

### extendMarkdown

```python
extendMarkdown(md: Markdown) -> None
```

Register the extension.

Add an instance of our AutoDocProcessor to the Markdown parser.

Parameters:

- #### **`md`**

  (`Markdown`) – A markdown.Markdown instance.

Source code in `src/mkdocstrings/_internal/extension.py`

```python
def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802 (casing: parent method's name)
    """Register the extension.

    Add an instance of our [`AutoDocProcessor`][mkdocstrings.AutoDocProcessor] to the Markdown parser.

    Arguments:
        md: A `markdown.Markdown` instance.
    """
    md.parser.blockprocessors.register(
        AutoDocProcessor(md, handlers=self._handlers, autorefs=self._autorefs),
        "mkdocstrings",
        priority=75,  # Right before markdown.blockprocessors.HashHeaderProcessor
    )
    md.treeprocessors.register(
        _HeadingsPostProcessor(md),
        "mkdocstrings_post_headings",
        priority=4,  # Right after 'toc'.
    )
    md.treeprocessors.register(
        _TocLabelsTreeProcessor(md),
        "mkdocstrings_post_toc_labels",
        priority=4,  # Right after 'toc'.
    )
```

## MkdocstringsInnerExtension

```python
MkdocstringsInnerExtension(headings: list[Element])
```

Bases: `Extension`

Extension that should always be added to Markdown sub-documents that handlers request (and *only* them).

Parameters:

- ### **`headings`**

  (`list[Element]`) – A list that will be populated with all HTML heading elements encountered in the document.

Methods:

- **`extendMarkdown`** – Register the extension.

Attributes:

- **`headings`** – The list that will be populated with all HTML heading elements encountered in the document.

Source code in `src/mkdocstrings/_internal/handlers/rendering.py`

```python
def __init__(self, headings: list[Element]):
    """Initialize the object.

    Arguments:
        headings: A list that will be populated with all HTML heading elements encountered in the document.
    """
    super().__init__()
    self.headings = headings
    """The list that will be populated with all HTML heading elements encountered in the document."""
```

### headings

```python
headings = headings
```

The list that will be populated with all HTML heading elements encountered in the document.

### extendMarkdown

```python
extendMarkdown(md: Markdown) -> None
```

Register the extension.

Parameters:

- #### **`md`**

  (`Markdown`) – A markdown.Markdown instance.

Source code in `src/mkdocstrings/_internal/handlers/rendering.py`

```python
def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802 (casing: parent method's name)
    """Register the extension.

    Arguments:
        md: A `markdown.Markdown` instance.
    """
    md.registerExtension(self)
    md.treeprocessors.register(
        HeadingShiftingTreeprocessor(md, 0),
        HeadingShiftingTreeprocessor.name,
        priority=12,
    )
    md.treeprocessors.register(
        IdPrependingTreeprocessor(md, ""),
        IdPrependingTreeprocessor.name,
        priority=4,  # Right after 'toc' (needed because that extension adds ids to headers).
    )
    md.treeprocessors.register(
        _HeadingReportingTreeprocessor(md, self.headings),
        _HeadingReportingTreeprocessor.name,
        priority=1,  # Close to the end.
    )
    md.treeprocessors.register(
        ParagraphStrippingTreeprocessor(md),
        ParagraphStrippingTreeprocessor.name,
        priority=0.99,  # Close to the end.
    )
```

## MkdocstringsPlugin

```python
MkdocstringsPlugin()
```

Bases: `BasePlugin[PluginConfig]`

An `mkdocs` plugin.

This plugin defines the following event hooks:

- `on_config`
- `on_env`
- `on_post_build`

Check the [Developing Plugins](https://www.mkdocs.org/user-guide/plugins/#developing-plugins) page of `mkdocs` for more information about its plugin system.

Methods:

- **`get_handler`** – Get a handler by its name. See mkdocstrings.Handlers.get_handler.
- **`on_config`** – Instantiate our Markdown extension.
- **`on_post_build`** – Teardown the handlers.

Attributes:

- **`css_filename`** (`str`) – The path of the CSS file to write in the site directory.
- **`handlers`** (`Handlers`) – Get the instance of mkdocstrings.Handlers for this plugin/build.
- **`inventory_enabled`** (`bool`) – Tell if the inventory is enabled or not.
- **`on_env`** – Extra actions that need to happen after all Markdown-to-HTML page rendering.
- **`plugin_enabled`** (`bool`) – Tell if the plugin is enabled or not.

Source code in `src/mkdocstrings/_internal/plugin.py`

```python
def __init__(self) -> None:
    """Initialize the object."""
    super().__init__()
    self._handlers: Handlers | None = None
```

### css_filename

```python
css_filename: str = 'assets/_mkdocstrings.css'
```

The path of the CSS file to write in the site directory.

### handlers

```python
handlers: Handlers
```

Get the instance of mkdocstrings.Handlers for this plugin/build.

Raises:

- `RuntimeError` – If the plugin hasn't been initialized with a config.

Returns:

- `Handlers` – An instance of mkdocstrings.Handlers (the same throughout the build).

### inventory_enabled

```python
inventory_enabled: bool
```

Tell if the inventory is enabled or not.

Returns:

- `bool` – Whether the inventory is enabled.

### on_env

```python
on_env = CombinedEvent(
    _on_env_load_inventories,
    _on_env_add_css,
    _on_env_write_inventory,
    _on_env_apply_backlinks,
)
```

Extra actions that need to happen after all Markdown-to-HTML page rendering.

Hook for the [`on_env` event](https://www.mkdocs.org/user-guide/plugins/#on_env).

- Gather results from background inventory download tasks.
- Write mkdocstrings' extra files (CSS, inventory) into the site directory.
- Apply backlinks to the HTML output of each page.

### plugin_enabled

```python
plugin_enabled: bool
```

Tell if the plugin is enabled or not.

Returns:

- `bool` – Whether the plugin is enabled.

### get_handler

```python
get_handler(handler_name: str) -> BaseHandler
```

Get a handler by its name. See mkdocstrings.Handlers.get_handler.

Parameters:

- #### **`handler_name`**

  (`str`) – The name of the handler.

Returns:

- `BaseHandler` – An instance of a subclass of BaseHandler.

Source code in `src/mkdocstrings/_internal/plugin.py`

```python
def get_handler(self, handler_name: str) -> BaseHandler:
    """Get a handler by its name. See [mkdocstrings.Handlers.get_handler][].

    Arguments:
        handler_name: The name of the handler.

    Returns:
        An instance of a subclass of [`BaseHandler`][mkdocstrings.BaseHandler].
    """
    return self.handlers.get_handler(handler_name)
```

### on_config

```python
on_config(config: MkDocsConfig) -> MkDocsConfig | None
```

Instantiate our Markdown extension.

Hook for the [`on_config` event](https://www.mkdocs.org/user-guide/plugins/#on_config). In this hook, we instantiate our MkdocstringsExtension and add it to the list of Markdown extensions used by `mkdocs`.

We pass this plugin's configuration dictionary to the extension when instantiating it (it will need it later when processing markdown to get handlers and their global configurations).

Parameters:

- #### **`config`**

  (`MkDocsConfig`) – The MkDocs config object.

Returns:

- `MkDocsConfig | None` – The modified config.

Source code in `src/mkdocstrings/_internal/plugin.py`

```python
def on_config(self, config: MkDocsConfig) -> MkDocsConfig | None:
    """Instantiate our Markdown extension.

    Hook for the [`on_config` event](https://www.mkdocs.org/user-guide/plugins/#on_config).
    In this hook, we instantiate our [`MkdocstringsExtension`][mkdocstrings.MkdocstringsExtension]
    and add it to the list of Markdown extensions used by `mkdocs`.

    We pass this plugin's configuration dictionary to the extension when instantiating it (it will need it
    later when processing markdown to get handlers and their global configurations).

    Arguments:
        config: The MkDocs config object.

    Returns:
        The modified config.
    """
    if not self.plugin_enabled:
        _logger.debug("Plugin is not enabled. Skipping.")
        return config
    _logger.debug("Adding extension to the list")

    locale = self.config.locale or config.theme.get("language") or config.theme.get("locale") or "en"
    locale = str(locale).replace("_", "-")

    handlers = Handlers(
        default=self.config.default_handler,
        handlers_config=self.config.handlers,
        theme=config.theme.name or os.path.dirname(config.theme.dirs[0]),
        custom_templates=self.config.custom_templates,
        mdx=config.markdown_extensions,
        mdx_config=config.mdx_configs,
        inventory_project=config.site_name,
        inventory_version="0.0.0",  # TODO: Find a way to get actual version.
        locale=locale,
        tool_config=config,
    )

    handlers._download_inventories()

    AutorefsPlugin.record_backlinks = True
    autorefs: AutorefsPlugin
    try:
        # If autorefs plugin is explicitly enabled, just use it.
        autorefs = config.plugins["autorefs"]  # type: ignore[assignment]
        _logger.debug("Picked up existing autorefs instance %r", autorefs)
    except KeyError:
        # Otherwise, add a limited instance of it that acts only on what's added through `register_anchor`.
        autorefs = AutorefsPlugin()
        autorefs.config = AutorefsConfig()
        autorefs.scan_toc = False
        config.plugins["autorefs"] = autorefs
        _logger.debug("Added a subdued autorefs instance %r", autorefs)

    mkdocstrings_extension = MkdocstringsExtension(handlers, autorefs)
    config.markdown_extensions.append(mkdocstrings_extension)  # type: ignore[arg-type]

    config.extra_css.insert(0, self.css_filename)  # So that it has lower priority than user files.

    self._autorefs = autorefs
    self._handlers = handlers
    return config
```

### on_post_build

```python
on_post_build(config: MkDocsConfig, **kwargs: Any) -> None
```

Teardown the handlers.

Hook for the [`on_post_build` event](https://www.mkdocs.org/user-guide/plugins/#on_post_build). This hook is used to teardown all the handlers that were instantiated and cached during documentation buildup.

For example, a handler could open a subprocess in the background and keep it open to feed it "autodoc" instructions and get back JSON data. If so, it should then close the subprocess at some point: the proper place to do this is in the handler's `teardown` method, which is indirectly called by this hook.

Parameters:

- #### **`config`**

  (`MkDocsConfig`) – The MkDocs config object.

- #### **`**kwargs`**

  (`Any`, default: `{}` ) – Additional arguments passed by MkDocs.

Source code in `src/mkdocstrings/_internal/plugin.py`

```python
def on_post_build(
    self,
    config: MkDocsConfig,  # noqa: ARG002
    **kwargs: Any,  # noqa: ARG002
) -> None:
    """Teardown the handlers.

    Hook for the [`on_post_build` event](https://www.mkdocs.org/user-guide/plugins/#on_post_build).
    This hook is used to teardown all the handlers that were instantiated and cached during documentation buildup.

    For example, a handler could open a subprocess in the background and keep it open
    to feed it "autodoc" instructions and get back JSON data. If so, it should then close the subprocess at some point:
    the proper place to do this is in the handler's `teardown` method, which is indirectly called by this hook.

    Arguments:
        config: The MkDocs config object.
        **kwargs: Additional arguments passed by MkDocs.
    """
    if not self.plugin_enabled:
        return

    if self._handlers:
        _logger.debug("Tearing handlers down")
        self.handlers.teardown()
```

## ParagraphStrippingTreeprocessor

Bases: `Treeprocessor`

Unwraps the `<p>` element around the whole output.

Methods:

- **`run`** – Unwrap the root element if it's a single <p> element.

Attributes:

- **`name`** (`str`) – The name of the treeprocessor.
- **`strip`** (`bool`) – Whether to strip <p> elements or not.

### name

```python
name: str = 'mkdocstrings_strip_paragraph'
```

The name of the treeprocessor.

### strip

```python
strip: bool = False
```

Whether to strip `<p>` elements or not.

### run

```python
run(root: Element) -> Element | None
```

Unwrap the root element if it's a single `<p>` element.

Source code in `src/mkdocstrings/_internal/handlers/rendering.py`

```python
def run(self, root: Element) -> Element | None:
    """Unwrap the root element if it's a single `<p>` element."""
    if self.strip and len(root) == 1 and root[0].tag == "p":
        # Turn the single `<p>` element into the root element and inherit its tag name (it's significant!)
        root[0].tag = root.tag
        return root[0]
    return None
```

## PluginConfig

Bases: `Config`

The configuration options of `mkdocstrings`, written in `mkdocs.yml`.

Attributes:

- **`custom_templates`** – Location of custom templates to use when rendering API objects.
- **`default_handler`** – The default handler to use. The value is the name of the handler module. Default is "python".
- **`enable_inventory`** – Whether to enable object inventory creation.
- **`enabled`** – Whether to enable the plugin. Default is true. If false, mkdocstrings will not collect or render anything.
- **`handlers`** – Global configuration of handlers.
- **`locale`** – The locale to use for translations.

### custom_templates

```python
custom_templates = Optional(Dir(exists=True))
```

Location of custom templates to use when rendering API objects.

Value should be the path of a directory relative to the MkDocs configuration file.

### default_handler

```python
default_handler = Type(str, default='python')
```

The default handler to use. The value is the name of the handler module. Default is "python".

### enable_inventory

```python
enable_inventory = Optional(Type(bool))
```

Whether to enable object inventory creation.

### enabled

```python
enabled = Type(bool, default=True)
```

Whether to enable the plugin. Default is true. If false, *mkdocstrings* will not collect or render anything.

### handlers

```python
handlers = Type(dict, default={})
```

Global configuration of handlers.

You can set global configuration per handler, applied everywhere, but overridable in each "autodoc" instruction. Example:

```yaml
plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            option1: true
            option2: "value"
        rust:
          options:
            option9: 2
```

### locale

```python
locale = Optional(Type(str))
```

The locale to use for translations.

## TemplateLogger

```python
TemplateLogger(logger: LoggerAdapter)
```

A wrapper class to allow logging in templates.

The logging methods provided by this class all accept two parameters:

- `msg`: The message to log.
- `once`: If `True`, the message will only be logged once.

Methods:

- **`debug`** – Function to log a DEBUG message.
- **`info`** – Function to log an INFO message.
- **`warning`** – Function to log a WARNING message.
- **`error`** – Function to log an ERROR message.
- **`critical`** – Function to log a CRITICAL message.

Parameters:

- ### **`logger`**

  (`LoggerAdapter`) – A logger adapter.

Attributes:

- **`critical`** – Log a CRITICAL message.
- **`debug`** – Log a DEBUG message.
- **`error`** – Log an ERROR message.
- **`info`** – Log an INFO message.
- **`warning`** – Log a WARNING message.

Source code in `src/mkdocstrings/_internal/loggers.py`

```python
def __init__(self, logger: LoggerAdapter):
    """Initialize the object.

    Arguments:
        logger: A logger adapter.
    """
    self.debug = get_template_logger_function(logger.debug)
    """Log a DEBUG message."""
    self.info = get_template_logger_function(logger.info)
    """Log an INFO message."""
    self.warning = get_template_logger_function(logger.warning)
    """Log a WARNING message."""
    self.error = get_template_logger_function(logger.error)
    """Log an ERROR message."""
    self.critical = get_template_logger_function(logger.critical)
    """Log a CRITICAL message."""
```

### critical

```python
critical = get_template_logger_function(critical)
```

Log a CRITICAL message.

### debug

```python
debug = get_template_logger_function(debug)
```

Log a DEBUG message.

### error

```python
error = get_template_logger_function(error)
```

Log an ERROR message.

### info

```python
info = get_template_logger_function(info)
```

Log an INFO message.

### warning

```python
warning = get_template_logger_function(warning)
```

Log a WARNING message.

## ThemeNotSupported

Bases: `Exception`

An exception raised to tell a theme is not supported.

## do_any

```python
do_any(seq: Sequence, attribute: str | None = None) -> bool
```

Check if at least one of the item in the sequence evaluates to true.

The `any` builtin as a filter for Jinja templates.

Parameters:

- ### **`seq`**

  (`Sequence`) – An iterable object.

- ### **`attribute`**

  (`str | None`, default: `None` ) – The attribute name to use on each object of the iterable.

Returns:

- `bool` – A boolean telling if any object of the iterable evaluated to True.

Source code in `src/mkdocstrings/_internal/handlers/base.py`

```python
def do_any(seq: Sequence, attribute: str | None = None) -> bool:
    """Check if at least one of the item in the sequence evaluates to true.

    The `any` builtin as a filter for Jinja templates.

    Arguments:
        seq: An iterable object.
        attribute: The attribute name to use on each object of the iterable.

    Returns:
        A boolean telling if any object of the iterable evaluated to True.
    """
    if attribute is None:
        return any(seq)
    return any(_[attribute] for _ in seq)
```

## get_logger

```python
get_logger(name: str) -> LoggerAdapter
```

Return a pre-configured logger.

Parameters:

- ### **`name`**

  (`str`) – The name to use with logging.getLogger.

Returns:

- `LoggerAdapter` – A logger configured to work well in MkDocs.

Source code in `src/mkdocstrings/_internal/loggers.py`

```python
def get_logger(name: str) -> LoggerAdapter:
    """Return a pre-configured logger.

    Arguments:
        name: The name to use with `logging.getLogger`.

    Returns:
        A logger configured to work well in MkDocs.
    """
    logger = logging.getLogger(f"mkdocs.plugins.{name}")
    return LoggerAdapter(name.split(".", 1)[0], logger)
```

## get_template_logger

```python
get_template_logger(
    handler_name: str | None = None,
) -> TemplateLogger
```

Return a logger usable in templates.

Parameters:

- ### **`handler_name`**

  (`str | None`, default: `None` ) – The name of the handler.

Returns:

- `TemplateLogger` – A template logger.

Source code in `src/mkdocstrings/_internal/loggers.py`

```python
def get_template_logger(handler_name: str | None = None) -> TemplateLogger:
    """Return a logger usable in templates.

    Parameters:
        handler_name: The name of the handler.

    Returns:
        A template logger.
    """
    handler_name = handler_name or "base"
    return TemplateLogger(get_logger(f"mkdocstrings_handlers.{handler_name}.templates"))
```

## get_template_logger_function

```python
get_template_logger_function(
    logger_func: Callable,
) -> Callable
```

Create a wrapper function that automatically receives the Jinja template context.

Parameters:

- ### **`logger_func`**

  (`Callable`) – The logger function to use within the wrapper.

Returns:

- `Callable` – A function.

Source code in `src/mkdocstrings/_internal/loggers.py`

```python
def get_template_logger_function(logger_func: Callable) -> Callable:
    """Create a wrapper function that automatically receives the Jinja template context.

    Arguments:
        logger_func: The logger function to use within the wrapper.

    Returns:
        A function.
    """

    @pass_context
    def wrapper(context: Context, msg: str | None = None, *args: Any, **kwargs: Any) -> str:
        """Log a message.

        Arguments:
            context: The template context, automatically provided by Jinja.
            msg: The message to log.
            **kwargs: Additional arguments passed to the logger function.

        Returns:
            An empty string.
        """
        logger_func(f"%s: {msg or 'Rendering'}", _Lazy(get_template_path, context), *args, **kwargs)
        return ""

    return wrapper
```

## get_template_path

```python
get_template_path(context: Context) -> str
```

Return the path to the template currently using the given context.

Parameters:

- ### **`context`**

  (`Context`) – The template context.

Returns:

- `str` – The relative path to the template.

Source code in `src/mkdocstrings/_internal/loggers.py`

```python
def get_template_path(context: Context) -> str:
    """Return the path to the template currently using the given context.

    Arguments:
        context: The template context.

    Returns:
        The relative path to the template.
    """
    context_name: str = str(context.name)
    filename = context.environment.get_template(context_name).filename
    if filename:
        for template_dir in TEMPLATES_DIRS:
            with suppress(ValueError):
                return str(Path(filename).relative_to(template_dir))
        with suppress(ValueError):
            return str(Path(filename).relative_to(Path.cwd()))
        return filename
    return context_name
```

## makeExtension

```python
makeExtension(
    *,
    default_handler: str | None = None,
    inventory_project: str | None = None,
    inventory_version: str | None = None,
    handlers: dict[str, dict] | None = None,
    custom_templates: str | None = None,
    markdown_extensions: list[str | dict] | None = None,
    locale: str | None = None,
    config_file_path: str | None = None,
) -> MkdocstringsExtension
```

Create the extension instance.

We only support this function being used by Zensical. Consider this function private API.

Source code in `src/mkdocstrings/_internal/extension.py`

```python
def makeExtension(  # noqa: N802
    *,
    default_handler: str | None = None,
    inventory_project: str | None = None,
    inventory_version: str | None = None,
    handlers: dict[str, dict] | None = None,
    custom_templates: str | None = None,
    markdown_extensions: list[str | dict] | None = None,
    locale: str | None = None,
    config_file_path: str | None = None,
) -> MkdocstringsExtension:
    """Create the extension instance.

    We only support this function being used by Zensical.
    Consider this function private API.
    """
    mdx, mdx_config = _split_configs(markdown_extensions or [])
    tool_config = _ToolConfig(config_file_path=config_file_path)

    handlers_instance = Handlers(
        theme="material",
        default=default_handler or _default_config["default_handler"],
        inventory_project=inventory_project or "Project",
        inventory_version=inventory_version or "0.0.0",
        handlers_config=handlers or _default_config["handlers"],
        custom_templates=custom_templates or _default_config["custom_templates"],
        mdx=mdx,
        mdx_config=mdx_config,
        locale=locale or _default_config["locale"],
        tool_config=tool_config,
    )

    handlers_instance._download_inventories()

    autorefs = AutorefsPlugin()
    autorefs.config = AutorefsConfig()
    autorefs.scan_toc = False

    return MkdocstringsExtension(handlers=handlers_instance, autorefs=autorefs)
```
