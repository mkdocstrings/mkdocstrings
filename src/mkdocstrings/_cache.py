import base64
import datetime
import gzip
import hashlib
import os
import urllib.parse
import urllib.request
from typing import BinaryIO, Callable, Union

import click
import platformdirs
import regex as re

from mkdocstrings.loggers import get_logger

log = get_logger(__name__)

# Regex pattern for an environment variable
ENV_VAR_PATTERN = re.compile(r"^\$([A-Za-z_][A-Za-z0-9_]*)$")


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


def _extract_auth_from_url(url: str) -> tuple[str, dict[str, str]]:
    """Extracts the username and password from the URL, if present, and returns the URL and the auth header."""
    parsed_url = urllib.parse.urlparse(url)

    auth_header: dict[str, str] = {}
    if parsed_url.username:
        # If the URL contains a username, we assume the user is trying to authenticate
        auth_header = _create_auth_header(user_env_var=parsed_url.username, pwd_env_var=parsed_url.password)
        # Remove the auth part from the URL
        url = parsed_url._replace(netloc=parsed_url.hostname or "").geturl()
    return url, auth_header


def _create_auth_header(user_env_var: str, pwd_env_var: Union[str, None] = None) -> dict[str, str]:
    """Creates the Authorization header for basic authentication."""
    user = _get_environment_variable(user_env_var)

    if pwd_env_var is None:
        # If password is not provided, we assume that the user is using a token
        log.debug("Using bearer token for authentication")
        return {"Authorization": f"Bearer {user}"}

    # Else, we assume that the user is using user:password
    pwd = _get_environment_variable(pwd_env_var)
    log.debug("Using basic authentication")
    credentials = base64.encodebytes(f"{user}:{pwd}".encode()).decode().strip()
    return {"Authorization": f"Basic {credentials}"}


def _get_environment_variable(env_var: str) -> str:
    """Extracts the environment variable name from env_var and returns its value."""
    match = ENV_VAR_PATTERN.match(env_var)
    if not match:
        raise ValueError("URL authentication must be specified as environment variables")

    try:
        return os.environ[match.group(1)]
    except KeyError as exc:
        raise ValueError(f"Environment variable '{match.group(1)}' is not set") from exc


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
                        log.debug(f"Using cached '{path}' for '{url}'")
                        return f.read()
        except (OSError, ValueError) as e:
            log.debug(f"{type(e).__name__}: {e}")

    # Download and cache the file
    log.debug(f"Downloading '{url}' to '{path}'")
    content = download(url)
    os.makedirs(directory, exist_ok=True)
    with click.open_file(path, "wb", atomic=True) as f:
        f.write(b"%s%d\n" % (prefix, now))
        f.write(content)
    return content
