import base64
import datetime
import gzip
import hashlib
import os
import re
import urllib.parse
import urllib.request
from collections.abc import Mapping
from typing import BinaryIO, Callable, Optional

import click
import platformdirs

from mkdocstrings.loggers import get_logger

log = get_logger(__name__)

# Regex pattern for an environment variable in the form ${ENV_VAR}.
ENV_VAR_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def download_url_with_gz(url: str) -> bytes:
    url, auth_header = _extract_auth_from_url(url)

    req = urllib.request.Request(  # noqa: S310
        url,
        headers={"Accept-Encoding": "gzip", "User-Agent": "mkdocstrings/0.15.0", **auth_header},
    )
    with urllib.request.urlopen(req) as resp:  # noqa: S310
        content: BinaryIO = resp
        if "gzip" in resp.headers.get("content-encoding", ""):
            content = gzip.GzipFile(fileobj=resp)  # type: ignore[assignment]
        return content.read()


def _expand_env_vars(credential: str, url: str, env: Optional[Mapping[str, str]] = None) -> str:
    """A safe implementation of environment variable substitution.

    It only supports the following forms: `${ENV_VAR}`.
    Neither `$ENV_VAR` or `%ENV_VAR` are supported.
    """
    if env is None:
        env = os.environ

    def replace_func(match: re.Match) -> str:
        try:
            return env[match.group(1)]
        except KeyError:
            log.warning("Environment variable '%s' is not set, but is used in inventory URL %s", match.group(1), url)
            return match.group(0)

    return re.sub(ENV_VAR_PATTERN, replace_func, credential)


# Implementation adapted from PDM: https://github.com/pdm-project/pdm.
def _extract_auth_from_url(url: str) -> tuple[str, dict[str, str]]:
    """Extract credentials from the URL if present, and return the URL and the appropriate auth header for the credentials."""
    if "@" not in url:
        return url, {}

    scheme, netloc, *rest = urllib.parse.urlparse(url)
    auth, host = netloc.split("@", 1)
    auth = _expand_env_vars(credential=auth, url=url)
    auth_header = _create_auth_header(credential=auth, url=url)

    url = urllib.parse.urlunparse((scheme, host, *rest))
    return url, auth_header


def _create_auth_header(credential: str, url: str) -> dict[str, str]:
    """Create the Authorization header for basic or bearer authentication, depending on credential."""
    if ":" not in credential:
        # We assume that the user is using a token.
        log.debug("Using bearer token authentication for %s", url)
        return {"Authorization": f"Bearer {credential}"}

    # Else, we assume that the user is using user:password.
    user, pwd = credential.split(":", 1)
    log.debug("Using basic authentication for %s", url)
    credentials = base64.encodebytes(f"{user}:{pwd}".encode()).decode().strip()
    return {"Authorization": f"Basic {credentials}"}


# This is mostly a copy of https://github.com/mkdocs/mkdocs/blob/master/mkdocs/utils/cache.py
# In the future maybe they can be deduplicated.


def download_and_cache_url(
    url: str,
    download: Callable[[str], bytes],
    cache_duration: datetime.timedelta,
    comment: bytes = b"# ",
) -> bytes:
    """Downloads a file from the URL, stores it under ~/.cache/, and returns its content.

    For tracking the age of the content, a prefix is inserted into the stored file, rather than relying on mtime.

    Args:
        url: URL to use.
        download: Callback that will accept the URL and actually perform the download.
        cache_duration: How long to consider the URL content cached.
        comment: The appropriate comment prefix for this file format.
    """
    directory = os.path.join(platformdirs.user_cache_dir("mkdocs"), "mkdocstrings_url_cache")
    name_hash = hashlib.sha256(url.encode()).hexdigest()[:32]
    path = os.path.join(directory, name_hash + os.path.splitext(url)[1])

    now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    prefix = b"%s%s downloaded at timestamp " % (comment, url.encode())
    # Check for cached file and try to return it
    if os.path.isfile(path):
        try:
            with open(path, "rb") as f:
                line = f.readline()
                if line.startswith(prefix):
                    line = line[len(prefix) :]
                    timestamp = int(line)
                    if datetime.timedelta(seconds=(now - timestamp)) <= cache_duration:
                        log.debug("Using cached '%s' for '%s'", path, url)
                        return f.read()
        except (OSError, ValueError) as e:
            log.debug("%s: %s", type(e).__name__, e)

    # Download and cache the file
    log.debug("Downloading '%s' to '%s'", url, path)
    content = download(url)
    os.makedirs(directory, exist_ok=True)
    with click.open_file(path, "wb", atomic=True) as f:
        f.write(b"%s%d\n" % (prefix, now))
        f.write(content)
    return content
