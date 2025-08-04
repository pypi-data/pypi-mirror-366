# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import numpy
import pytest

from fairical.utils import normalized_radar_area


@pytest.mark.parametrize(
    "values,expected",
    [
        # trivial use-cases
        ([1, 1, 1], 1),
        ([1, 1, 1, 1], 1),
        ([1, 1, 1, 1, 1], 1),
        ([0, 0, 0], 0),
        ([0, 0, 0, 0], 0),
        ([0, 0, 0, 0, 0], 0),
        ([1, 0, 0], 0),
        ([1, 1, 0], 1 / 3),
        ([1, 1, 1, 0], 2 / 4),
        ([1, 1, 1, 0, 0], 2 / 5),
        ([1, 1, 1, 1, 0], 3 / 5),
        ([1, 1, 0, 1, 1], 3 / 5),
        ([0.5, 0.5, 0.5], 1 / 4),
        ([0.5, 0.5, 0.5, 0.5], 1 / 4),
        ([0.5, 0.5, 0.5, 0.5, 0.5], 1 / 4),
    ],
    ids=lambda x: str(x),  # just changes how pytest prints it
)
def test_case(values: list[float], expected: float):
    assert numpy.allclose(normalized_radar_area(values), expected)
