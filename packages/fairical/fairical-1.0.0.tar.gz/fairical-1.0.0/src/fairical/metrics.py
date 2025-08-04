# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Helpers to evaluate scikit-learn metrics at arbitrary thresholds."""

import typing

import fairlearn.metrics
import numpy
import sklearn.metrics

UtilityMetricsType: typing.TypeAlias = typing.Literal[
    "fpr",  # False Positive Rate (minimize, range: [0, 1])
    "tpr",  # True Positive Rate (maximize, range: [0, 1])
    "tnr",  # True Negative Rate (minimize, range: [0, 1])
    "fnr",  # False Negative Rate (minimize, range: [0, 1])
    "roc_auc",  # Area Under the Curve for Receiver Operating Characteristic (maximize, range: [0, 1])
    "prec",  # Precision (maximize, range: [0, 1])
    "rec",  # Recall (maximize, range: [0, 1])
    "avg_prec",  # Average precision for Precision Recall Curve (maximize, range: [0, 1])
    "f1",  # F1 Score (maximize, range: [0, 1])
    "acc",  # Accuracy (maximize, range: [0, 1])
    "bal_acc",  # Balanced Accuracy (maximize, range: [0, 1])
]
"""Supported utility metrics type for pareto front estimates."""

FairnessMetricsType: typing.TypeAlias = typing.Literal[
    "dpd",  # Demographic Parity Difference (minimize, range: [0, 1])
    "dpr",  # Demographic Parity Ratio (maximize, range: [0, 1])
    "eod",  # Equalized Odds Difference (minimize, range: [0, 1])
    "eor",  # Equalized Odds Ratio (maximize, range: [0, 1])
]
"""Supported fairness metrics type for pareto front estimates."""

MinMaxFairnessMetricsType: typing.TypeAlias = typing.Literal[
    "minmaxd",  # Min-Max (absolute) difference: max(util) - min(util)
    "minmaxr",  # Min-Max ratio: min(util) / max(util)
]
"""Supported min-max fairness metrics type for pareto front estimates."""


def parse_metric(
    name: str,
) -> (
    UtilityMetricsType
    | tuple[FairnessMetricsType, str]
    | tuple[MinMaxFairnessMetricsType, UtilityMetricsType, str]
):
    """Parse and validate a string supposed to carry a metric name.

    Valid metric names are the ones listed in :py:type:`UtilityMetricsType`,
    :py:type:`FairnessMetricsType` (followed by a "+<attr>"), or
    :py:type:`MinMaxFairnessMetricsType` (followed by a "+<util>+<attr>"), where
    ``<attr>`` corresponds to the protected attribute being measured by the fairness
    metric, and ``<util>`` corresponds to the :py:type:`UtilityMetricsType` to be used
    to measure min-max fairness difference or ratios.

    Parameters
    ----------
    name
        The string to be validated.

    Returns
    -------
        The parsed metric.

    Raises
    ------
    ValueError
        If the metric expressed in ``name`` is invalid.
    """

    parts = name.split("+", 2)
    if parts[0] in typing.get_args(UtilityMetricsType):
        return typing.cast(UtilityMetricsType, parts[0])
    if parts[0] in typing.get_args(FairnessMetricsType):
        if len(parts) != 2:
            raise ValueError(
                f"fairness metric should be set like `{parts[0]}+<attr>` "
                f"(`{name}` is invalid)"
            )
        return (typing.cast(FairnessMetricsType, parts[0]), parts[1])
    if parts[0] in typing.get_args(MinMaxFairnessMetricsType):
        if len(parts) != 3:
            raise ValueError(
                f"min-max fairness metric should be set like `{parts[0]}+<util>+<attr>` "
                f"(`{name}` is invalid)"
            )
        if parts[1] not in typing.get_args(UtilityMetricsType):
            raise ValueError(f"invalid utility metric name `{parts[1]}` at `{name}`")
        return (
            typing.cast(MinMaxFairnessMetricsType, parts[0]),
            typing.cast(UtilityMetricsType, parts[1]),
            parts[2],
        )

    raise ValueError(f"Invalid metric specification: `{name!r}`")


def should_minimize(metric: str) -> bool:
    """For a given metric, tells if it should be minimized or maximized.

    Currently, "fpr", in the utility side, "minmaxd" on the min-max fairness metrics, or
    any other fairness metric should be minimized. All others should be maximized.

    Parameters
    ----------
    metric
        Metric name.

    Returns
    -------
        ``True``, if the metric should be minimized (instead of maximized).  ``False``
        otherwise.

    Raises
    ------
    ValueError
        If the metric is invalid.
    """
    pm = parse_metric(metric)
    return (
        pm in ("fpr", "fnr")
        or (isinstance(pm, tuple) and len(pm) == 2 and pm[0] in ("dpd", "eod"))
        or (isinstance(pm, tuple) and len(pm) == 3 and pm[0] == "minmaxd")
    )


def supported_metrics() -> list[str]:
    """Generate a comma-separated list of supported metrics.

    Returns
    -------
        A comma-separated list of supported metrics.
    """

    utility = typing.get_args(UtilityMetricsType)
    fairness = [f"{k}+<attr>" for k in typing.get_args(FairnessMetricsType)]
    minmax = [f"{k}+<util>+<attr>" for k in typing.get_args(MinMaxFairnessMetricsType)]

    return list(utility) + fairness + minmax


def calculate_metric(
    metric: str,
    y_true: typing.Sequence[int],
    y_score: typing.Sequence[float],
    thresholds: typing.Sequence[float],
    sensitive_attributes: typing.Mapping[str, typing.Sequence[int | str]] | None = None,
) -> list[float]:
    """Entry-point function to calculate arbitrary (supported) metrics.

    This function works as an entry-point to the metric calculation submodule. It can
    calculate arbirary (supported) metrics provided input information for a system,
    consisting of ground-truth, scores, thresholds and (optionally) sensitive features.

    Parameters
    ----------
    metric
        The metric to calculate.
    y_true
        True binary labels (0 or 1).
    y_score
        Predicted continuous scores or probabilities.
    thresholds
        Threshold values at which to binarize ``y_score`` (:math:`score >= threshold`
        implies sample is classified as positive).
    sensitive_attributes
        Group membership for each sample, according to protected attribute. Only
        required if ``metric`` is a fairness metric. Each entry in the input dictionary
        should match the order of samples in ``y_true`` and ``y_score``. When ``metric``
        refers to a particular sensitive attribute, it should be a key in this
        dictionary.

    Returns
    -------
        The metric over all considered thresholds.

    Raises
    ------
    ValueError
        In case of unknown metrics.
    """
    parsed_metric = parse_metric(metric)

    if parsed_metric in typing.get_args(UtilityMetricsType):
        # simple closure to avoid repeatitive for loops with the same config
        def _for_all_t(f):
            y_score_arr = numpy.asarray(y_score, dtype=float)
            return numpy.nan_to_num(
                [f(y_true, y_score_arr >= t) for t in thresholds]
            ).tolist()

        match metric:
            case "fpr":
                return _for_all_t(fairlearn.metrics.false_positive_rate)

            case "tpr":
                return _for_all_t(fairlearn.metrics.true_positive_rate)

            case "fnr":
                return _for_all_t(fairlearn.metrics.false_negative_rate)

            case "tnr":
                return _for_all_t(fairlearn.metrics.true_negative_rate)

            case "acc":
                return _for_all_t(sklearn.metrics.accuracy_score)

            case "bal_acc":
                return _for_all_t(sklearn.metrics.balanced_accuracy_score)

            case "prec":
                return _for_all_t(sklearn.metrics.precision_score)

            case "rec":
                return _for_all_t(sklearn.metrics.recall_score)

            case "f1":
                return _for_all_t(sklearn.metrics.f1_score)

            case "roc_auc":
                # there is only 1 roc-auc, where there are multiple fpr or tpr points --
                # so we repeat the roc-auc as many times as there are thresholds to keep
                # consistence.
                val = float(sklearn.metrics.roc_auc_score(y_true, y_score))
                return len(thresholds) * [val]

            case "avg_prec":
                # there is only 1 average precision, where there are multiple fpr or tpr
                # points -- so we repeat the average precision as many times as there are
                # thresholds to keep consistence.
                val = float(sklearn.metrics.average_precision_score(y_true, y_score))
                return len(thresholds) * [val]

    elif (
        isinstance(parsed_metric, tuple)
        and len(parsed_metric) == 2
        and parsed_metric[0] in typing.get_args(FairnessMetricsType)
    ):
        assert sensitive_attributes is not None
        assert parsed_metric[1] in sensitive_attributes

        # simple closure to avoid repeatitive for loops with the same config
        def _for_all_t(f):
            y_score_arr = numpy.asarray(y_score, dtype=float)
            return numpy.nan_to_num(
                [
                    f(
                        y_true,
                        y_score_arr >= t,
                        sensitive_features=sensitive_attributes[parsed_metric[1]],
                    )
                    for t in thresholds
                ]
            ).tolist()

        match parsed_metric[0]:
            case "dpd":
                return _for_all_t(fairlearn.metrics.demographic_parity_difference)

            case "dpr":
                return _for_all_t(fairlearn.metrics.demographic_parity_ratio)

            case "eod":
                return _for_all_t(fairlearn.metrics.equalized_odds_difference)

            case "eor":
                return _for_all_t(fairlearn.metrics.equalized_odds_ratio)

    elif (
        isinstance(parsed_metric, tuple)
        and len(parsed_metric) == 3
        and parsed_metric[0] in typing.get_args(MinMaxFairnessMetricsType)
    ):
        assert sensitive_attributes is not None
        assert parsed_metric[2] in sensitive_attributes

        # simple closures to avoid repeatitive for loops with the same config
        def _for_all_t(f):
            y_score_arr = numpy.asarray(y_score, dtype=float)
            return numpy.nan_to_num(
                [
                    f(
                        y_true,
                        y_score_arr >= t,
                        sensitive_features=sensitive_attributes[parsed_metric[2]],
                    )
                    for t in thresholds
                ]
            ).tolist()

        def _make_derived(f):
            return fairlearn.metrics.make_derived_metric(
                metric=f,
                transform="difference" if parsed_metric[0] == "minmaxd" else "ratio",
            )

        match parsed_metric[1]:
            case "fpr":
                return _for_all_t(_make_derived(fairlearn.metrics.false_positive_rate))

            case "tpr":
                return _for_all_t(_make_derived(fairlearn.metrics.true_positive_rate))

            case "fnr":
                return _for_all_t(_make_derived(fairlearn.metrics.false_negative_rate))

            case "tnr":
                return _for_all_t(_make_derived(fairlearn.metrics.true_negative_rate))

            case "acc":
                return _for_all_t(_make_derived(sklearn.metrics.accuracy_score))

            case "bal_acc":
                return _for_all_t(
                    _make_derived(sklearn.metrics.balanced_accuracy_score)
                )

            case "prec":
                return _for_all_t(_make_derived(sklearn.metrics.precision_score))

            case "rec":
                return _for_all_t(_make_derived(sklearn.metrics.recall_score))

            case "f1":
                return _for_all_t(_make_derived(sklearn.metrics.f1_score))

            case "roc_auc":
                # there is only 1 roc-auc, where there are multiple fpr or tpr points --
                # so we repeat the roc-auc as many times as there are thresholds to keep
                # consistence.
                val = float(
                    _make_derived(sklearn.metrics.roc_auc_score)(
                        y_true,
                        y_score,
                        sensitive_features=sensitive_attributes[parsed_metric[2]],
                    )
                )
                return len(thresholds) * [val]

            case "avg_prec":
                # there is only 1 average precision, where there are multiple fpr or tpr
                # points -- so we repeat the average precision as many times as there are
                # thresholds to keep consistence.
                val = float(
                    _make_derived(sklearn.metrics.average_precision_score)(
                        y_true,
                        y_score,
                        sensitive_features=sensitive_attributes[parsed_metric[2]],
                    )
                )
                return len(thresholds) * [val]

    # this should not occur, as metric is parsed from start
    raise ValueError(f"Invalid metric specification: `{metric!r}`")
