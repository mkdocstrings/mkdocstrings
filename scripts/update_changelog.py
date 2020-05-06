"""Insert the new version changes in the changelog."""

import re
import sys

import requests
from git_changelog.build import Changelog
from jinja2.sandbox import SandboxedEnvironment

TEMPLATE_URL = "https://raw.githubusercontent.com/pawamoy/jinja-templates/master/keepachangelog.md"
COMMIT_STYLE = "angular"

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage: update_changelog.py <FILE> <MARKER> <VERSION_REGEX>", file=sys.stderr)
        sys.exit(1)

    env = SandboxedEnvironment(autoescape=True)
    template = env.from_string(requests.get(TEMPLATE_URL).text)
    changelog = Changelog(".", style=COMMIT_STYLE)
    inplace_file, marker, version_regex = sys.argv[1:]
    with open(inplace_file, "r") as fd:
        old_lines = fd.read().splitlines(keepends=False)
    # get last version
    version_re = re.compile(version_regex)
    last_released = None
    for line in old_lines:
        match = version_re.search(line)
        if match:
            last_released = match.groupdict()["version"]
            break
    # only keep more recent versions
    versions = []
    for version in changelog.versions_list:
        if version.tag == last_released:
            break
        versions.append(version)
    changelog.versions_list = versions
    # render and insert
    rendered = template.render(changelog=changelog, inplace=True)
    for i in range(len(old_lines)):
        if old_lines[i] == marker:
            old_lines[i] = rendered
            break
        i += 1
    with open(inplace_file, "w") as fd:
        fd.write("\n".join(old_lines))
