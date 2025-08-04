# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Plotting utilities."""

import itertools
import typing

import matplotlib.axes
import matplotlib.colors
import matplotlib.figure
import matplotlib.pyplot
import numpy

from .metrics import FairnessMetricsType, MinMaxFairnessMetricsType, UtilityMetricsType
from .solutions import Solutions
from .utils import IndicatorType, extend_indicators, parse_indicator


def radar_chart(
    indicators: dict[str, dict[IndicatorType, float]],
    axes: dict[IndicatorType | str, str] = {
        "relative-onvg": r"$\widehat{ONVG}$",
        "onvgr": r"$ONVGR$",
        "ud": r"$UD$",
        "as": r"$AS$",
        "hv": r"$HV$",
    },
) -> tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """Generate radar chart for all systems under comparison.

    This method generates radar chart given performance indicator values in comparison
    of systems. It requires the presence of ``complement-ud`` and ``relative-onvg`` on
    ``indicators``.

    Parameters
    ----------
    indicators
        Indicators organized in a single dictionary where keys represent system labels,
        and values, dictionaries with *at least* the same keys as listed in
        ``axes_keys``.
    axes
        A dictionary containing the indicator keys that will be drawn on the radar
        chart, and corresponding labels associated with each of those axes. You can use
        LaTeX symbols and notations on the values of the dictionary.
    title
        The plot title.
    **kwargs
        Additional keyword arguments for updating chart properties. Supported options:
        - linewidth: Line width
        - linestyle: Line style

    Returns
    -------
        A tuple containing both the matplotlib figure and axes used to create the radar
        chart.
    """

    _hatch_list = ["/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"]
    _hatch_cycle = itertools.cycle(_hatch_list)

    ndim = len(axes)

    # validate inputs
    assert ndim >= 3
    axes_ind: dict[IndicatorType, str] = {
        parse_indicator(k): v for k, v in axes.items()
    }

    extend_indicators(list(indicators.values()), list(axes_ind.keys()))

    values = numpy.array(
        [[v[k] for k in axes_ind.keys()] for v in indicators.values()], dtype=float
    )

    # concatenate the first column to last for looping
    values = numpy.column_stack((values, values[:, 0]))

    # draw plot
    angles = numpy.linspace(0, 2 * numpy.pi, values.shape[1], endpoint=True)
    fig, ax = matplotlib.pyplot.subplots(subplot_kw=dict(polar=True))
    labels = list(indicators.keys())

    for i, value in enumerate(values):
        # draws the line around each system entry
        (line,) = ax.plot(angles, value, label=labels[i])

        # fills the polygon
        ax.fill(angles, value, color=line.get_color(), alpha=0.25)

        # draws the hatching over the radar surface
        ax.fill(
            angles,
            value,
            color="none",
            edgecolor=line.get_color(),
            alpha=0.40,
            hatch=next(_hatch_cycle),
        )

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(axes.values())
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"])
    ax.tick_params(axis="both", which="major")
    ax.set_ylim(0, 1)

    ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, -0.2),  # “where that corner goes in axes coords”
        bbox_transform=ax.transAxes,
        ncol=len(indicators),  # spread entries horizontally
    )

    fig.tight_layout()

    return fig, ax


_AXES_LABELS_UTILITY: dict[UtilityMetricsType, str] = {
    "fpr": "Utility (FPR)",
    "tpr": "Utility (TPR)",
    "fnr": "Utility (FNR)",
    "tnr": "Utility (TNR)",
    "roc_auc": "Utility (AUROC)",
    "prec": "Utility (Precision)",
    "rec": "Utility (Recall)",
    "avg_prec": "Utility (Avg.Precision)",
    "f1": "Utility (F1-score)",
    "acc": "Utility (Accuracy)",
    "bal_acc": "Utility (Accuracy)",
}
"""Labels for pareto plots (utility)."""

_AXES_LABELS_FAIRNESS: dict[FairnessMetricsType, str] = {
    "dpd": "Fairness ($\\text{DPD}_\\text{%s})$",
    "dpr": "Fairness ($\\text{DPR}_\\text{%s})$",
    "eod": "Fairness ($\\text{EOD}_\\text{%s})$",
    "eor": "Fairness ($\\text{EOR}_\\text{%s})$",
}
"""Labels for pareto plots (fairness)."""

_AXES_LABELS_MINMAX_FAIRNESS: dict[MinMaxFairnessMetricsType, str] = {
    "minmaxd": "Min-Max Fairness (Diff. $\\text{%s}_\\text{%s})",
    "minmaxr": "Min-Max Fairness (Ratio $\\text{%s}_\\text{%s})",
}
"""Labels for pareto plots (min-max fairness)."""


def pareto_plot(
    solutions: dict[str, tuple[Solutions, Solutions]],
    axes_labels: dict[str, str] = {},
    alpha: float = 0.2,
) -> tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """Generate pareto plot for all systems under comparison.

    This method generates pareto plot given solutions of
    systems in comparison.

    Parameters
    ----------
    solutions
        A dictionary where keys represent system names (that will be used as labels),
        and values are tuples with non-dominated (nds) and dominated solutions (ds)
        respectively.
    axes_labels
        If specified, overwrites the default labels for dimensions in
        :py:class:`fairical.solutions.Solutions`. Should be a dictionary that maps the
        keys in each :py:class:`fairical.solutions.Solutions` object to a single label.
        If not set, then we use a default setup provided in the module.
    alpha
        Alpha blend between non-dominated (fully opaque) and dominated solutions (partly
        transparent).

    Returns
    -------
        A tuple containing both the matplotlib figure and axes used to create the pareto
        plot.
    """

    _marker_list = ["o", "s", "^", "v", "<", ">", "d", "P", "X", "*", "+"]
    _marker_cycle = itertools.cycle(_marker_list)

    ndim = next(iter(solutions.values()))[0].n_metrics()

    # validate inputs
    assert 2 <= ndim <= 3

    # draw plot, 2D and 3D are only possibiliies.
    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(projection="3d") if ndim == 3 else fig.add_subplot()

    for label, (nds, ds) in solutions.items():
        marker = next(_marker_cycle)

        # plot non-dominated points with no transparence
        nds_arr = numpy.asarray(nds)
        pc_nds = ax.scatter(
            *nds_arr.T,
            marker=marker,
        )

        fc = pc_nds.get_facecolors()
        the_color = fc[0] if len(fc) else pc_nds.get_edgecolors()[0]

        # plot dominated points using the same marker and color
        ds_arr = numpy.asarray(ds)
        ax.scatter(
            *ds_arr.T,
            color=the_color,
            alpha=alpha,
            marker=marker,
        )

        if nds_arr.shape[1] == 2:
            # sort by the first metric (x-axis) to get a sensible path
            order = numpy.argsort(nds_arr[:, 0])
            x_sorted, y_sorted = nds_arr[order].T
            ax.plot(
                x_sorted,
                y_sorted,
                linestyle="-",
                color=matplotlib.colors.to_rgba(the_color, alpha=min(2 * alpha, 1.0)),
                marker=marker,
                markerfacecolor=matplotlib.colors.to_rgba(the_color, alpha=1.0),
                linewidth=1,
                label=label,
            )
        else:
            # 3 dimensional case
            ax.plot_trisurf(
                *nds_arr.T,
                antialiased=False,
                shade=0,
                alpha=0.5,
                edgecolor="none",
            )

    # resolve which axes labels to use
    use_axes_labels: list[str] = []
    for k in next(iter(solutions.values()))[0].keys():
        if k in axes_labels:
            use_axes_labels.append(axes_labels[k])
        else:
            parts = k.split("+", 2)

            if parts[0] in typing.get_args(UtilityMetricsType):
                use_axes_labels.append(
                    _AXES_LABELS_UTILITY[typing.cast(UtilityMetricsType, parts[0])]
                )

            elif parts[0] in typing.get_args(FairnessMetricsType):
                use_axes_labels.append(
                    _AXES_LABELS_FAIRNESS[typing.cast(FairnessMetricsType, parts[0])]
                )
                if "%s" in use_axes_labels[-1]:
                    use_axes_labels[-1] = use_axes_labels[-1] % parts[1]

            elif parts[0] in typing.get_args(MinMaxFairnessMetricsType):
                use_axes_labels.append(
                    _AXES_LABELS_MINMAX_FAIRNESS[
                        typing.cast(MinMaxFairnessMetricsType, parts[0])
                    ]
                )
                if "%s" in use_axes_labels[-1]:
                    use_axes_labels[-1] = use_axes_labels[-1] % parts[1:]

    ax.set_xlabel(use_axes_labels[0])
    ax.set_ylabel(use_axes_labels[1])
    if ndim == 3:
        ax.set_zlabel(use_axes_labels[2])

    ax.grid()
    ax.legend(loc="best")

    fig.tight_layout()

    return fig, ax
