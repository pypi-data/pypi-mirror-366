# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import matplotlib

# avoids loading X11-dependent backends
matplotlib.use("agg")

import matplotlib.axes
import matplotlib.figure
import numpy
import pytest

from fairical import plot
from fairical.solutions import Solutions
from fairical.utils import IndicatorType


def test_radar_chart_output_type() -> None:
    indicators: dict[str, dict[IndicatorType, float]] = {
        "System 1": {
            "hv": 0.8,
            "ud": 0.3,
            "as": 0.4,
            "onvg": 10,
            "onvgr": 0.7,
            "relative-onvg": 4,
        },
        "System 2": {
            "hv": 0.6,
            "ud": 0.4,
            "as": 0.2,
            "onvg": 12,
            "onvgr": 0.8,
            "relative-onvg": 5,
        },
    }

    # radar_chart expects axes_keys to be subset of keys in dicts
    fig, ax = plot.radar_chart(indicators)
    assert isinstance(fig, matplotlib.figure.Figure)
    assert isinstance(ax, matplotlib.axes.Axes)


def test_radar_chart_exceptions() -> None:
    indicators: dict[str, dict[IndicatorType, float]] = {
        "System 1": {
            "hv": 0.8,
            "ud": 0.3,
            "as": 0.4,
            "onvg": 10,
            "onvgr": 0.7,
            "relative-onvg": 4,
        },
    }

    # axes too short
    with pytest.raises(AssertionError):
        plot.radar_chart(indicators, axes={"hv": ""})

    # invalid axes keys
    with pytest.raises(ValueError):
        plot.radar_chart(indicators, axes={"hv": "", "os": "", "foobar": ""})


def test_pareto_plot_errors() -> None:
    rng = numpy.random.default_rng()
    nds = Solutions.fromarray(rng.random((3, 1)), ("eod+race",))
    ds = Solutions.fromarray(rng.random((2, 1)), ("eod+race",))

    solutions = {"System 1": (nds, ds)}

    with pytest.raises(AssertionError):
        plot.pareto_plot(solutions, axes_labels={"acc": ""})


def test_pareto_2d_plot() -> None:
    rng = numpy.random.default_rng()

    solutions = {
        "System 1": (
            Solutions.fromarray(rng.random((3, 2)), ("eod+race", "acc")),
            Solutions.fromarray(rng.random((2, 2)), ("eod+race", "acc")),
        ),
        "System 2": (
            Solutions.fromarray(rng.random((3, 2)), ("eod+race", "acc")),
            Solutions.fromarray(rng.random((2, 2)), ("eod+race", "acc")),
        ),
    }

    fig, ax = plot.pareto_plot(
        solutions, axes_labels={"eod+race": "Race", "acc": "Acc"}
    )
    assert isinstance(fig, matplotlib.figure.Figure)
    assert isinstance(ax, matplotlib.axes.Axes)


def test_pareto_3d_plot() -> None:
    rng = numpy.random.default_rng()

    solutions = {
        "System 1": (
            Solutions.fromarray(rng.random((3, 3)), ("eod+race", "eod+age", "acc")),
            Solutions.fromarray(rng.random((2, 3)), ("eod+race", "eod+age", "acc")),
        ),
        "System 2": (
            Solutions.fromarray(rng.random((3, 3)), ("eod+race", "eod+age", "acc")),
            Solutions.fromarray(rng.random((2, 3)), ("eod+race", "eod+age", "acc")),
        ),
    }

    fig, ax = plot.pareto_plot(
        solutions, axes_labels={"eod+race": "Race", "eod+age": "Age", "acc": "Acc"}
    )
    assert isinstance(fig, matplotlib.figure.Figure)
    assert isinstance(ax, matplotlib.axes.Axes)
