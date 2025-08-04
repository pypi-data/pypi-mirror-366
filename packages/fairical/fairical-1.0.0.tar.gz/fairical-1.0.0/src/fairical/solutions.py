# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Define the basic solution data model and functionality."""

import logging
import pathlib
import typing

logger = logging.getLogger(__name__)

import numpy
import numpy.typing
import pydantic
import pymoo.config
import pymoo.indicators.hv
import pymoo.util.nds.non_dominated_sorting
import sklearn.cluster

from . import metrics, utils

# Supress pymoo warnings
pymoo.config.Config.show_compile_hint = False


def _hypervolume(
    nds: numpy.typing.NDArray[numpy.float64],
    nadir_point: numpy.typing.ArrayLike,
) -> float:
    r"""Calculate hyper-volume(hv) of non-dominated solutions.

    This method calculates convergence-diversity based on union of hypervolumes created
    by points from candidate solution set (non-dominated) and Nadir point. Higher is
    better.

    This indicator evaluates how the solution set covers the metric space in terms of
    diversity and proximity to the ideal. HV is formulated as:

    .. math::
        HV(S) = VOL\left(\bigcup_{\substack{x \in S \\ x \prec r}} \prod_{i=1}^{N}[x^{i},r^{i}]\right)

    Where :math:`x` is the solution set and :math:`r` is the Nadir point

    Parameters
    ----------
    nds
        Array with shape ``(n_solutions, n_objectives)`` containing the non-dominated
        solutions (NDS).  **All objectives are assumed to be minimised.**  If your
        problem involves maximisation, multiply the corresponding columns by ``-1``
        before calling.
    nadir_point
        Nadir point with shape ``(n_objectives,)``. Must **not** dominate any point in
        ``nds``.

    Returns
    -------
        The hyper-volume value.

    Raises
    ------
    ValueError
        If ``nadir_point`` is not an 1-D array or does not match with ``nds``.
    """

    nadir_point_ = numpy.asarray(nadir_point, dtype=float)

    # validation
    if nadir_point_.ndim != 1:
        raise ValueError("nadir_point must be a 1‑D array of shape (n_objectives,)")

    if nds.ndim != 2:
        raise ValueError("nds.ndim should be 2")

    if nds.shape[1] != nadir_point_.shape[0]:
        raise ValueError(
            f"nds.shape[1] ({nds.shape[1]}) should match nadir_point.shape[0]"
        )

    ind = pymoo.indicators.hv.Hypervolume(ref_point=nadir_point_)
    return ind._do(nds)


def _uniform_distribution(
    nds: numpy.typing.NDArray[numpy.float64], shared_dist: float = 0.01
) -> float:
    r"""Calculate Uniform Distribution (UD).

    This method calculates diversity/distribution based on distribution of
    non-dominated solutions found on trade-off surface. Lower is better.

    This indicator evaluates how uniform the solution set is spanned in the
    metric space based on an upper-bound distance, :math:`\sigma`. UD is formulated as:

    .. math::

       UD(S,\sigma)=\frac{1}{1+D_{nc}(S, \sigma)}

    Where

    .. math::

        D_{nc}(S,\sigma)=\sqrt{\frac{1}{|X_n|-1} \sum_{i=1}^{|X_n|} \left(nc(x^i,\sigma)-\mu_{nc(x,\sigma)}\right)^2}

    and

    .. math::

        nc(x^i,\sigma)=|\{x \in X_n, \|x-x^i\|<\sigma\}|-1

    :math:`\sigma` is the niche radius that is problem dependent and can be
    adjusted based on the distribution of the candidate solution in the space.
    :math:`\mu_{nc(x,\sigma)}` is the mean of the niche counts, :math:`nc`, calculated
    as :math:`\mu_{nc(x,\sigma)}=\frac{1}{|X_n|} \sum_{j=1}^{|X_n|} nc(x^j,\sigma)`.


    Parameters
    ----------
    nds
        Array with shape ``(n_solutions, n_objectives)`` containing the non-dominated
        solutions (NDS).  **All objectives are assumed to be minimised.**  If your
        problem involves maximisation, multiply the corresponding columns by ``-1``
        before calling.
    shared_dist
        Niche radius. Default is 0.01.

    Returns
    -------
        The uniform disttribution value.
    """

    if nds.ndim != 2:
        raise ValueError("nds.ndim should be 2")

    pf_size = len(nds)
    list_niches = numpy.zeros(pf_size)

    for i in range(0, pf_size):
        niche_count = 0

        for j in range(0, pf_size):
            if i != j:
                dist = numpy.linalg.norm(nds[i] - nds[j])
                niche_count += 1 if dist < shared_dist else 0

        list_niches[i] = niche_count

    niche_mean = numpy.mean(list_niches)

    # correction for the denominator of NaN
    if pf_size in [0, 1]:
        s_nc = 0.0
    else:
        s_nc = numpy.sqrt((numpy.sum((list_niches - niche_mean) ** 2)) / (pf_size - 1))

    return 1.0 / (1.0 + s_nc)


def _overall_spread(
    nds: numpy.typing.NDArray[numpy.float64],
    nadir_point: numpy.typing.ArrayLike,
    ideal_point: numpy.typing.ArrayLike,
) -> float:
    r"""Calculate overall pareto spread (OS).

    This method calculates diversity/spread based on how much extreme points are covered
    by Pareto Front approximation. Higher is better.

    This indicator assesses how well the points from the candidate set spreads towards
    the ideal of the optimal PF. OS is formulated as:

    .. math::
        OS(S,\mathcal{P})=\prod_{i=1}^{N}\left|\frac{\max\limits_{s \in S}s_i-\min\limits_{s \in S}s_i}{\max\limits_{p \in \mathcal{P}}p_{i}-\min\limits_{p \in \mathcal{P}}p_{i}}\right|

    Where the nominator and denominator are the absolute difference between the worst and
    best points for the candidate solution :math:`S` and Pareto optimal set :math:`\mathcal{P}`,
    respectively, on a particular metric dimension.


    Parameters
    ----------
    nds
        Array with shape ``(n_solutions, n_objectives)`` containing the non-dominated
        solutions (NDS).  **All objectives are assumed to be minimised.**  If your
        problem involves maximisation, multiply the corresponding columns by ``-1``
        before calling.
    nadir_point
        Nadir point with shape ``(n_objectives,)``. Must **not** dominate any point in
        ``nds``.
    ideal_point
        Reference point for the the ideal case where all objectives are fulfilled with
        shape ``(n_objectives,)``.  Must dominate any point in ``nds``.


    Returns
    -------
        The overall pareto spread value.

    Raises
    ------
    ValueError
        If ``nadir_point`` is not an 1-D array or does not match with ``nds``.
    """
    nadir_point_ = numpy.asarray(nadir_point, dtype=float)
    ideal_point_ = numpy.asarray(ideal_point, dtype=float)

    # validate
    if nds.size == 0:
        raise ValueError("nds must be non-empty.")

    if nds.ndim != 2:
        raise ValueError("nds.ndim should be 2")

    if nadir_point_.ndim != 1:
        raise ValueError(
            "nadir_point must be a 1‑D array‑like of shape (n_objectives,)."
        )

    if ideal_point_.ndim != 1:
        raise ValueError(
            "nadir_point must be a 1‑D array‑like of shape (n_objectives,)."
        )

    if nds.shape[1] != nadir_point_.shape[0]:
        raise ValueError(
            "The shape of nds.shape[1] and nadir_point.shape[0] should match."
        )

    if ideal_point_.shape[0] != nadir_point_.shape[0]:
        raise ValueError(
            "The shape of ideal_point.shape[0] and nadir_point.shape[0] should match."
        )

    numerator = nds.max(axis=0) - nds.min(axis=0)
    denominator = nadir_point_ - ideal_point_

    return numpy.prod(numerator / denominator)


def _average_spread(
    nds: numpy.typing.NDArray[numpy.float64],
    nadir_point: numpy.typing.ArrayLike,
    ideal_point: numpy.typing.ArrayLike,
) -> float:
    r"""Calculate average pareto spread (AS).

    This method calculates diversity/spread based on how much extreme points are covered
    by Pareto Front approximation. Higher is better.

    This indicator assesses how well the points from the candidate set spreads towards
    the ideal of the optimal PF. AS is formulated as:

    .. math::
        AS(S,\mathcal{P})=\frac{1}{N}\sum_{i=1}^{N}\left|\frac{\max\limits_{s \in S}s_i-\min\limits_{s \in S}s_i}{\max\limits_{p \in \mathcal{P}}p_{i}-\min\limits_{p \in \mathcal{P}}p_{i}}\right|

    Where the nominator and denominator are the absolute difference between the worst and
    best points for the candidate solution :math:`S` and Pareto optimal set :math:`\mathcal{P}`,
    respectively, on a particular metric dimension.


    Parameters
    ----------
    nds
        Array with shape ``(n_solutions, n_objectives)`` containing the non-dominated
        solutions (NDS).  **All objectives are assumed to be minimised.**  If your
        problem involves maximisation, multiply the corresponding columns by ``-1``
        before calling.
    nadir_point
        Nadir point with shape ``(n_objectives,)``. Must **not** dominate any point in
        ``nds``.
    ideal_point
        Reference point for the the ideal case where all objectives are fulfilled with
        shape ``(n_objectives,)``.  Must dominate any point in ``nds``.


    Returns
    -------
        The overall pareto spread value.

    Raises
    ------
    ValueError
        If ``nadir_point`` is not an 1-D array or does not match with ``nds``.
    """
    nadir_point_ = numpy.asarray(nadir_point, dtype=float)
    ideal_point_ = numpy.asarray(ideal_point, dtype=float)

    # validate
    if nds.size == 0:
        raise ValueError("nds must be non-empty.")

    if nds.ndim != 2:
        raise ValueError("nds.ndim should be 2")

    if nadir_point_.ndim != 1:
        raise ValueError(
            "nadir_point must be a 1‑D array‑like of shape (n_objectives,)."
        )

    if ideal_point_.ndim != 1:
        raise ValueError(
            "nadir_point must be a 1‑D array‑like of shape (n_objectives,)."
        )

    if nds.shape[1] != nadir_point_.shape[0]:
        raise ValueError(
            "The shape of nds.shape[1] and nadir_point.shape[0] should match."
        )

    if ideal_point_.shape[0] != nadir_point_.shape[0]:
        raise ValueError(
            "The shape of ideal_point.shape[0] and nadir_point.shape[0] should match."
        )

    numerator = nds.max(axis=0) - nds.min(axis=0)
    denominator = nadir_point_ - ideal_point_

    return numpy.average(numerator / denominator)


class Solutions(pydantic.RootModel):
    """Data model representing system solutions (or utility/fairness trade-offs).

    Objects of this type carry information about two or more performance metrics
    (utility or fairness) for each operating mode (utility/fairness trade-off) of the
    analysed ML system.

    It is a dictionary where keys correspond to utility or fairness metrics calculated
    for the whole system, and values across different keys represent each the
    performance at a particular operating mode (utility/fairness trade-off) the system
    being analysed can potentially implement.
    """

    root: dict[str, list[typing.Annotated[float, pydantic.Field(ge=0.0, le=1.0)]]] = (
        pydantic.Field(
            ...,
            description="One or many lists of solution coordinates representing "
            "different operating points of the system being analyzed.",
        )
    )

    # --- Mapping API methods ---------------------------------------

    def __getitem__(self, key: str) -> list[float]:
        """Retrieve the list of floats associated with the given metric key.

        Parameters
        ----------
        key
            The metric name to look up.

        Returns
        -------
            The solution vector for the specified metric.

        Raises
        ------
        KeyError
            If the metric key is not present in the model.
        """
        return self.root[key]

    def __len__(self) -> int:
        """Return the number of metrics stored in the model.

        Returns
        -------
            The count of metric keys in the model.
        """
        return len(self.root)

    n_metrics = __len__

    def n_solutions(self) -> int:
        """Return the number of solutions stored in the model, across all metrics.

        Returns
        -------
            The number of solutions in the model, across all metrics.
        """
        return len(next(iter(self.root.values())))

    def items(self) -> typing.ItemsView[str, list[float]]:
        """Return a view of metric keys and their associated solution vectors.

        Returns
        -------
            A set-like view of (metric, vector) pairs.
        """
        return self.root.items()

    def keys(self) -> typing.KeysView[str]:
        """Return a view of the metric keys.

        Returns
        -------
            A set-like view of metric names.
        """
        return self.root.keys()

    def values(self) -> typing.ValuesView[list[float]]:
        """Return a view of all solution vectors.

        Returns
        -------
            A view of all metric solution vectors in the model.
        """
        return self.root.values()

    def __array__(self) -> numpy.typing.NDArray[numpy.float64]:
        """Allow numpy to convert this model directly into an (n_solutions, n_metrics) array.

        Each row is one solution; columns follow the insertion order of the metric keys.

        Parameters
        ----------
        dtype
            Optional dtype

        Returns
        -------
            A newly created and validated object.
        """
        # stack columns in the order of self.keys()
        return numpy.stack(
            [self.root[k] for k in self.keys()], axis=1, dtype=numpy.float64
        )

    @classmethod
    def fromarray(
        cls, data: numpy.typing.ArrayLike, metrics: typing.Sequence[str]
    ) -> typing.Self:
        """Create a new instance from an array and names of metrics.

        Parameters
        ----------
        data
            2-D array-like object with floating-point numbers organized as
            ``(n_solutions, n_metrics)``.
        metrics
            A set of strictly **valid and supported** metrics, each representing the
            columns of the input data array.

        Returns
        -------
            A newly created and validated object.

        Raises
        ------
        AssertionError
            If the number of columns on the input array-like object is different than
            the number of listed metrics.
        """
        data_arr = numpy.asarray(data, dtype=numpy.float64)
        assert data_arr.shape[1] == len(metrics)
        return cls.model_validate(dict(zip(metrics, data_arr.T)))

    @classmethod
    def load(cls, source: pathlib.Path | str | typing.TextIO) -> typing.Self:
        """Validate and load a JSON file into a solution data object.

        This function is intended to validate and load the input in JSON format. It opens
        the given file path, parses its JSON content, and validates it against the defined
        model.

        Parameters
        ----------
        source
            Source input where to read JSON from.

        Returns
        -------
            Parsed and validated content as a :py:class:`Solutions` instance.

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

    @pydantic.model_validator(mode="after")
    def check_metrics_validity(self) -> typing.Self:
        """Ensure all metrics are valid."""

        invalid = []
        parsed: list[
            metrics.UtilityMetricsType
            | tuple[metrics.FairnessMetricsType, str]
            | tuple[metrics.MinMaxFairnessMetricsType, metrics.UtilityMetricsType, str]
        ] = []
        for name in self.root.keys():
            try:
                parsed.append(metrics.parse_metric(name))
            except ValueError:
                invalid.append(f"`{name}`")

        if invalid:
            raise ValueError(f"invalid metric names: {', '.join(invalid)}")

        # cannot have utility metrics relying on statistics from a single utility group
        # (positives or negatives), as those will generate misleading results -- see
        # discussion at: https://gitlab.idiap.ch/medai/software/fairical/-/merge_requests/4
        utility_metrics: list[metrics.UtilityMetricsType] = [
            typing.cast(metrics.UtilityMetricsType, k)
            for k in parsed
            if k in typing.get_args(metrics.UtilityMetricsType)
        ]
        if len(utility_metrics) == 1:
            if utility_metrics[0] in ("fpr", "tpr", "fnr", "tnr", "rec"):
                raise ValueError(
                    f"cannot use `{utility_metrics[0]}` as the sole utility metrics "
                    f"for analysis - it generates biased results at extreme thresholds"
                )
        elif len(utility_metrics) == 2:
            forbidden_groups = [
                set(k) for k in [("fpr", "tnr"), ("fnr", "tpr"), ("fnr", "rec")]
            ]
            if set(utility_metrics) in forbidden_groups:
                raise ValueError(
                    f"cannot use the pair `{utility_metrics}` as the sole utility "
                    f"metrics for analysis as both measures belong to the same "
                    f"group -- it generates biased results at extreme thresholds"
                )

        return self

    @pydantic.model_validator(mode="after")
    def check_consistent_lengths(self) -> typing.Self:
        """Ensure all solution lists have the same length."""

        expected = len(next(iter(self.root.values())))

        for key, value in self.root.items():
            if len(value) != expected:
                raise ValueError(f"solutions[{key}] length {len(value)} != {expected}")

        return self

    def deduplicate(self, eps: float = 1e-6) -> typing.Self:
        """Filter solutions to remove duplicates within a certain epsilon.

        Remove points in these solutions that lie within ``eps`` of another by
        clustering with :py:class:`sklearn.cluster.DBSCAN` (min_samples=1) and keeping
        the first point in each cluster.

        Parameters
        ----------
        eps
            Maximum distance between points in the same cluster.

        Returns
        -------
            Filtered solutions without duplicates, as a new object.
        """
        dims = list(self.root.keys())
        data = numpy.vstack([self.root[d] for d in dims]).T

        labels = sklearn.cluster.DBSCAN(
            eps=eps, min_samples=1, metric="euclidean"
        ).fit_predict(data)

        # pick the first index for each label
        _, first_idx = numpy.unique(labels, return_index=True)
        filtered = data[numpy.sort(first_idx)]

        logger.info(
            f"Deduplication reduced solutions {self.n_solutions()} -> {len(filtered)}"
        )

        return self.model_validate(
            {dim: filtered[:, idx].tolist() for idx, dim in enumerate(dims)}
        )

    def non_dominated_solutions(self) -> tuple[typing.Self, typing.Self]:
        """Filter solutions from system that are non-dominated.

        This is a thin wrapper around :py:class:`pymoo.util.nds.NonDominatedSorting` that
        extracts the *rank‑0* solutions (those that are not dominated by any other).

        **Definition**: A point p is dominated only if one single competitor is no worse in
        every objective and strictly better in at least one.

        Parameters
        ----------
        solutions
            All solutions available in the current system.

        Returns
        -------
            A tuple containing non-dominated and dominated solutions respectively. By
            definition, the sets are guaranteed to not overlap.
        """

        # calculation of non-dominated solutions requires all axes to be set as one is
        # minimizing on every direction.
        data = numpy.asarray(self)
        for k, metric in enumerate(self.root.keys()):
            if not metrics.should_minimize(metric):
                data[:, k] *= -1

        algo = pymoo.util.nds.non_dominated_sorting.NonDominatedSorting()
        nds_idx = typing.cast(
            set[int], set(algo.do(data, only_non_dominated_front=True))
        )
        ds_idx = set(range(self.n_solutions())) - nds_idx

        def filter_by_indices(indices):
            return {k: [self.root[k][i] for i in indices] for k in self.root.keys()}

        nds = self.model_validate(filter_by_indices(sorted(nds_idx)))
        ds = self.model_validate(filter_by_indices(sorted(ds_idx)))

        logger.info(
            f"Non-dominated/Dominated solutions {nds.n_solutions()}/{ds.n_solutions()}"
        )

        return nds, ds

    def indicators(self) -> dict[utils.IndicatorType, float]:
        r"""Assess utility-fairness trade-off systems based on characteristics of the
        estimated Pareto front.

        This method evaluates trade-off between utiltiy and fairness of adjustable systems
        by using Multi-Objective based performance indicators. It first estimates the
        set of non-dominated solutions.

        Returns
        -------
            A dictionary that characterizes the (estimated Pareto) front composed of
            non-dominated solutions in ``nds``. The dictionary contains the following keys:

            * ``hv``: The hypervolume of the front.

              Higher is better. This indicator evaluates how the solution set covers the
              metric space in terms of diversity and proximity to the ideal. HV is
              formulated as:

              .. math::
                  HV(S) = VOL\left(\bigcup_{\substack{x \in S \\ x \prec r}} \prod_{i=1}^{N}[x^{i},r^{i}]\right)

              Where :math:`x` is the solution set and :math:`r` is the Nadir point

            * ``ud``: Uniformity of the distribution of ``nds`` points on the front.

              This indicator evaluates how uniform the solution set is spanned in the
              metric space based on an upper-bound distance, :math:`\sigma`. UD is
              formulated as:

              .. math::

                 UD(S,\sigma)=\frac{1}{1+D_{nc}(S, \sigma)}

              Where

              .. math::

                  D_{nc}(S,\sigma)=\sqrt{\frac{1}{|X_n|-1} \sum_{i=1}^{|X_n|} \left(nc(x^i,\sigma)-\mu_{nc(x,\sigma)}\right)^2}

              and

              .. math::

                  nc(x^i,\sigma)=|\{x \in X_n, \|x-x^i\|<\sigma\}|-1

              :math:`\sigma` is the niche radius that is problem dependent and can be
              adjusted based on the distribution of the candidate solution in the space.
              :math:`\mu_{nc(x,\sigma)}` is the mean of the niche counts, :math:`nc`,
              calculated as :math:`\mu_{nc(x,\sigma)}=\frac{1}{|X_n|} \sum_{j=1}^{|X_n|}
              nc(x^j,\sigma)`.

            * ``os``: Overall spread of ``nds`` points with respect to extremities of the front.

              This indicator assesses how well the points from the candidate set spreads
              towards the ideal of the optimal PF. OS is formulated as:

              .. math::
                  OS(S,\mathcal{P})=\prod_{i=1}^{N}\left|\frac{\max\limits_{s \in S}s_i-\min\limits_{s \in S}s_i}{\max\limits_{p \in \mathcal{P}}p_{i}-\min\limits_{p \in \mathcal{P}}p_{i}}\right|

              Where the nominator and denominator are the absolute difference between
              the worst and best points for the candidate solution :math:`S` and Pareto
              optimal set :math:`\mathcal{P}`, respectively.

            * ``as``: Average spread of ``nds`` points with respect to extremities of the front.

              This indicator assesses how well the points from the candidate set spreads
              towards the ideal of the optimal PF. AS is formulated as:

              .. math::
                  AS(S,\mathcal{P})=\frac{1}{N}\sum_{i=1}^{N}\left|\frac{\max\limits_{s \in S}s_i-\min\limits_{s \in S}s_i}{\max\limits_{p \in \mathcal{P}}p_{i}-\min\limits_{p \in \mathcal{P}}p_{i}}\right|

              Where the nominator and denominator are the absolute difference between
              the worst and best points for the candidate solution :math:`S` and Pareto
              optimal set :math:`\mathcal{P}`, respectively.

            * ``onvg``: Overall Nondominated Vector Generation (ONVG) in the front
              (``nds``).

              Higher is better. This indicator evaluates how many optimal solutions are
              generated by the system. ONVG is formulated as:

              .. math::
                  ONVG(S) = |X_n|

              Where :math:`|.|` is the cardinality of the candidate solution set in the metric space.

            * ``onvgr``: Ratio between number of solutions in ``nds`` and ``nds + ds``.

              Higher is better. This indicator assesses the proportion of optimal solutions
              generated by the system. ONVGR is formulated as:

              .. math::
                  ONVGR(S) = \left|\frac{X_n}{S}\right|

              Where :math:`|.|` is the ratio of the optimality.
        """

        assert len(self.root) >= 2, (
            "cannot extract indicators on solutions with a single dimension"
        )

        nds, ds = self.non_dominated_solutions()

        # calculate indicators
        retval: dict[utils.IndicatorType, float] = {}
        nds_arr = numpy.asarray(nds)

        # use the complement to 1.0, to everything we need to maximize so we can keep
        # using (1, 1, ...) as a fixed nadir point, and (0, 0, ...) for the ideal point.
        for k, metric in enumerate(self.root.keys()):
            if not metrics.should_minimize(metric):
                nds_arr[:, k] *= -1
                nds_arr[:, k] += 1

        nadir_point = len(self) * (1.0,)  # dominated by any point in nds
        ideal_point = len(self) * (0.0,)  # dominates all points in nds

        retval["hv"] = _hypervolume(nds_arr, nadir_point)
        retval["ud"] = _uniform_distribution(nds_arr, shared_dist=0.01)
        retval["os"] = _overall_spread(nds_arr, nadir_point, ideal_point)
        retval["as"] = _average_spread(nds_arr, nadir_point, ideal_point)
        retval["onvg"] = float(nds.n_solutions())
        retval["onvgr"] = float(
            nds.n_solutions() / (nds.n_solutions() + ds.n_solutions())
        )

        return retval
