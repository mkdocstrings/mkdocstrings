"""Generate redirection pages for autorefs reference."""

import mkdocs_gen_files

redirect_map = {
    "reference/autorefs/references.md": "https://mkdocstrings.github.io/autorefs/reference/mkdocs_autorefs/references/",
    "reference/autorefs/plugin.md": "https://mkdocstrings.github.io/autorefs/reference/mkdocs_autorefs/plugin/",
}

redirect_template = """
<script type="text/javascript">
    window.location.href = "{link}";
</script>
<a href="{link}">Redirecting...</a>
"""

for page, link in redirect_map.items():
    with mkdocs_gen_files.open(page, "w") as fd:
        print(redirect_template.format(link=link), file=fd)
