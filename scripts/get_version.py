# Get current project version from Git tags or changelog.

import re
from contextlib import suppress
from pathlib import Path

from pdm.backend.hooks.version import SCMVersion, Version, default_version_formatter, get_version_from_scm

_root = Path(__file__).parent.parent
_changelog = _root / "CHANGELOG.md"
_changelog_version_re = re.compile(r"^## \[(\d+\.\d+\.\d+)\].*$")
_default_scm_version = SCMVersion(Version("0.0.0"), None, False, None, None)  # noqa: FBT003


def get_version() -> str:
    scm_version = get_version_from_scm(_root) or _default_scm_version
    if scm_version.version <= Version("0.1"):  # Missing Git tags?
        with suppress(OSError, StopIteration):  # noqa: SIM117
            with _changelog.open("r", encoding="utf8") as file:
                match = next(filter(None, map(_changelog_version_re.match, file)))
                scm_version = scm_version._replace(version=Version(match.group(1)))
    return default_version_formatter(scm_version)


if __name__ == "__main__":
    print(get_version())
