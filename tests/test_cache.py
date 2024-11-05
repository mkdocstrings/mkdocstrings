"""Tests for the internal mkdocstrings _cache module."""

from __future__ import annotations

import pytest

from mkdocstrings import _cache


@pytest.mark.parametrize(
    ("url", "expected_url"),
    [
        ("http://host/path", "http://host/path"),
        ("http://username:password@host/path", "http://host/path"),
        ("http://token@host/path", "http://host/path"),
    ],
)
def test_extract_auth_from_url(monkeypatch: pytest.MonkeyPatch, url: str, expected_url: str) -> None:
    """Test extracting the auth part from the URL."""
    monkeypatch.setattr(_cache, "_create_auth_header", lambda *args, **kwargs: {})
    result_url, _result_auth_header = _cache._extract_auth_from_url(url)
    assert result_url == expected_url


def test_create_auth_header_basic_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test creating the Authorization header for basic authentication."""
    monkeypatch.setenv("MY_USERNAME", "user123")
    monkeypatch.setenv("MY_PASSWORD", "pass456")

    auth_header = _cache._create_auth_header(user_env_var="$MY_USERNAME", pwd_env_var="$MY_PASSWORD")  # noqa: S106
    assert auth_header == {"Authorization": "Basic user123:pass456"}


def test_create_auth_header_bearer_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test creating the Authorization header for bearer token authentication."""
    monkeypatch.setenv("MY_TOKEN", "token123")

    auth_header = _cache._create_auth_header(user_env_var="$MY_TOKEN")
    assert auth_header == {"Authorization": "Bearer token123"}


@pytest.mark.parametrize(
    ("env_var", "value"),
    [
        ("$MY_USERNAME", "some_user"),
    ],
)
def test_get_environment_variable_valid(monkeypatch: pytest.MonkeyPatch, env_var: str, value: str) -> None:
    """Test getting an environment variable."""
    monkeypatch.setenv(env_var.replace("$", ""), value)
    result_value = _cache._get_environment_variable(env_var)
    assert result_value == value


def test_get_environment_variable_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that an exception is raised when the environment variable is not set."""
    env_var = "MY_USERNAME"
    monkeypatch.delenv(f"{env_var}", raising=False)
    with pytest.raises(ValueError, match=r"Environment variable .*? is not set"):
        _cache._get_environment_variable(f"${env_var}")


@pytest.mark.parametrize(
    ("var", "match"),
    [
        ("$var", "var"),
        ("$VAR", "VAR"),
        ("$_VAR", "_VAR"),
        ("$VAR123", "VAR123"),
        ("$VAR123_", "VAR123_"),
        ("VAR", None),
        ("$1VAR", None),
    ],
)
def test_env_var_pattern(var: str, match: str | None) -> None:
    """Test the environment variable regex pattern."""
    _match = _cache.ENV_VAR_PATTERN.match(var)
    if _match is None:
        assert match is _match
    else:
        assert _match.group(1) == match
