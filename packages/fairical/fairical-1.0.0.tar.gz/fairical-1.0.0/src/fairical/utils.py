# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared utilities."""

import typing

import numpy
import tabulate

IndicatorType: typing.TypeAlias = typing.Literal[
    "hv",  # Hypervolume
    "ud",  # Uniform Distribution
    "os",  # Overall Pareto Spread
    "as",  # Average Pareto Spread
    "onvg",  # Overall Nondominated Vector Generation
    "onvgr",  # Overall Nondominated Vector Generation Ratio
    "relative-onvg",  # Relative ONVG
    "area",  # Radar chart area
]
"""Supported indicators type for pareto front estimates."""


def parse_indicator(ind: str | IndicatorType) -> IndicatorType:
    """Parse indicator from string.

    Parameters
    ----------
    ind
        Indicator prototype to parse.

    Returns
    -------
        Parsed indicator value.
    """
    allowed = typing.get_args(IndicatorType)

    if ind not in allowed:
        raise ValueError(f"Unknown indicator type: {ind!r}.  Must be one of {allowed}")

    return typing.cast(IndicatorType, ind)


def normalize_onvg(values: list[int]) -> list[float]:
    """Normalize ONVG indicators so range is :math:`[0, 1]`.

    This function normalizes the ONVG indicators of multiple systems so that it
    represents a ratio between the original value and the maximum for all systems
    compared.

    Parameters
    ----------
    values
        The values of all ONVG indicators to normalize.

    Returns
    -------
        A new list containing the values of indicators divided by their maximum.
    """

    return [k / max(values) for k in values]


def normalized_radar_area(values: list[int | float], maximum: float = 1.0) -> float:
    r"""Evaluate the radar-chart area formed by indicators of interest.

    This method calculates the "normalized" area (value between :math:`[0, 1]`) of a
    radar chart formed by indicators listed in ``values``.

    An intuitive way to calculate the area of radar chart is to consider it as a set of
    triangles, defined by the chart axes and the angles between then, out of which you
    know the sizes of two sides, which are given, and the angle between them, which is
    fixed (:math:`2\pi/n`). For example, the area of a 3-way radar chart is therefore
    the total area of 3 triangles with sides equal to each combination of input
    ``values``, with angles of :math:`120^o`.  More generally, the total area can be
    defined as:

    .. math::

       \sum_i^n 0.5 a_i b_i \sin(2\pi/n)

    Where :math:`n` is the total number of axes on the radar chart, and `a_i` and `b_i`
    are the adjacent axes for which we are computing the section area. To normalize this
    such that all charts have a maximum area of 1.0, one must bind the maximum values in
    each of the radar chart axes.  In this implementation, we bind these maxima to 1.0.
    With that, one can compute the largest radar chart area and normalize the given area
    by that value.

    If one considers each triangle individually, it becomes clear that the factor
    :math:`0.5 \sin(2\pi/n)` cancels out and only :math:`a b / max^2` matters.
    This simplified version is implemented here for maximum accuracy and speed.

    Parameters
    ----------
    values
        The values of the radar chart plot. Naturally, at least 3 values must be
        provided.  All values are required to lie in the interval :math:`[0, 1]`.
    maximum
        The maximum value one can have in each axis of the radar chart.  This value is
        used to compute the normalization factor.

    Returns
    -------
        The "normalized" area (value between :math:`[0, 1]`) of a
        radar chart formed by indicators listed in ``values``.
    """

    def _norm_triangle_area(a, b):
        return a * b / (maximum**2)

    assert len(values) >= 3, "At least 3 values are required."
    assert all([0 <= k <= maximum for k in values])

    return sum(
        [_norm_triangle_area(*k) for k in zip(values, values[1:] + values[:1])]
    ) / len(values)


def extend_indicators(
    indicators: typing.Sequence[dict[IndicatorType, float]],
    radar_axes: typing.Sequence[IndicatorType] = [
        "relative-onvg",
        "onvgr",
        "ud",
        "as",
        "hv",
    ],
) -> None:
    """Extend indicators of each system with relative metrics.

    This method adds ``relative-onvg``, and relative radar chart area on ``area``.  The
    radar chart area is calculated based on the axes selected on ``radar_axes``.

    Note this function **modifies the indicator dictionaries in-place**.

    Parameters
    ----------
    indicators
        Indicators organized in a dictionary of dictionaries where keys represent the
        labels of each system, and values, dictionaries that represent indicators for
        that system with *at least* keys listed in ``table_keys``. We assume the
        following metrics are calculated for every system:

        * ``hv``: the pareto estimate hypervolume (float)
        * ``onvg``: the number of non-dominated solutions (int)
        * ``onvgr``: the ratio between the number of non-dominated solutions and the
          total number of solutions (int)
        * ``ud``: the uniformity of non-dominated solutions across the estimated front
          (float)
        * ``as``: the average spread of non-dominated solutions across the estimated
          front (float)

    radar_axes
        The indicator keys that will be used for estimating the normalized radar surface
        for each system.
    """

    ordered_onvg = [typing.cast(int, k["onvg"]) for k in indicators]
    for v, rel_onvg in zip(indicators, normalize_onvg(ordered_onvg)):
        v["relative-onvg"] = rel_onvg
        v["area"] = normalized_radar_area(
            [typing.cast(float, v[parse_indicator(k)]) for k in radar_axes]
        )


def make_table(
    indicators: dict[str, dict[IndicatorType, float]],
    table_keys: typing.Sequence[IndicatorType | str] = [
        "relative-onvg",
        "onvgr",
        "ud",
        "as",
        "hv",
    ],
    fmt: str = "simple",
) -> str:
    """Extract and format table from pre-computed evaluation data.

    Extracts elements from ``data`` that can be displayed on a
    terminal-style table, format, and return it.

    Parameters
    ----------
    indicators
        Indicators organized in a dictionary of dictionaries where keys represent the
        labels of each system, and values, dictionaries that represent indicators for
        that system with *at least* keys listed in ``table_keys``. We assume the
        following metrics are calculated for every system:

        * ``hv``: the pareto estimate hypervolume (float)
        * ``onvg``: the number of non-dominated solutions (int)
        * ``onvgr``: the ratio between the number of non-dominated solutions and the
          total number of solutions (int)
        * ``ud``: the uniformity of non-dominated solutions across the estimated front
          (float)
        * ``as``: the average spread of non-dominated solutions across the estimated
          front (float)

    table_keys
        The indicator keys that will be tabulated in the table.
    fmt
        One of the formats supported by `python-tabulate
        <https://pypi.org/project/tabulate/>`_. Default is "github".

    Returns
    -------
        A string representation of a table.
    """

    table_keys_ind: list[IndicatorType] = [parse_indicator(k) for k in table_keys]

    extend_indicators(list(indicators.values()), table_keys_ind)

    table_headers = ["System"] + [k.upper() for k in table_keys] + ["Area"]

    values = numpy.array(
        [[v[k] for k in table_keys_ind + ["area"]] for v in indicators.values()],
        dtype=float,
    )

    table_data = []
    for system_name, system_data in zip(indicators.keys(), values):
        table_data.append([system_name] + system_data.tolist())

    return tabulate.tabulate(
        table_data, table_headers, tablefmt=fmt, floatfmt=".2f", stralign="right"
    )
