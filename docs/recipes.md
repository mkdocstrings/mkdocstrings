On this page you will find various recipes, tips and tricks
for *mkdocstrings* and more generally Markdown documentation.

## Prevent selection of `>>>` in Python code blocks

To prevent the selection of `>>>` in Python code blocks,
you can use the `pycon` language on your code block,
and add some CSS rules to your site using MkDocs `extra_css` option:

````md
```pycon
>>> print("Hello mkdocstrings!")
```
````

```css title="docs/css/code_select.css"
.highlight .gp, .highlight .go { /* Generic.Prompt, Generic.Output */
    user-select: none;
}
```

```yaml title="mkdocs.yml"
extra_css:
- css/code_select.css
```

Try to select the following code block's text:

<style>
.highlight .gp, .highlight .go { /* Generic.Prompt, Generic.Output */
    user-select: none;
}
</style>

```pycon
>>> print("Hello mkdocstrings!")
```
