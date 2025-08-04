# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib
import typing

import numpy
import pytest

from fairical.scores import Scores
from fairical.solutions import Solutions
from fairical.utils import IndicatorType


@pytest.mark.parametrize(
    "system",
    [
        ("empirical"),
        ("sample"),
    ],
    ids=lambda x: str(x),  # just changes how pytest prints it
)
def test_scores_case(
    datadir: pathlib.Path,
    system: str,
) -> None:
    thresholds = typing.cast(list[float], list(numpy.linspace(0, 1, 5, dtype=float)))

    data = Scores.load(datadir / "data" / system / "system_1.json")
    indicators = (
        data.solutions(
            ["eod+race", "minmaxr+roc_auc+gender", "acc"], thresholds=thresholds
        )
        .deduplicate()
        .indicators()
    )

    assert isinstance(indicators, dict)
    assert len(indicators.keys()) == 6

    for ind in [
        # "onvg", >> 1
        "onvgr",
        # "relative-onvg",
        "ud",
        # "complement-ud",
        "os",
        "as",
        "hv",
        # "area",
    ]:
        assert ind in indicators
        assert 0.0 <= indicators[typing.cast(IndicatorType, ind)] <= 1.0
    assert indicators["onvg"] >= 1


@pytest.mark.parametrize(
    "system",
    [
        ("uc-1"),
        ("uc-2"),
        ("uc-3"),
    ],
    ids=lambda x: str(x),  # just changes how pytest prints it
)
def test_solutions_case(
    datadir: pathlib.Path,
    system: str,
) -> None:
    data = Solutions.load(datadir / "data" / system / "system_1.json")
    indicators = data.indicators()

    assert isinstance(indicators, dict)
    assert len(indicators.keys()) == 6

    for ind in [
        # "onvg", >> 1
        "onvgr",
        # "relative-onvg",
        "ud",
        # "complement-ud",
        "os",
        "as",
        "hv",
        # "area",
    ]:
        assert ind in indicators
        assert 0.0 <= indicators[typing.cast(IndicatorType, ind)] <= 1.0
    assert indicators["onvg"] >= 1
