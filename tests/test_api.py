"""Tests for our own API exposition."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

import griffe
import pytest

import mkdocstrings
from mkdocstrings import Inventory

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture(name="loader", scope="module")
def _fixture_loader() -> griffe.GriffeLoader:
    loader = griffe.GriffeLoader()
    loader.load("mkdocstrings")
    loader.resolve_aliases()
    return loader


@pytest.fixture(name="internal_api", scope="module")
def _fixture_internal_api(loader: griffe.GriffeLoader) -> griffe.Module:
    return loader.modules_collection["mkdocstrings._internal"]


@pytest.fixture(name="public_api", scope="module")
def _fixture_public_api(loader: griffe.GriffeLoader) -> griffe.Module:
    return loader.modules_collection["mkdocstrings"]


def _yield_public_objects(
    obj: griffe.Module | griffe.Class,
    *,
    modules: bool = False,
    modulelevel: bool = True,
    inherited: bool = False,
    special: bool = False,
) -> Iterator[griffe.Object | griffe.Alias]:
    for member in obj.all_members.values() if inherited else obj.members.values():
        try:
            if member.is_module:
                if member.is_alias or not member.is_public:
                    continue
                if modules:
                    yield member
                yield from _yield_public_objects(
                    member,  # type: ignore[arg-type]
                    modules=modules,
                    modulelevel=modulelevel,
                    inherited=inherited,
                    special=special,
                )
            elif member.is_public and (special or not member.is_special):
                yield member
            else:
                continue
            if member.is_class and not modulelevel:
                yield from _yield_public_objects(
                    member,  # type: ignore[arg-type]
                    modules=modules,
                    modulelevel=False,
                    inherited=inherited,
                    special=special,
                )
        except (griffe.AliasResolutionError, griffe.CyclicAliasError):
            continue


@pytest.fixture(name="modulelevel_internal_objects", scope="module")
def _fixture_modulelevel_internal_objects(internal_api: griffe.Module) -> list[griffe.Object | griffe.Alias]:
    return list(_yield_public_objects(internal_api, modulelevel=True))


@pytest.fixture(name="internal_objects", scope="module")
def _fixture_internal_objects(internal_api: griffe.Module) -> list[griffe.Object | griffe.Alias]:
    return list(_yield_public_objects(internal_api, modulelevel=False, special=True))


@pytest.fixture(name="public_objects", scope="module")
def _fixture_public_objects(public_api: griffe.Module) -> list[griffe.Object | griffe.Alias]:
    return list(_yield_public_objects(public_api, modulelevel=False, inherited=True, special=True))


@pytest.fixture(name="inventory", scope="module")
def _fixture_inventory() -> Inventory:
    inventory_file = Path(__file__).parent.parent / "site" / "objects.inv"
    if not inventory_file.exists():
        raise pytest.skip("The objects inventory is not available.")
    with inventory_file.open("rb") as file:
        return Inventory.parse_sphinx(file)


def test_exposed_objects(modulelevel_internal_objects: list[griffe.Object | griffe.Alias]) -> None:
    """All public objects in the internal API are exposed under `mkdocstrings`."""
    not_exposed = [
        obj.path
        for obj in modulelevel_internal_objects
        if obj.name not in mkdocstrings.__all__ or not hasattr(mkdocstrings, obj.name)
    ]
    assert not not_exposed, "Objects not exposed:\n" + "\n".join(sorted(not_exposed))


def test_unique_names(modulelevel_internal_objects: list[griffe.Object | griffe.Alias]) -> None:
    """All internal objects have unique names."""
    names_to_paths = defaultdict(list)
    for obj in modulelevel_internal_objects:
        names_to_paths[obj.name].append(obj.path)
    non_unique = [paths for paths in names_to_paths.values() if len(paths) > 1]
    assert not non_unique, "Non-unique names:\n" + "\n".join(str(paths) for paths in non_unique)


def test_single_locations(public_api: griffe.Module) -> None:
    """All objects have a single public location."""

    def _public_path(obj: griffe.Object | griffe.Alias) -> bool:
        return obj.is_public and (obj.parent is None or _public_path(obj.parent))

    multiple_locations = {}
    for obj_name in mkdocstrings.__all__:
        obj = public_api[obj_name]
        if obj.aliases and (
            public_aliases := [path for path, alias in obj.aliases.items() if path != obj.path and _public_path(alias)]
        ):
            multiple_locations[obj.path] = public_aliases
    assert not multiple_locations, "Multiple public locations:\n" + "\n".join(
        f"{path}: {aliases}" for path, aliases in multiple_locations.items()
    )


def test_api_matches_inventory(inventory: Inventory, public_objects: list[griffe.Object | griffe.Alias]) -> None:
    """All public objects are added to the inventory."""
    ignore_names = {"__getattr__", "__init__", "__repr__", "__str__", "__post_init__"}
    not_in_inventory = [
        obj.path for obj in public_objects if obj.name not in ignore_names and obj.path not in inventory
    ]
    msg = "Objects not in the inventory (try running `make run mkdocs build`):\n{paths}"
    assert not not_in_inventory, msg.format(paths="\n".join(sorted(not_in_inventory)))


def test_inventory_matches_api(
    inventory: Inventory,
    public_objects: list[griffe.Object | griffe.Alias],
    loader: griffe.GriffeLoader,
) -> None:
    """The inventory doesn't contain any additional Python object."""
    not_in_api = []
    # YORE: Bump 1: Remove line.
    deprecated_modules = {"extension", "handlers", "inventory", "loggers", "plugin"}
    public_api_paths = {obj.path for obj in public_objects}
    public_api_paths.add("mkdocstrings")
    for item in inventory.values():
        if (
            item.domain == "py"
            and "(" not in item.name
            and (item.name == "mkdocstrings" or item.name.startswith("mkdocstrings."))
        ):
            obj = loader.modules_collection[item.name]
            # YORE: Bump 1: Remove block.
            if any(obj.path.startswith(f"mkdocstrings.{module}") for module in deprecated_modules):
                continue

            if obj.path not in public_api_paths and not any(path in public_api_paths for path in obj.aliases):
                not_in_api.append(item.name)
    msg = "Inventory objects not in public API (try running `make run mkdocs build`):\n{paths}"
    assert not not_in_api, msg.format(paths="\n".join(sorted(not_in_api)))


def test_no_module_docstrings_in_internal_api(internal_api: griffe.Module) -> None:
    """No module docstrings should be written in our internal API.

    The reasoning is that docstrings are addressed to users of the public API,
    but internal modules are not exposed to users, so they should not have docstrings.
    """

    def _modules(obj: griffe.Module) -> Iterator[griffe.Module]:
        for member in obj.modules.values():
            yield member
            yield from _modules(member)

    for obj in _modules(internal_api):
        assert not obj.docstring
