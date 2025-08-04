# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Solver CLI for demographically fair machine learning systems.

This module defines the ``solve`` command, which loads one or more system score output
files in JSON format, validates them against a predefined data model, and computes
fairness-related indicators such as accuracy and equalized odds. It outputs JSON files
containing solutions (or operating-modes) following the chosen metrics space, and
thresholds.

Input files must conform to a structured data model including scores, ground-truth
labels, and protected attributes. The CLI provides options to customize metrics, and
select thresholds.
"""

import logging
import pathlib

logger = logging.getLogger(__name__.split(".", 1)[0])

import click

from ..metrics import supported_metrics
from ..scores import Scores
from . import utils


@click.command(
    epilog="""Examples:

\b
  1. Compute and store solutions from two systems on the current directory:

     .. code:: sh

        fairical solve scores/system1.json scores/system2.json

""",
)
@click.argument(
    "system",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=pathlib.Path),
    required=True,
    nargs=-1,
    callback=utils.validate_scores_json,
)
@click.option(
    "-d/-D",
    "--deduplicate/--no-deduplicate",
    default=True,
    show_default=True,
    help="If we should prune (deduplicate) similar solutions.",
)
@click.option(
    "-o",
    "--output-path",
    type=click.Path(
        dir_okay=True, file_okay=False, writable=True, path_type=pathlib.Path
    ),
    help="Directory where to store system solutions.",
)
@click.option(
    "-m",
    "--metric",
    type=str,
    multiple=True,
    help=f"Metric to consider for Pareto estimation. Values are considered in the "
    f"order they are provided forming the axes of a potentially multi-dimensional "
    f"surface where dominated and non-dominated solutions are evaluated. Valid values "
    f"are: {', '.join(supported_metrics())}, where ``<attr>`` refers to attributes in "
    f"the provided sensitive attribute dictionary, and ``<util>`` refers to any "
    f"supported utility metrics.",
    default=["acc", "eod+gender"],
    callback=utils.validate_metrics,
    show_default=True,
)
@click.option(
    "-T",
    "--thresholds",
    type=click.IntRange(2),
    help="If set, then run for a fixed number of equally-spaced thresholds in the "
    "interval [0.0, 1.0].  Here, you only specify the number of thresholds to use, "
    "with the minimum being 2. If you want explicitly set the thresholds, you should "
    "use the API directly. If unset, then let scikit-learn calculate the number of "
    "sensible thresholds based the scores and changes on the ROC or PR-curve "
    "depending on utility metrics chosen.",
    default=None,
    show_default=True,
    callback=utils.validate_thresholds,
)
@utils.verbosity_option(logger)
def solve(
    system: dict[str, Scores],
    deduplicate: bool,
    output_path: pathlib.Path | None,
    metric: list[str],
    thresholds: list[float] | None,
    verbose: int,
) -> None:  # numpydoc ignore=PR01
    """Find operating-modes (a.k.a. solutions) for ML systems.

    This module defines the ``solve`` command, which loads one or more system score
    output files in JSON format, validates them against a predefined data model, and
    computes fairness-related indicators such as accuracy and equalized odds. It outputs
    JSON files containing solutions (or operating-modes) following the chosen metrics
    space, and thresholds.

    Input JSON files must be formatted as described in the documentation.
    """

    # 0. validate that the selected protected attributes do exist inside JSON system
    # TODO: validate metrics against user loaded systems

    # 1. if no path was provided, using the current path
    if output_path is None:
        output_path = pathlib.Path()

    # 2. for each system provided as input, get solutions
    for k, v in system.items():
        if thresholds is not None:
            logger.info(
                f"Calculating solutions for system `{k}` using {len(thresholds)} "
                f"thresholds..."
            )
        else:
            logger.info(f"Calculating solutions for system `{k}`...")
        solutions = v.solutions(metric, thresholds=thresholds)
        if deduplicate:
            solutions = solutions.deduplicate()
        output_filename = (output_path / k).with_suffix(".json")
        utils.save_json_with_backup(output_filename, solutions.model_dump())
        logger.info(f"Saved `{output_filename}`")
