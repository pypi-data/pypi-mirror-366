# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Evaluation CLI for demographically fair machine learning systems.

This module defines the ``evaluate`` command, which loads one or more system solution
files in JSON format, validates them against a predefined data model, and computes
Pareto-front indicators. It supports tabulated output in various formats (via
`tabulate`) and optional generation of radar plots to visualize trade-offs between
metrics.

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
  1. Evaluate adjustable fairness (estimate Pareto/Non-dominated-solutions) from
     two systems, and print table with indicators:

     .. code:: sh

        fairical evaluate system1.json system2.json

\b
  2. Evaluate adjustable fairness and create a file with a radar plot (called
     ``radar.pdf``):

     .. code:: sh

        fairical evaluate system1.json system2.json --radar radar.pdf

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
    "-r",
    "--radar",
    type=click.Path(dir_okay=False, writable=True, path_type=pathlib.Path),
    help="Creates radar plot of system indicators and saves it to file",
)
@click.option(
    "-d/-D",
    "--deduplicate/--no-deduplicate",
    default=True,
    help="If we should prune (deduplicate) similar solutions.",
)
@click.option(
    "-t",
    "--table-format",
    type=click.Choice(__import__("tabulate").tabulate_formats),
    help="Output table format.",
    default="simple",
    show_default=True,
)
@utils.verbosity_option(logger)
def evaluate(
    system: dict[str, Solutions],
    radar: pathlib.Path | None,
    deduplicate: bool,
    table_format: str,
    verbose: int,
) -> None:  # numpydoc ignore=PR01
    """Evaluate systems for adjustable fairness.

    This command takes an arbitrary number of JSON files describing ML system solutions
    and estimates the Pareto front (i.e. non-dominated solutions according to an
    arbitrary number of utility and demographic fairness metrics), and outputs
    indicators that characterize the trade-off between all metrics.

    The JSON files must be formatted as described in the documentation.
    """
    # 1. for each system, get indicators
    indicator_values = []
    for k, v in system.items():
        sol = v.deduplicate() if deduplicate else v
        indicator_values.append(sol.indicators())
    indicators = dict(zip(system.keys(), indicator_values))

    # 2. table and output to stdout
    from fairical.utils import make_table

    click.echo(make_table(indicators, fmt=table_format))

    if radar is not None:
        # [optional] 3. save radar plot of indicators
        from fairical.plot import radar_chart

        fig, _ = radar_chart(indicators)
        fig.savefig(radar)
