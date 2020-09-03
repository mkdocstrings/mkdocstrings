"""Tests for the references module."""
import pytest

from mkdocstrings.references import relative_url


@pytest.mark.parametrize(
    "current_url, to_url, result",
    (
        ("a", "a#b", "#b"),
        ("a", "a/b#c", "b#c"),
        ("a/b", "a/b#c", "#c"),
        ("a/b", "a/c#d", "../c#d"),
        ("a/b", "a#c", "..#c"),
        ("a/b/c", "d#e", "../../../d#e"),
        ("a/b", "c/d/#e", "../../c/d/#e"),
    ),
)
def test_relative_url(current_url, to_url, result):
    """Compute relative URLs correctly."""
    assert relative_url(current_url, to_url) == result
