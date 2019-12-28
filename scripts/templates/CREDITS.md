<!--
IMPORTANT:
  This file is generated from the template at 'scripts/templates/CREDITS.md'.
  Please update the template instead of this file.
-->

# Credits
These projects were used to build `mkdocstrings`. **Thank you!**

[`python`](https://www.python.org/) |
[`poetry`](https://poetry.eustace.io/) |
[`cookie-poetry`](https://github.com/pawamoy/cookie-poetry)

### Direct dependencies
{%- for dep in direct_dependencies -%}
{%- with package = package_info.get(dep, {}) %}
[`{{ package.get("name", dep) }}`]({{ package.get("home-page", "") }}){% if not loop.last %} |{% endif %}
{%- endwith -%}
{%- endfor %}

### Indirect dependencies
{%- for dep in indirect_dependencies -%}
{%- with package = package_info.get(dep, {}) %}
[`{{ package.get("name", dep) }}`]({{ package.get("home-page", "") }}){% if not loop.last %} |{% endif %}
{%- endwith -%}
{%- endfor %}

**[More credits from the author](http://pawamoy.github.io/credits/)**
