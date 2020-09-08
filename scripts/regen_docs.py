"""Regenerate all templated documentation pages."""

import sys

import httpx
from gen_credits_data import get_data as get_credits
from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment

URL_PREFIX = "https://raw.githubusercontent.com/pawamoy/jinja-templates/master/"
REGEN = (("docs/credits.md", get_credits, URL_PREFIX + "credits.md"),)


def main() -> int:
    """
    Regenerate pages listed in global `REGEN` list.

    Returns:
        An exit code.
    """
    env = SandboxedEnvironment(undefined=StrictUndefined)
    for target, get_data, template in REGEN:
        print("Regenerating", target)  # noqa: WPS421 (side-effect in main is fine)
        template_data = get_data()
        template_text = httpx.get(template).text
        rendered = env.from_string(template_text).render(**template_data)
        with open(target, "w") as stream:
            stream.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
