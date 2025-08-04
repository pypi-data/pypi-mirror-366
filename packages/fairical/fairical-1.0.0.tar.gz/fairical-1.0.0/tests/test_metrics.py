# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import typing

import numpy

import fairical.metrics

# Example extracted from:
# https://fairlearn.org/v0.12/user_guide/assessment/common_fairness_metrics.html#common-fairness-metrics
y_true = [0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1]
y_pred = [0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0]
sf_data = [
    "b",
    "b",
    "a",
    "b",
    "b",
    "c",
    "c",
    "c",
    "a",
    "a",
    "c",
    "a",
    "b",
    "c",
    "c",
    "b",
    "c",
    "c",
]


def test_dpd():
    r = fairical.metrics.calculate_metric(
        "dpd+foo",
        y_true,
        y_pred,
        thresholds=[0.5],
        sensitive_attributes={"foo": sf_data},
    )

    assert len(r) == 1
    assert numpy.isclose(r, 0.25)


def test_dpr():
    r = fairical.metrics.calculate_metric(
        "dpr+foo",
        y_true,
        y_pred,
        thresholds=[0.5],
        sensitive_attributes={"foo": sf_data},
    )

    assert len(r) == 1
    assert numpy.isclose(r, 0.666666666)


def test_eod():
    r = fairical.metrics.calculate_metric(
        "eod+foo",
        y_true,
        y_pred,
        thresholds=[0.5],
        sensitive_attributes={"foo": sf_data},
    )

    assert len(r) == 1
    assert numpy.isclose(r, 1.00)


def test_eor():
    r = fairical.metrics.calculate_metric(
        "eor+foo",
        y_true,
        y_pred,
        thresholds=[0.5],
        sensitive_attributes={"foo": sf_data},
    )

    assert len(r) == 1
    assert numpy.isclose(r, 0.0)


def test_minmaxd_recall():
    r = fairical.metrics.calculate_metric(
        "minmaxd+rec+foo",
        y_true,
        y_pred,
        thresholds=[0.5],
        sensitive_attributes={"foo": sf_data},
    )

    assert len(r) == 1
    assert numpy.isclose(r, 0.1999999)


def test_minmaxr_recall():
    r = fairical.metrics.calculate_metric(
        "minmaxr+rec+foo",
        y_true,
        y_pred,
        thresholds=[0.5],
        sensitive_attributes={"foo": sf_data},
    )

    assert len(r) == 1
    assert numpy.isclose(r, 0.666667)


def test_should_minimize():
    for k in typing.get_args(fairical.metrics.UtilityMetricsType):
        if k in ("fnr", "fpr"):
            assert fairical.metrics.should_minimize(k)
        else:
            assert not fairical.metrics.should_minimize(k)

    for k in typing.get_args(fairical.metrics.FairnessMetricsType):
        if k in ("eod", "dpd"):
            assert fairical.metrics.should_minimize(k + "+foo")
        else:
            assert not fairical.metrics.should_minimize(k + "+foo")

    for k in typing.get_args(fairical.metrics.MinMaxFairnessMetricsType):
        if k == "minmaxd":
            assert fairical.metrics.should_minimize(k + "+rec+foo")
        else:
            assert not fairical.metrics.should_minimize(k + "+roc_auc+foo")
