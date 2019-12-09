<!--
IMPORTANT:
  This file is generated from the template at 'scripts/templates/CREDITS.md'.
  Please update the template instead of this file.
-->

# Credits
These projects were used to build `mkdocstrings`. **Thank you!**

[![`python`](https://www.vectorlogo.zone/logos/python/python-ar21.svg)](https://www.python.org/) |
[`poetry`](https://poetry.eustace.io/) |
[`cookie-poetry`](https://github.com/pawamoy/cookie-poetry)

### Direct dependencies
{%- for dep in direct_dependencies -%}
{%- with package = package_info.get(dep, {}) %}
[{% if package.get("vlz-url") %}![{% endif %}`{{ package.get("name", dep) }}`]{% if package.get("vlz-url") %}({{ package["vlz-url"] }})]{% endif %}({{ package.get("home-page", "") }}){% if not loop.last %} |{% endif %}
{%- endwith -%}
{%- endfor %}

### Indirect dependencies
{%- for dep in indirect_dependencies -%}
{%- with package = package_info.get(dep, {}) %}
[{% if package.get("vlz-url") %}![{% endif %}`{{ package.get("name", dep) }}`]{% if package.get("vlz-url") %}({{ package["vlz-url"] }})]{% endif %}({{ package.get("home-page", "") }}){% if not loop.last %} |{% endif %}
{%- endwith -%}
{%- endfor %}

**[More credits from the author](http://pawamoy.github.io/credits/)**

*See one of your project without the logo? Make sure it's available on [VectorLogoZone](https://www.vectorlogo.zone/)
([GitHub repo](https://github.com/VectorLogoZone/vectorlogozone)) and open an issue or send a pull/merge request!*
