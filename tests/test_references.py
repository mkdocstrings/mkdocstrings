"""Tests for the references module."""
import pytest
from bs4 import BeautifulSoup

from mkdocstrings.references import Placeholder, relative_url


@pytest.mark.parametrize(
    ("current_url", "to_url", "href_url"),
    [
        ("a/", "a#b", "#b"),
        ("a/", "a/b#c", "b#c"),
        ("a/b/", "a/b#c", "#c"),
        ("a/b/", "a/c#d", "../c#d"),
        ("a/b/", "a#c", "..#c"),
        ("a/b/c/", "d#e", "../../../d#e"),
        ("a/b/", "c/d/#e", "../../c/d/#e"),
        ("a/index.html", "a/index.html#b", "#b"),
        ("a/index.html", "a/b.html#c", "b.html#c"),
        ("a/b.html", "a/b.html#c", "#c"),
        ("a/b.html", "a/c.html#d", "c.html#d"),
        ("a/b.html", "a/index.html#c", "index.html#c"),
        ("a/b/c.html", "d.html#e", "../../d.html#e"),
        ("a/b.html", "c/d.html#e", "../c/d.html#e"),
        ("a/b/index.html", "a/b/c/d.html#e", "c/d.html#e"),
        ("", "#x", "#x"),
        ('a/', "#x", "../#x"),
        ('a/b.html', "#x", "../#x"),
        ("", "a/#x", "a/#x"),
        ("", "a/b.html#x", "a/b.html#x"),
    ],
)
def test_relative_url(current_url, to_url, href_url):
    """
    Compute relative URLs correctly.

    Arguments:
        current_url: The URL of the source page.
        to_url: The URL of the target page.
        href_url: The relative URL to put in the `href` HTML field.
    """
    assert relative_url(current_url, to_url) == href_url


@pytest.mark.parametrize("html", ["foo<code>code content</code>4"])
def test_placeholder(html):
    """
    Test the references "fixing" mechanism.

    Arguments:
        html: HTML contents in which to fix references.
    """
    placeholder = Placeholder()

    soup = BeautifulSoup(html, "html.parser")
    placeholder.replace_code_tags(soup)
    html_with_placeholders = str(soup).replace("code content", "should not be replaced")

    html_restored = placeholder.restore_code_tags(html_with_placeholders)
    assert html == html_restored
