"""Tests for the internal mkdocstrings _download module."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest

from mkdocstrings._internal import download

if TYPE_CHECKING:
    from collections.abc import Mapping


@pytest.mark.parametrize(
    ("credential", "expected", "env"),
    [
        ("USER", "USER", {"USER": "testuser"}),
        ("$USER", "$USER", {"USER": "testuser"}),
        ("${USER", "${USER", {"USER": "testuser"}),
        ("$USER}", "$USER}", {"USER": "testuser"}),
        ("${TOKEN}", "testtoken", {"TOKEN": "testtoken"}),
        ("${USER}:${PASSWORD}", "${USER}:testpass", {"PASSWORD": "testpass"}),
        ("${USER}:${PASSWORD}", "testuser:testpass", {"USER": "testuser", "PASSWORD": "testpass"}),
        (
            "user_prefix_${USER}_user_$uffix:pwd_prefix_${PASSWORD}_pwd_${uffix",
            "user_prefix_testuser_user_$uffix:pwd_prefix_testpass_pwd_${uffix",
            {"USER": "testuser", "PASSWORD": "testpass"},
        ),
    ],
)
def test_expand_env_vars(credential: str, expected: str, env: Mapping[str, str]) -> None:
    """Test expanding environment variables."""
    assert download._expand_env_vars(credential, url="https://test.example.com", env=env) == expected


def test_expand_env_vars_with_missing_env_var(caplog: pytest.LogCaptureFixture) -> None:
    """Test expanding environment variables with a missing environment variable."""
    caplog.set_level(logging.WARNING, logger="mkdocs.plugins.mkdocstrings._download")

    credential = "${USER}"
    env: dict[str, str] = {}
    assert download._expand_env_vars(credential, url="https://test.example.com", env=env) == "${USER}"

    output = caplog.records[0].getMessage()
    assert "'USER' is not set" in output


@pytest.mark.parametrize(
    ("url", "expected_url"),
    [
        ("http://host/path", "http://host/path"),
        ("http://token@host/path", "http://host/path"),
        ("http://${token}@host/path", "http://host/path"),
        ("http://username:password@host/path", "http://host/path"),
        ("http://username:${PASSWORD}@host/path", "http://host/path"),
        ("http://${USERNAME}:${PASSWORD}@host/path", "http://host/path"),
        ("http://prefix${USERNAME}suffix:prefix${PASSWORD}suffix@host/path", "http://host/path"),
    ],
)
def test_extract_auth_from_url(monkeypatch: pytest.MonkeyPatch, url: str, expected_url: str) -> None:
    """Test extracting the auth part from the URL."""
    monkeypatch.setattr(download, "_create_auth_header", lambda *args, **kwargs: {})
    result_url, _result_auth_header = download._extract_auth_from_url(url)
    assert result_url == expected_url


def test_create_auth_header_basic_auth() -> None:
    """Test creating the Authorization header for basic authentication."""
    auth_header = download._create_auth_header(credential="testuser:testpass", url="https://test.example.com")
    assert auth_header == {"Authorization": "Basic dGVzdHVzZXI6dGVzdHBhc3M="}


def test_create_auth_header_bearer_auth() -> None:
    """Test creating the Authorization header for bearer token authentication."""
    auth_header = download._create_auth_header(credential="token123", url="https://test.example.com")
    assert auth_header == {"Authorization": "Bearer token123"}


@pytest.mark.parametrize(
    ("var", "match"),
    [
        ("${var}", "var"),
        ("${VAR}", "VAR"),
        ("${_}", "_"),
        ("${_VAR}", "_VAR"),
        ("${VAR123}", "VAR123"),
        ("${VAR123_}", "VAR123_"),
        ("VAR", None),
        ("$1VAR", None),
        ("${1VAR}", None),
        ("${}", None),
        ("${ }", None),
    ],
)
def test_env_var_pattern(var: str, match: str | None) -> None:
    """Test the environment variable regex pattern."""
    _match = download._ENV_VAR_PATTERN.match(var)
    if _match is None:
        assert match is _match
    else:
        assert _match.group(1) == match
