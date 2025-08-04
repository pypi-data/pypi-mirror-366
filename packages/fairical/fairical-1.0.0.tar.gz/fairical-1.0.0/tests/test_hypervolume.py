# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy
import pytest

from fairical.solutions import _hypervolume as hv


def _manual_hv_2d(points: numpy.ndarray, ref: numpy.ndarray) -> float:
    """Compute 2‑D hyper‑volume manually for small sets (helper)."""
    # brute‑force via inclusion–exclusion for ≤2 points
    if len(points) == 1:
        return numpy.prod(ref - points[0])
    if len(points) == 2:
        a1 = numpy.prod(ref - points[0])
        a2 = numpy.prod(ref - points[1])
        # overlap rectangle upper‑left corner is component‑wise max
        overlap_low = numpy.maximum(points[0], points[1])
        overlap = numpy.prod(numpy.maximum(ref - overlap_low, 0))
        return a1 + a2 - overlap
    raise ValueError("Helper only supports up to 2 points.")


@pytest.mark.parametrize(
    "pts, ref, manual",
    [
        (numpy.array([[1.0, 1.0]]), numpy.array([3.0, 3.0]), 4.0),
        (numpy.array([[1.0, 1.0], [1.0, 1.0]]), numpy.array([3.0, 3.0]), 4.0),
        (numpy.array([[1.0, 2.0], [2.0, 1.0]]), numpy.array([3.0, 3.0]), 3.0),
    ],
)
def test_hv_2d_exact(pts: numpy.ndarray, ref: numpy.ndarray, manual: float) -> None:
    """Exact hyper‑volume for 1‑ or 2‑point 2‑D sets matches manual calc."""
    expected = _manual_hv_2d(pts, ref)
    assert numpy.isclose(manual, expected)
    assert numpy.isclose(hv(pts, ref), expected)


def test_hv_3d_single_point() -> None:
    """Single point 3‑D volume is (ref‑point).prod()."""
    pts = numpy.array([[1.0, 1.0, 1.0]])
    ref = numpy.array([2.0, 2.0, 2.0])
    expected = numpy.prod(ref - pts[0])
    assert numpy.isclose(hv(pts, ref), expected)


def test_hv_dimension_mismatch() -> None:
    """Mismatch between nds objectives and ref‑point length raises error."""
    pts = numpy.array([[1.0, 2.0]])
    ref = numpy.array([3.0, 3.0, 3.0])  # one extra dimension
    with pytest.raises(ValueError):
        hv(pts, ref)


def test_hv_ref_point_not_1d() -> None:
    """Supplying a 2‑D ref‑point must raise, enforcing 1‑D requirement."""
    pts = numpy.array([[1.0, 2.0]])
    ref = numpy.array([[3.0, 3.0]])  # 2‑D instead of 1‑D
    with pytest.raises(ValueError):
        hv(pts, ref)
