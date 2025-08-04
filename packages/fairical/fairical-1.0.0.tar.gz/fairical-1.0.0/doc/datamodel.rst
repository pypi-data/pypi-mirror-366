.. SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _fairical.datamodel:

=============
 Data Models
=============

This library uses two primary data models defined via pydantic_:
:py:class:`fairical.Scores` and :py:class:`fairical.Solutions`. These models form the
backbone of the multi-objective fairness assessment workflow for machine learning (ML)
systems.

The :py:class:`fairical.Scores` model holds the raw outputs from machine learning
systems, **you must provide to the library**. Multiple sets of scores represent
different *operating modes* (utility/fairness trade-off) of a machine learning system.
Operating models correspond to utility-fairness trade-offs that can be adjusted *a
posteriori*, after the system has been trained. Examples of adjustments that can affect
the utility-fairness trade-off in an ML system can be the threshold at which positive
and negative samples are classified, or any other selection mechanisms on systems that
can be tuned *a posteriori* to modify their behaviour (e.g. Pareto Hyper-networks,
:cite:t:`navon_learning_2021`, or You-Only-Train-Once models,
:cite:t:`dosovitskiy_you_2020`).

The :py:class:`fairical.Solutions` model holds intermediary data produced by this
library. It carries information about two or more performance metrics (utility or
fairness) for each operating mode (utility/fairness trade-off) of the analysed ML
system.

This library assumes you can create a JSON or Python representation of
:py:class:`fairical.Scores` direclty from your ML framework. You can then either use the
:ref:`fairical.api` or :ref:`fairical.cli` to transform :py:class:`fairical.Scores` into
:py:class:`fairical.Solutions`, and then into tabled results and plots, as discussed in
:ref:`fairical.usage`.

The data model implemented in this package is summarized in the following figure:

.. image:: img/datamodel-lite.svg
   :align: center
   :class: only-light

.. image:: img/datamodel-dark.svg
   :align: center
   :class: only-dark

In the :ref:`next section <fairical.usage>`, we explore use-cases that exemplify the use
of the :ref:`fairical.api` and :ref:`fairical.cli` to convert dataset scores,
ground-truth and protected attributes into summary tables and visualisations.

.. include:: links.rst
