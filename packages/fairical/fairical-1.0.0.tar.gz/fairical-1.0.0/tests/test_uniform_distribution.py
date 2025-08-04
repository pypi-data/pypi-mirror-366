# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy
import pytest

from fairical.solutions import _uniform_distribution as ud


def test_ud_perfectly_uniform() -> None:
    """Three points that are evenly spaced inside radius."""
    pts = numpy.array([[0.0, 0.0], [0.005, 0.0], [0.01, 0.0]])
    result = ud(pts, shared_dist=0.01)
    assert 0 < result <= 1
    assert numpy.isclose(result, 0.63, 0.01)


def test_ud_single_point() -> None:
    """Single point."""
    pts = numpy.array([[0.0, 0.0]])
    assert numpy.isclose(ud(pts), 1.0)  # No deviation with 1 point


def test_ud_two_points_within_radius() -> None:
    """Two points inside radius."""
    pts = numpy.array([[0.0, 0.0], [0.005, 0.0]])
    assert numpy.isclose(
        ud(pts, shared_dist=0.01), 1.0
    )  # Niche counts are same (1 each), so std = 0


def test_ud_two_points_outside_radius() -> None:
    """Two points outside radius."""
    pts = numpy.array([[0.0, 0.0], [1.0, 1.0]])
    assert numpy.isclose(
        ud(pts, shared_dist=0.01), 1.0
    )  # Both have 0 neighbors, std = 0


def test_ud_non_uniform_distribution() -> None:
    """Three points as non uniformly distributed."""
    pts = numpy.array([[0, 0], [0.001, 0.0], [1, 1]])
    assert 0 < ud(pts, shared_dist=0.01) < 1  # Non-uniform distribution


def test_ud_empty_input() -> None:
    """Empty input."""
    pts = numpy.empty((0, 2))
    assert ud(pts) == 1.0  # The worst case ending up with full non-uniformity.


@pytest.mark.parametrize(
    "pts",
    [
        (numpy.array([1.0, 2.0, 3.0])),  # 1-D
        (numpy.ones((2, 2, 2))),  # 3-D
    ],
)
def test_ud_invalid_shape_raises(pts: numpy.ndarray) -> None:
    """Invalid input in 1-D and 3-D."""
    with pytest.raises(ValueError):
        ud(pts)
