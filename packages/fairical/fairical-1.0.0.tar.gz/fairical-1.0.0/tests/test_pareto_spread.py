# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy
import numpy.typing
import pytest

from fairical.solutions import Solutions


@pytest.mark.parametrize(
    "solutions, metrics, manual, tol",
    [
        (
            # 2d case with mininimisation and maximisation
            # note: [0.4, 0.6] is dominated by the other 2 points
            [[0.2, 0.8], [0.4, 0.6], [0.3, 0.9]],
            ("eod+race", "acc"),
            0.01,
            0.001,
        ),
        (
            # 3d case with mininimisation and maximisation
            [[0.3, 0.5, 0.9], [0.1, 0.9, 0.6], [0.2, 0.1, 0.3]],
            ("eod+race", "eod+age", "acc"),
            0.096,
            0.001,
        ),
        (
            # 2d case with no spread
            [[0.5, 0.5], [0.5, 0.5]],
            ("eod+race", "acc"),
            0.0,
            0.001,
        ),
        (
            # 2d case with maximum spread
            [[0.0, 0.0], [1.0, 1.0]],
            ("eod+race", "acc"),
            1.0,
            0.001,
        ),
    ],
)
def test_os(
    solutions: numpy.typing.ArrayLike, metrics: tuple[str], manual: float, tol: float
) -> None:
    """A valid system with three points."""

    sol = Solutions.fromarray(solutions, metrics)
    ind = sol.indicators()
    assert numpy.isclose(ind["os"], manual, tol)


@pytest.mark.parametrize(
    "solutions, metrics, manual, tol",
    [
        (
            # 2d case with mininimisation and maximisation
            # note: [0.4, 0.6] is dominated by the other 2 points
            [[0.2, 0.8], [0.4, 0.6], [0.3, 0.9]],
            ("eod+race", "acc"),
            0.1,
            0.001,
        ),
        (
            # 3d case with mininimisation and maximisation
            [[0.3, 0.5, 0.9], [0.1, 0.9, 0.6], [0.2, 0.1, 0.3]],
            ("eod+race", "eod+age", "acc"),
            0.533333,
            0.001,
        ),
        (
            # 2d case with no spread
            [[0.5, 0.5], [0.5, 0.5]],
            ("eod+race", "acc"),
            0.0,
            0.001,
        ),
        (
            # 2d case with maximum spread
            [[0.0, 0.0], [1.0, 1.0]],
            ("eod+race", "acc"),
            1.0,
            0.001,
        ),
    ],
)
def test_as(
    solutions: numpy.typing.ArrayLike, metrics: tuple[str], manual: float, tol: float
) -> None:
    """A valid system with three points."""

    sol = Solutions.fromarray(solutions, metrics)
    ind = sol.indicators()
    assert numpy.isclose(ind["as"], manual, tol)
