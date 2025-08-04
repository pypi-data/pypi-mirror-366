# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tools for command-line applications."""

import logging
import pathlib
import shutil
import typing

import click
import compact_json
import numpy

from ..scores import Scores
from ..solutions import Solutions

logger = logging.getLogger(__name__)


def prepare_and_backup(path: pathlib.Path) -> None:
    """Ensure parent directory exists and back-up copies.

    This function will check that the directory leading to a file path exists and will
    created it otherwise.  It will also check if the file does not already exists, and
    back it up otherwise.

    Parameters
    ----------
    path
        The full path of the file to ensure the parent directory exists and that it is
        properly backed-up if necessary.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup = path.parent / (path.name + "~")
        shutil.copy(path, backup)


def save_json_with_backup(path: pathlib.Path, data: dict) -> None:
    """Save a dictionary into a JSON file with path checking and backup.

    This function will save a dictionary into a JSON file.  It will check to
    the existence of the directory leading to the file and create it if
    necessary.  If the file already exists on the destination folder, it is
    backed-up before a new file is created with the new contents.

    Parameters
    ----------
    path
        The full path where to save the JSON data.
    data
        The data to save on the JSON file.
    """

    formatter = compact_json.Formatter()
    # only only 2 indent spaces for further levels
    formatter.indent_spaces = 2
    # controls how much nesting can happen
    formatter.max_inline_complexity = 2
    # controls the maximum line width (has priority over nesting)
    formatter.max_inline_length = 88
    # remove any trailing whitespaces
    formatter.omit_trailing_whitespace = True

    prepare_and_backup(path)

    formatter.dump(data, str(path))


def validate_scores_json(
    ctx: click.Context, param: click.Parameter, value: typing.Sequence[pathlib.Path]
) -> dict[str, Scores]:
    """
    Validate one or more JSON files against a predefined data model.

    This function is intended to be used as a Click argument callback. It opens the
    given file path, parses its JSON content, and validates it against the library data
    model. If any validation error occurs, a `click.BadParameter` is raised to inform
    the user.

    Parameters
    ----------
    ctx
        The Click execution context.
    param
        The parameter that triggered the callback.
    value
        Path to the JSON files to load and validate.

    Returns
    -------
        The parsed and validated JSON content as a dictionary, where keys represent the
        basename of files without extension.

    Raises
    ------
    click.BadParameter
        If the file cannot be read, contains invalid JSON, or fails data model
        validation.
    """

    retval: dict[str, Scores] = {}

    for v in value:
        try:
            assert v.stem not in retval
            logger.info(f"Loading scores for system `{v}`...")
            retval[v.stem] = Scores.load(v)
        except AssertionError as e:
            raise click.BadParameter(f"The same path was passed more than once: {e}")
        except __import__("pydantic").ValidationError as e:
            raise click.BadParameter(f"Score data model validation failed: {e}")

    return retval


def validate_solutions_json(
    ctx: click.Context, param: click.Parameter, value: typing.Sequence[pathlib.Path]
) -> dict[str, Solutions]:
    """
    Validate one or more JSON files against a predefined data model.

    This function is intended to be used as a Click argument callback. It opens the
    given file path, parses its JSON content, and validates it against the library data
    model. If any validation error occurs, a `click.BadParameter` is raised to inform
    the user.

    Parameters
    ----------
    ctx
        The Click execution context.
    param
        The parameter that triggered the callback.
    value
        Path to the JSON files to load and validate.

    Returns
    -------
        The parsed and validated JSON content as a dictionary, where keys represent the
        basename of files without extension.

    Raises
    ------
    click.BadParameter
        If the file cannot be read, contains invalid JSON, or fails data model
        validation.
    """

    retval: dict[str, Solutions] = {}

    for v in value:
        try:
            assert v.stem not in retval
            logger.info(f"Loading solutions for system `{v}`...")
            retval[v.stem] = Solutions.load(v)
        except AssertionError as e:
            raise click.BadParameter(f"The same path was passed more than once: {e}")
        except __import__("pydantic").ValidationError as e:
            raise click.BadParameter(f"Solution data model validation failed: {e}")

    return retval


def validate_metrics(
    ctx: click.Context, param: click.Parameter, value: typing.Sequence[str]
) -> tuple[str, ...]:
    """Validate a user defined metric for support.

    Parameters
    ----------
    ctx
        The Click execution context.
    param
        The parameter that triggered the callback.
    value
        The value to validate.

    Returns
    -------
        The validated metrics.

    Raises
    ------
    click.BadParameter
        If one or more of the provided metrics do not validate correctly.
    """
    from .. import metrics

    invalid = []
    for name in value:
        try:
            metrics.parse_metric(name)
        except ValueError:
            invalid.append(f"`{name}`")

    if invalid:
        raise click.BadParameter(f"invalid metric names: {', '.join(invalid)}")

    return tuple(value)


def validate_thresholds(
    ctx: click.Context, param: click.Parameter, value: int | None
) -> None | list[float]:
    """Validate a threshold setup.

    Parameters
    ----------
    ctx
        The Click execution context.
    param
        The parameter that triggered the callback.
    value
        The value to validate.

    Returns
    -------
        The validated threshold, as our API likes it.

    Raises
    ------
    click.BadParameter
        If the threshold cannot be validated.
    """

    if value is None:
        return value

    return typing.cast(list[float], list(numpy.linspace(0, 1, value, dtype=float)))


def verbosity_option(
    logger: logging.Logger,
    short_name: str = "v",
    name: str = "verbose",
    dflt: int = 0,
    **kwargs: typing.Any,
) -> typing.Callable[..., typing.Any]:
    """Click-option decorator that adds a ``-v``/``--verbose`` option to a cli.

    This decorator adds a click option to your CLI to set the log-level on a
    provided :py:class:`logging.Logger`.  You must specifically determine the
    logger that will be affected by this CLI option, via the ``logger`` option.

    .. code-block:: python

       @verbosity_option(logger=logger)

    The verbosity option has the "count" type, and has a default value of 0.
    At each time you provide ``-v`` options on the command-line, this value is
    increased by one.  For example, a CLI setting of ``-vvv`` will set the
    value of this option to 3.  This is the mapping between the value of this
    option (count of ``-v`` CLI options passed) and the log-level set at the
    provided logger:

    * 0 (no ``-v`` option provided): ``logger.setLevel(logging.ERROR)``
    * 1 (``-v``): ``logger.setLevel(logging.WARNING)``
    * 2 (``-vv``): ``logger.setLevel(logging.INFO)``
    * 3 (``-vvv`` or more): ``logger.setLevel(logging.DEBUG)``


    Arguments:

        logger: The :py:class:`logging.Logger` to be set.

        short_name: Short name of the option.  If not set, then use ``v``

        name: Long name of the option.  If not set, then use ``verbose`` --
            this will also become the name of the contextual parameter for click.

        dlft: The default verbosity level to use (defaults to 0).

        **kwargs: Further keyword-arguments to be forwarded to the underlying
            :py:func:`click.option`


    Returns
    -------
        A callable, that follows the :py:mod:`click`-framework policy for
        option decorators.  Use it accordingly.
    """

    def custom_verbosity_option(f):
        def callback(ctx, _, value):
            ctx.meta[name] = value
            log_level: int = {  # type: ignore
                0: logging.ERROR,
                1: logging.WARNING,
                2: logging.INFO,
                3: logging.DEBUG,
            }[value]

            # one‐time handler setup
            if not getattr(logger, "_verbosity_configured", False):
                handler = logging.StreamHandler()
                handler.setFormatter(
                    logging.Formatter(
                        "%(levelname)s %(name)s: %(message)s",
                    )
                )
                logger.addHandler(handler)
                logger._verbosity_configured = True  # type: ignore[attr-defined]

            logger.setLevel(log_level)
            logger.debug(f'Level of Logger("{logger.name}") was set to {log_level}')

            return value

        return click.option(
            f"-{short_name}",
            f"--{name}",
            count=True,
            type=click.IntRange(min=0, max=3, clamp=True),
            default=dflt,
            show_default=True,
            help=(
                f"Increase the verbosity level from 0 (only error and "
                f"critical) messages will be displayed, to 1 (like 0, but adds "
                f"warnings), 2 (like 1, but adds info messags), and 3 (like 2, "
                f"but also adds debugging messages) by adding the --{name} "
                f"option as often as desired (e.g. '-vvv' for debug)."
            ),
            callback=callback,
            **kwargs,
        )(f)

    return custom_verbosity_option
