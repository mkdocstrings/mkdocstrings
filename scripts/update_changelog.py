"""Insert the new version changes in the changelog."""

import re
import sys
from typing import List, Optional, Pattern

import httpx
from git_changelog.build import Changelog, Version
from jinja2.sandbox import SandboxedEnvironment

TEMPLATE_URL = "https://raw.githubusercontent.com/pawamoy/jinja-templates/master/keepachangelog.md"
COMMIT_STYLE = "angular"


def latest(lines: List[str], regex: Pattern) -> Optional[str]:
    """
    Return the last released version.

    Arguments:
        lines: Lines of the changelog file.
        regex: A compiled regex to find version numbers.

    Returns:
        The last version.
    """
    for line in lines:
        match = regex.search(line)
        if match:
            return match.groupdict()["version"]
    return None


def unreleased(versions: List[Version], last_release: str) -> List[Version]:
    """
    Return the most recent versions down to latest release.

    Arguments:
        versions: All the versions (released and unreleased).
        last_release: The latest release.

    Returns:
        A list of versions.
    """
    for index, version in enumerate(versions):
        if version.tag == last_release:
            return versions[:index]
    return versions


def read_changelog(filepath: str) -> List[str]:
    """
    Read the changelog file.

    Arguments:
        filepath: The path to the changelog file.

    Returns:
        The changelog lines.
    """
    with open(filepath, "r") as changelog_file:
        return changelog_file.read().splitlines(keepends=False)


def write_changelog(filepath: str, lines: List[str]) -> None:
    """
    Write the changelog file.

    Arguments:
        filepath: The path to the changelog file.
        lines: The lines to write to the file.
    """
    with open(filepath, "w") as changelog_file:
        changelog_file.write("\n".join(lines).rstrip("\n") + "\n")


def update_changelog(inplace_file: str, marker: str, version_regex: str) -> None:
    """
    Update the given changelog file in place.

    Arguments:
        inplace_file: The file to update in-place.
        marker: The line after which to insert new contents.
        version_regex: A regular expression to find currently documented versions in the file.
    """
    env = SandboxedEnvironment(autoescape=True)
    template = env.from_string(httpx.get(TEMPLATE_URL).text)
    changelog = Changelog(".", style=COMMIT_STYLE)

    if len(changelog.versions_list) == 1:
        last_version = changelog.versions_list[0]
        if last_version.planned_tag is None:
            planned_tag = "v0.1.0"
            last_version.tag = planned_tag
            last_version.url += planned_tag
            last_version.compare_url = last_version.compare_url.replace("HEAD", planned_tag)

    lines = read_changelog(inplace_file)
    last_released = latest(lines, re.compile(version_regex))
    if last_released:
        changelog.versions_list = unreleased(changelog.versions_list, last_released)
    rendered = template.render(changelog=changelog, inplace=True)
    lines[lines.index(marker)] = rendered
    write_changelog(inplace_file, lines)


def main(args):
    """
    Run the main script.

    Arguments:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    if len(args) != 3:
        print(  # noqa: WPS421 (side-effect)
            "usage: update_changelog.py <FILE> <MARKER> <VERSION_REGEX>",
            file=sys.stderr,
        )
        return 1

    update_changelog(*args)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
