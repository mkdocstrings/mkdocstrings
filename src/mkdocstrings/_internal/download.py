import base64
import gzip
import os
import re
import urllib.parse
import urllib.request
from collections.abc import Mapping
from typing import BinaryIO, Optional

from mkdocstrings._internal.loggers import get_logger

_logger = get_logger("mkdocstrings")

# Regex pattern for an environment variable in the form ${ENV_VAR}.
_ENV_VAR_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def _download_url_with_gz(url: str) -> bytes:
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
            _logger.warning(
                "Environment variable '%s' is not set, but is used in inventory URL %s",
                match.group(1),
                url,
            )
            return match.group(0)

    return re.sub(_ENV_VAR_PATTERN, replace_func, credential)


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
        _logger.debug("Using bearer token authentication for %s", url)
        return {"Authorization": f"Bearer {credential}"}

    # Else, we assume that the user is using user:password.
    user, pwd = credential.split(":", 1)
    _logger.debug("Using basic authentication for %s", url)
    credentials = base64.encodebytes(f"{user}:{pwd}".encode()).decode().strip()
    return {"Authorization": f"Basic {credentials}"}
