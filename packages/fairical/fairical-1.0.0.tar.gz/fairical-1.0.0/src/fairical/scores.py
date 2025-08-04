# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Data model organizing scores of ML systems under multi-objective constraints.

The model describes a data structure containing machine learning model scores,
ground-truth labels, and sensitive attributes (e.g., race, gender).
"""

import json
import logging
import pathlib
import typing

import pydantic
import sklearn.metrics

from . import metrics, solutions

logger = logging.getLogger(__name__)

_CACHE: dict[pathlib.Path, list] = {}
"""We read input files only once, and then serve repeated reads from the cache to save
memory and read-time."""


def _cache_json(path: pathlib.Path) -> list | dict:
    """Load and cache a JSON file.

    Parameters
    ----------
    path
        Path to the file to load and cache.

    Returns
    -------
    list
        A list of scores, ground-truth or attributes.
    """
    path = path.resolve()
    if path in _CACHE:
        return _CACHE[path]
    return _CACHE.setdefault(path, json.load(path.open("r")))


def _single_system_solutions(
    scores: typing.Sequence[float],
    ground_truth: typing.Sequence[int],
    attributes: typing.Mapping[str, list[int | str]],
    eval_metrics: typing.Sequence[str],
    thresholds: list[float] | None = None,
) -> dict[str, list[float]]:
    """Calculate all solutions of a sub-system, given metrics and thresholds.

    Helper method for py:func:`solutions` -- check its documentation for help.

    Parameters
    ----------
    scores
        Scores of the sub-system being analyzed.
    ground_truth
        Ground-truth for the task.
    attributes
        Protected attributes to consider for the calculation of demographic fairness
        metrics.
    eval_metrics
        Metrics types to consider when evaluating solutions. Example: ``eod+age``,
        ``eod+gender``, or ``acc``.
    thresholds
        List of thresholds to apply as values within the interval :math:`[0,1]`. If not
        provided, then estimate thresholds using scikit's ROC technique.

    Returns
    -------
        All know solutions for the input system.
    """

    solutions: dict[str, list[float]] = {}

    # we cache everything we calculate so we don't calculate the same quantity twice
    cache: dict[str, list[float]] = {}

    if thresholds is None:
        if any([k in eval_metrics for k in ("prec", "rec", "avg_prec", "f1")]):
            # use precision-recall-thresholds as thresholds
            prec, rec, pr_thresholds = sklearn.metrics.precision_recall_curve(
                ground_truth, scores
            )
            cache["prec"] = list(prec)
            cache["rec"] = list(rec)
            thresholds = list(pr_thresholds)

        # if any([k in eval_metrics for k in ("fpr", "tpr", "roc_auc", "acc")]):
        else:
            # use roc-thresholds as thresholds
            fpr, tpr, roc_thresholds = sklearn.metrics.roc_curve(ground_truth, scores)
            cache["fpr"] = list(fpr)
            cache["tpr"] = list(tpr)
            thresholds = list(roc_thresholds)

        logger.info(f"Using {len(thresholds)} thresholds for evaluation of solutions.")

    for metric in eval_metrics:
        if metric not in cache:
            cache[metric] = metrics.calculate_metric(
                metric, ground_truth, scores, thresholds, attributes
            )
        solutions[metric] = cache[metric]

    return solutions


class Scores(pydantic.BaseModel):
    """Data model representing raw machine learning score outputs.

    It is composed of a set of scores, for one or more operating points (e.g. preference
    rays, or ratios between various optimisation objectives), ground-truth for the task
    being analyzed, as well as extra (protected?) attributes that are relevant for, at
    least, demographic fairness analysis.

    For the JSON representation, scores, ground-truth, and demographic attributes may be
    inlined or out-sourced to an external file where the data structure can be loaded
    from.  Relative paths are considered w.r.t. the location of the current file.
    """

    #: Inline scores data or list of file paths. Each score must be a floating-point
    #: number between 0 and 1 inclusive.
    scores: list[
        list[typing.Annotated[float, pydantic.Field(ge=0.0, le=1.0)]] | pathlib.Path
    ] = pydantic.Field(
        ...,
        description="One or many lists of scores representing different operating "
        "points of the system being analyzed.",
    )

    #: Inline ground-truth data or a single file path. Each ground-truth label must be
    #: an integer with a minimum value of 0.
    ground_truth: list[typing.Annotated[int, pydantic.Field(ge=0)]] | pathlib.Path = (
        pydantic.Field(
            ...,
            alias="ground-truth",
            description="Ground-truth for the task being analyzed.",
        )
    )

    #: Inline attributes data or a single file path. It is setup as a dictionary
    #: mapping attribute names to lists of demographic data, which can be of type str,
    #: integer or floating-point.
    attributes: (
        dict[
            str,
            list[str | typing.Annotated[int, pydantic.Field(ge=0)]],
        ]
        | pathlib.Path
    ) = pydantic.Field(
        ...,
        description="Meta-data (demographic or other) attributes for samples "
        "in the task.",
    )

    @pydantic.model_validator(mode="after")
    def maybe_load_members(self, info: pydantic.ValidationInfo) -> typing.Self:
        """Load all external files if needed."""

        base = pathlib.Path.cwd()
        if info.context is not None:
            base = pathlib.Path(info.context.get("base_dir", base))

        for k, v in enumerate(self.scores):
            if isinstance(v, pathlib.Path):
                path = (base / v) if not v.is_absolute() else v
                self.scores[k] = typing.cast(list[float], _cache_json(path))

        if isinstance(self.ground_truth, pathlib.Path):
            gt_path = (
                (base / self.ground_truth)
                if not self.ground_truth.is_absolute()
                else self.ground_truth
            )
            self.ground_truth = typing.cast(list[int], _cache_json(gt_path))

        if isinstance(self.attributes, pathlib.Path):
            attr_path = (
                (base / self.attributes)
                if not self.attributes.is_absolute()
                else self.attributes
            )
            self.attributes = typing.cast(
                dict[str, list[int | str]], _cache_json(attr_path)
            )

        return self

    @pydantic.model_validator(mode="after")
    def check_consistent_lengths(self) -> typing.Self:
        """Ensure all sample-level lists have the same length."""

        assert isinstance(self.scores[0], list)
        expected = len(self.scores[0])

        # Validate each ScoreList
        for idx, score_list in enumerate(self.scores):
            assert isinstance(score_list, list)
            if len(score_list) != expected:
                raise ValueError(
                    f"scores[{idx}] length {len(score_list)} != {expected}"
                )

        # Validate ground-truth length
        assert isinstance(self.ground_truth, list)
        gt_len = len(self.ground_truth)
        if gt_len != expected:
            raise ValueError(f"ground-truth length {gt_len} != {expected}")

        # Validate attributes lengths
        assert isinstance(self.attributes, dict)
        for name, values in self.attributes.items():
            if len(values) != expected:
                raise ValueError(
                    f"attribute '{name}' length {len(values)} != {expected}"
                )

        return self

    @classmethod
    def load(cls, source: pathlib.Path | str | typing.TextIO) -> typing.Self:
        """Validate and load a JSON file into a raw data object.

        This function is intended to validate and load the input in JSON format. It opens
        the given file path, parses its JSON content, and validates it against the defined
        data model.

        Parameters
        ----------
        source
            Source input where to read JSON from.

        Returns
        -------
            Parsed and validated content as a :py:class:`Scores` instance.

        Raises
        ------
        pydantic_core.ValidationError
            If the file contains invalid data.
        """

        if isinstance(source, pathlib.Path | str):
            path = pathlib.Path(source)
            return cls.model_validate_json(
                path.read_text(), context={"base_dir": path.parent}
            )

        else:  # noqa: RET505
            return cls.model_validate_json(source.read())

    def save(self, dest: pathlib.Path | str | typing.TextIO, **args) -> None:
        """Save contents to an external file.

        Parameters
        ----------
        dest
            Destination where to save the contents. If not a path or str, then assumed
            to have a ``write`` method accepting strings.
        args
            Parameters further passed down to
            :py:func:`pydantic.BaseModel.model_dump_json`.
        """

        if isinstance(dest, pathlib.Path | str):
            with pathlib.Path(dest).open("w", encoding="utf-8") as f:
                f.write(self.model_dump_json(**args))

        else:
            dest.write(self.model_dump_json(**args))

    def solutions(
        self, metrics: typing.Sequence[str], thresholds: list[float] | None = None
    ) -> solutions.Solutions:
        """Calculate all solutions of a system, given metrics and thresholds.

        This method retrieves solutions that can be implemented systems. For each set of
        scores in ``self.scores``, it calculates all solutions of the system being
        analysed through simple thresholding, and then aggregate all solutions to
        construct all possible sets of solutions a system can implement.

        Parameters
        ----------
        metrics
            Metrics types to consider when evaluating solutions. Example: ``eod+age``,
            ``eod+gender``, or ``acc``.
        thresholds
            List of thresholds to apply as values within the interval :math:`[0,1]`. If
            not provided, then uses scikit-learn to extract meaningful scores from the
            system.

        Returns
        -------
            All know solutions for the input system.
        """

        data: dict[str, list[float]] = {k: [] for k in metrics}

        for i, subsystem in enumerate(self.scores):
            logger.info(f"Evaluating subsystem {i + 1}/{len(self.scores)}")
            sol = _single_system_solutions(
                # note: at this point we are sure not to have any path lying around!
                typing.cast(typing.Sequence[float], subsystem),
                typing.cast(typing.Sequence[int], self.ground_truth),
                typing.cast(typing.Mapping[str, list[int | str]], self.attributes),
                metrics,
                thresholds,
            )

            for k in metrics:
                data[k] += sol[k]

        return solutions.Solutions.model_validate(data)
