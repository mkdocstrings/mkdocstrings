"""Tests for the handlers.python module."""

from mkdocstrings.handlers.python import _sort_key_alphabetical, _sort_key_source, sort_object


def test_members_order():
    """Assert that members sorting functions work correctly."""
    collected = {
        key: [
            {"name": "z", "source": {"line_start": 100}},
            {"name": "b", "source": {"line_start": 0}},
            {"source": {"line_start": 10}},
            {"name": "a"},
            {
                "name": "c",
                "source": {"line_start": 30},
                "children": [
                    {
                        {"name": "z", "source": {"line_start": 200}},
                        {"name": "a", "source": {"line_start": 20}},
                    }
                ],
            },
        ]
        for key in ("children", "attributes", "classes", "functions", "methods", "modules")
    }

    alphebetical = sort_object(collected, _sort_key_alphabetical)

    for category in ("children", "attributes", "classes", "functions", "methods", "modules"):
        assert alphebetical[category] == [
            {"name": "a"},
            {"name": "b", "source": {"line_start": 0}},
            {
                "name": "c",
                "source": {"line_start": 30},
                "children": [
                    {
                        {"name": "a", "source": {"line_start": 20}},
                        {"name": "z", "source": {"line_start": 200}},
                    }
                ],
            },
            {"name": "z", "source": {"line_start": 100}},
            {"source": {"line_start": 10}},
        ]

    source = sort_object(collected, _sort_key_source)

    for category in ("children", "attributes", "classes", "functions", "methods", "modules"):
        assert source[category] == [
            {"name": "a"},
            {"name": "b", "source": {"line_start": 0}},
            {"source": {"line_start": 10}},
            {
                "name": "c",
                "source": {"line_start": 30},
                "children": [
                    {
                        {"name": "a", "source": {"line_start": 20}},
                        {"name": "z", "source": {"line_start": 200}},
                    }
                ],
            },
            {"name": "z", "source": {"line_start": 100}},
        ]
