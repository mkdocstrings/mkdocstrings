import datetime
import gzip
import hashlib
import os
import urllib.parse
import urllib.request
from typing import BinaryIO, Callable

import click
import platformdirs

from mkdocstrings.loggers import get_logger

log = get_logger(__name__)


def download_url_with_gz(url: str) -> bytes:
    req = urllib.request.Request(  # noqa: S310
        url,
        headers={"Accept-Encoding": "gzip", "User-Agent": "mkdocstrings/0.15.0"},
    )
    with urllib.request.urlopen(req) as resp:  # noqa: S310
        content: BinaryIO = resp
        if "gzip" in resp.headers.get("content-encoding", ""):
            content = gzip.GzipFile(fileobj=resp)  # type: ignore[assignment]
        return content.read()


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
