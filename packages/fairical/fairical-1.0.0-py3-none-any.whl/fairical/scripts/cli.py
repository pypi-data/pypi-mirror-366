# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Command-line interface for assessing demographically fair ML systems.

This module defines the root CLI entry point using :py:mod:`click`. It includes a base
command group and dynamically registers subcommands by importing them from other modules
in the package.
"""

import importlib

import click


@click.group(
    context_settings=dict(help_option_names=["-?", "-h", "--help"]),
)
def cli():
    """Assess adjustable demographically fair Machine Learning (ML) systems."""
    pass


def _add_command(module, obj):
    cli.add_command(
        getattr(importlib.import_module("." + module, package=__name__), obj)
    )


_add_command(".solve", "solve")
_add_command(".evaluate", "evaluate")
_add_command(".plot", "plot")
