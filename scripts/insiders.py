# Functions related to Insiders funding goals.

from __future__ import annotations

import json
import logging
import os
import posixpath
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, cast
from urllib.error import HTTPError
from urllib.parse import urljoin
from urllib.request import urlopen

import yaml

if TYPE_CHECKING:
    from collections.abc import Iterable

logger = logging.getLogger(f"mkdocs.logs.{__name__}")


def human_readable_amount(amount: int) -> str:
    str_amount = str(amount)
    if len(str_amount) >= 4:  # noqa: PLR2004
        return f"{str_amount[: len(str_amount) - 3]},{str_amount[-3:]}"
    return str_amount


@dataclass
class Project:
    name: str
    url: str


@dataclass
class Feature:
    name: str
    ref: str | None
    since: date | None
    project: Project | None

    def url(self, rel_base: str = "..") -> str | None:  # noqa: D102
        if not self.ref:
            return None
        if self.project:
            rel_base = self.project.url
        return posixpath.join(rel_base, self.ref.lstrip("/"))

    def render(self, rel_base: str = "..", *, badge: bool = False) -> None:  # noqa: D102
        new = ""
        if badge:
            recent = self.since and date.today() - self.since <= timedelta(days=60)  # noqa: DTZ011
            if recent:
                ft_date = self.since.strftime("%B %d, %Y")  # type: ignore[union-attr]
                new = f' :material-alert-decagram:{{ .new-feature .vibrate title="Added on {ft_date}" }}'
        project = f"[{self.project.name}]({self.project.url}) — " if self.project else ""
        feature = f"[{self.name}]({self.url(rel_base)})" if self.ref else self.name
        print(f"- [{'x' if self.since else ' '}] {project}{feature}{new}")


@dataclass
class Goal:
    name: str
    amount: int
    features: list[Feature]
    complete: bool = False

    @property
    def human_readable_amount(self) -> str:  # noqa: D102
        return human_readable_amount(self.amount)

    def render(self, rel_base: str = "..") -> None:  # noqa: D102
        print(f"#### $ {self.human_readable_amount} — {self.name}\n")
        if self.features:
            for feature in self.features:
                feature.render(rel_base)
            print("")
        else:
            print("There are no features in this goal for this project.  ")
            print(
                "[See the features in this goal **for all Insiders projects.**]"
                f"(https://pawamoy.github.io/insiders/#{self.amount}-{self.name.lower().replace(' ', '-')})",
            )


def load_goals(data: str, funding: int = 0, project: Project | None = None) -> dict[int, Goal]:
    goals_data = yaml.safe_load(data)["goals"]
    return {
        amount: Goal(
            name=goal_data["name"],
            amount=amount,
            complete=funding >= amount,
            features=[
                Feature(
                    name=feature_data["name"],
                    ref=feature_data.get("ref"),
                    since=feature_data.get("since") and datetime.strptime(feature_data["since"], "%Y/%m/%d").date(),  # noqa: DTZ007
                    project=project,
                )
                for feature_data in goal_data["features"]
            ],
        )
        for amount, goal_data in goals_data.items()
    }


def _load_goals_from_disk(path: str, funding: int = 0) -> dict[int, Goal]:
    project_dir = os.getenv("MKDOCS_CONFIG_DIR", ".")
    try:
        data = Path(project_dir, path).read_text()
    except OSError as error:
        raise RuntimeError(f"Could not load data from disk: {path}") from error
    return load_goals(data, funding)


def _load_goals_from_url(source_data: tuple[str, str, str], funding: int = 0) -> dict[int, Goal]:
    project_name, project_url, data_fragment = source_data
    data_url = urljoin(project_url, data_fragment)
    try:
        with urlopen(data_url) as response:  # noqa: S310
            data = response.read()
    except HTTPError as error:
        raise RuntimeError(f"Could not load data from network: {data_url}") from error
    return load_goals(data, funding, project=Project(name=project_name, url=project_url))


def _load_goals(source: str | tuple[str, str, str], funding: int = 0) -> dict[int, Goal]:
    if isinstance(source, str):
        return _load_goals_from_disk(source, funding)
    return _load_goals_from_url(source, funding)


def funding_goals(source: str | list[str | tuple[str, str, str]], funding: int = 0) -> dict[int, Goal]:
    if isinstance(source, str):
        return _load_goals_from_disk(source, funding)
    goals = {}
    for src in source:
        source_goals = _load_goals(src, funding)
        for amount, goal in source_goals.items():
            if amount not in goals:
                goals[amount] = goal
            else:
                goals[amount].features.extend(goal.features)
    return {amount: goals[amount] for amount in sorted(goals)}


def feature_list(goals: Iterable[Goal]) -> list[Feature]:
    return list(chain.from_iterable(goal.features for goal in goals))


def load_json(url: str) -> str | list | dict:
    with urlopen(url) as response:  # noqa: S310
        return json.loads(response.read().decode())


data_source = globals()["data_source"]
sponsor_url = "https://github.com/sponsors/pawamoy"
data_url = "https://raw.githubusercontent.com/pawamoy/sponsors/main"
numbers: dict[str, int] = load_json(f"{data_url}/numbers.json")  # type: ignore[assignment]
sponsors: list[dict] = load_json(f"{data_url}/sponsors.json")  # type: ignore[assignment]
current_funding = numbers["total"]
sponsors_count = numbers["count"]
goals = funding_goals(data_source, funding=current_funding)
ongoing_goals = [goal for goal in goals.values() if not goal.complete]
unreleased_features = sorted(
    (ft for ft in feature_list(ongoing_goals) if ft.since),
    key=lambda ft: cast("date", ft.since),
    reverse=True,
)
