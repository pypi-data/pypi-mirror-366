# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy

from fairical.solutions import Solutions


def test_single_pareto_point() -> None:
    """Only one solution should survive when it dominates all others."""

    sol = Solutions.fromarray([[0.1, 0.9], [0.2, 0.2], [0.3, 0.3]], ("eod+race", "acc"))
    nds, ds = sol.non_dominated_solutions()

    front = numpy.asarray(nds)
    back = numpy.asarray(ds)

    assert front.shape == (1, sol.n_metrics())
    numpy.testing.assert_allclose(front[0], [0.1, 0.9])

    assert back.shape == (2, sol.n_metrics())
    numpy.testing.assert_allclose(back, numpy.array([[0.2, 0.2], [0.3, 0.3]]))

    # check ONVG and ONVGR
    indicators = sol.indicators()
    assert indicators["onvg"] == 1.0
    assert indicators["onvgr"] == 1 / 3


def test_two_non_dominated_points() -> None:
    """Two solutions mutually non‑dominated should both be returned."""

    sol = Solutions.fromarray([[0.1, 0.8], [0.2, 0.9], [0.3, 0.3]], ("eod+age", "f1"))
    nds, ds = sol.non_dominated_solutions()

    front = numpy.asarray(nds)
    back = numpy.asarray(ds)

    assert front.shape == (2, sol.n_metrics())
    numpy.testing.assert_allclose(front, numpy.array([[0.1, 0.8], [0.2, 0.9]]))

    assert back.shape == (1, sol.n_metrics())
    numpy.testing.assert_allclose(back[0], [0.3, 0.3])

    # check ONVG and ONVGR
    indicators = sol.indicators()
    assert indicators["onvg"] == 2.0
    assert indicators["onvgr"] == 2 / 3


def test_duplicate_points() -> None:
    """Identical optimal points are all kept; duplicates aren't filtered."""

    sol = Solutions.fromarray(
        [[0.1, 0.9], [0.1, 0.9], [0.2, 0.2]], ("eod+gender", "acc")
    )
    nds, ds = sol.non_dominated_solutions()

    front = numpy.asarray(nds)
    back = numpy.asarray(ds)

    assert front.shape == (2, sol.n_metrics())
    numpy.testing.assert_allclose(front, numpy.array([[0.1, 0.9], [0.1, 0.9]]))

    assert back.shape == (1, sol.n_metrics())
    numpy.testing.assert_allclose(back[0], [0.2, 0.2])

    # check ONVG and ONVGR
    indicators = sol.indicators()
    assert indicators["onvg"] == 2.0
    assert indicators["onvgr"] == 2 / 3


def test_deduplicate_points() -> None:
    """Identical optimal points are all kept; duplicates are filtered."""

    sol = Solutions.fromarray(
        [[0.1, 0.9], [0.1, 0.9], [0.2, 0.2]], ("eod+race", "bal_acc")
    )
    nds, ds = sol.deduplicate().non_dominated_solutions()

    front = numpy.asarray(nds)
    back = numpy.asarray(ds)

    assert front.shape == (1, sol.n_metrics())
    numpy.testing.assert_allclose(front[0], [0.1, 0.9])

    assert back.shape == (1, sol.n_metrics())
    numpy.testing.assert_allclose(back[0], [0.2, 0.2])

    # check ONVG and ONVGR
    indicators = sol.deduplicate().indicators()
    assert indicators["onvg"] == 1.0
    assert indicators["onvgr"] == 0.5


def test_three_objective_case() -> None:
    """Verify correct Pareto extraction with three objectives."""

    sol = Solutions.fromarray(
        [
            [0.1, 0.1, 0.5],  # non‑dominated
            [0.5, 0.1, 0.9],  # non‑dominated
            [0.1, 0.5, 0.9],  # non‑dominated
            [0.3, 0.3, 0.4],  # dominated by (0.1,0.1,0.5)
            [0.2, 0.2, 0.8],  # non-dominated
        ],
        ("eod+race", "eod+gender", "roc_auc"),
    )
    nds, ds = sol.non_dominated_solutions()

    front = numpy.asarray(nds)
    back = numpy.asarray(ds)

    assert front.shape == (4, sol.n_metrics())
    # Ensure the dominated point is NOT present
    assert not any(numpy.allclose(p, [0.3, 0.3, 0.4]) for p in front)

    assert back.shape == (1, sol.n_metrics())
    # Ensure the dominated point is there
    numpy.testing.assert_allclose(back[0], [0.3, 0.3, 0.4])

    # check ONVG and ONVGR
    indicators = sol.indicators()
    assert indicators["onvg"] == 4.0
    assert indicators["onvgr"] == 0.8
