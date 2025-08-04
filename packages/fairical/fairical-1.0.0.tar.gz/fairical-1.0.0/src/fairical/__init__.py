# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""A library to assess adjustable demographically fair Machine Learning (ML) systems."""

from .plot import pareto_plot, radar_chart
from .scores import Scores
from .solutions import Solutions
from .utils import make_table

__all__ = [
    "Scores",
    "Solutions",
    "make_table",
    "pareto_plot",
    "radar_chart",
]
