"""Tests for the handlers.python module."""

from copy import deepcopy

from mkdocstrings.handlers.python import (  # noqa: WPS450
    _sort_key_alphabetical,
    _sort_key_source,
    rebuild_category_lists,
    sort_object,
)


def test_members_order():
    """Assert that members sorting functions work correctly."""
    subcategories = {key: [] for key in ("attributes", "classes", "functions", "methods", "modules")}
    categories = {"children": {}, **subcategories}
    collected = {
        "name": "root",
        "children": {
            "b": {"name": "b", "source": {"line_start": 0}, **categories},
            "a": {"name": "a", **categories},
            "z": {"name": "z", "source": {"line_start": 100}, **categories},
            "no_name": {"source": {"line_start": 10}, **categories},
            "c": {
                "name": "c",
                "source": {"line_start": 30},
                "children": {
                    "z": {"name": "z", "source": {"line_start": 200}, **categories},
                    "a": {"name": "a", "source": {"line_start": 20}, **categories},
                },
                **subcategories,
            },
        },
        "attributes": ["b", "c", "no_name", "z", "a"],
        "classes": [],
        "functions": [],
        "methods": [],
        "modules": [],
    }
    rebuild_category_lists(collected)
    alphebetical = deepcopy(collected)
    sort_object(alphebetical, _sort_key_alphabetical)

    rebuilt_categories = {"children": [], **subcategories}
    assert (
        alphebetical["children"]
        == alphebetical["attributes"]
        == [
            {"name": "a", **rebuilt_categories},
            {"name": "b", "source": {"line_start": 0}, **rebuilt_categories},
            {
                "name": "c",
                "source": {"line_start": 30},
                "children": [
                    {"name": "a", "source": {"line_start": 20}, **rebuilt_categories},
                    {"name": "z", "source": {"line_start": 200}, **rebuilt_categories},
                ],
                **subcategories,
            },
            {"name": "z", "source": {"line_start": 100}, **rebuilt_categories},
            {"source": {"line_start": 10}, **rebuilt_categories},
        ]
    )

    source = deepcopy(collected)
    sort_object(source, _sort_key_source)

    assert (
        source["children"]
        == source["attributes"]
        == [
            {"name": "a", **rebuilt_categories},
            {"name": "b", "source": {"line_start": 0}, **rebuilt_categories},
            {"source": {"line_start": 10}, **rebuilt_categories},
            {
                "name": "c",
                "source": {"line_start": 30},
                "children": [
                    {"name": "a", "source": {"line_start": 20}, **rebuilt_categories},
                    {"name": "z", "source": {"line_start": 200}, **rebuilt_categories},
                ],
                **subcategories,
            },
            {"name": "z", "source": {"line_start": 100}, **rebuilt_categories},
        ]
    )
