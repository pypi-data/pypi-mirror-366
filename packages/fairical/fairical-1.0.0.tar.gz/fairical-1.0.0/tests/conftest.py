# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib

import matplotlib
import pytest

matplotlib.use("agg")


@pytest.fixture
def datadir(request) -> pathlib.Path:
    """Return the directory in which the test is sitting. Check the pytest
    documentation for more information.

    Parameters
    ----------
    request
        Information of the requesting test function.

    Returns
    -------
    pathlib.Path
        The directory in which the test is sitting.
    """

    return pathlib.Path(request.module.__file__).parents[0]
