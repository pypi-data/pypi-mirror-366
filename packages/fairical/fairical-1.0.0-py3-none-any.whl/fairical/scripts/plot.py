# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Visualization CLI for demographically fair machine learning systems.

This module defines the ``plot`` command, which loads one or more system solutions in
JSON format and generates the pareto plots to visualize trade-offs between metrics.

The CLI provides options to output formatting, and radar plot generation, and is
intended to support analysis of fairness-performance trade-offs across systems.
"""

import logging
import pathlib

logger = logging.getLogger(__name__.split(".", 1)[0])

import click
import matplotlib

# avoids loading X11-dependent backends
matplotlib.use("agg")

from ..solutions import Solutions
from . import utils


@click.command(
    epilog="""Examples:

\b
  1. Evaluate adjustable fairness considering and create a file with a pareto plot
     (called ``pareto.pdf``):

     .. code:: sh

        fairical plot system-1.json system-2.json

""",
)
@click.argument(
    "system",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=pathlib.Path),
    required=True,
    nargs=-1,
    callback=utils.validate_solutions_json,
)
@click.option(
    "-d/-D",
    "--deduplicate/--no-deduplicate",
    default=True,
    help="If we should prune (deduplicate) similar solutions.",
)
@click.option(
    "-p",
    "--pareto",
    default="pareto.pdf",
    type=click.Path(dir_okay=False, writable=True, path_type=pathlib.Path),
    help="Name of the file where to save the plot.",
)
@utils.verbosity_option(logger)
def plot(
    system: dict[str, Solutions],
    deduplicate: bool,
    pareto: pathlib.Path,
    verbose: int,
) -> None:  # numpydoc ignore=PR01
    """Plot pareto frontiers of systems.

    This command takes an arbitrary number of JSON files describing ML system solutions
    and plots the Pareto front (i.e. non-dominated solutions according to an
    arbitrary number of utility and demographic fairness metrics).

    The JSON files must be formatted as described in the documentation.
    """
    from fairical.plot import pareto_plot

    if deduplicate:
        system = {k: v.deduplicate() for k, v in system.items()}

    solutions = {k: v.non_dominated_solutions() for k, v in system.items()}

    logger.info(f"Saving plot at `{str(pareto)}`...")
    fig, _ = pareto_plot(solutions)
    fig.savefig(pareto)
