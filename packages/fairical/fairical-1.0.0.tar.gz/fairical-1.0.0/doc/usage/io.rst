.. SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _fairical.io:

=============
 I/O Formats
=============

Pydantic_ models for :py:class:`fairical.Scores` and :py:class:`fairical.Solutions` can
be created from or saved into JSON representations that can be stored on disk. When
loaded, JSON representations are validated against the pre-defined schema defined for
those objects.

Scores
------

As indicated in :ref:`fairical.datamodel`, :py:class:`fairical.Scores` correspond to the
primary input to :py:mod:`fairical`. A valid JSON for :py:class:`fairical.Scores`
consists of a dictionary composed of 3 keys:

- **scores:** A list of prediction scores for each Machine Learning (ML) model in
  consideration. Each model (or utility/fairness tradeoff) is represented with a single
  list of floats. A system that has multiple models (utility/fairness tradeoffs) is
  therefore represented by lists of lists of floats. An example of ``scores`` from a
  single-mode model, having predictions for 9 samples is shown below:

  .. code-block:: json

      {
          "scores": [
              [ 0.3970, 0.3434, 0.7074, 0.5787, 0.2451, 0.6383, 0.5937, 0.3629, 0.5526 ]
          ]
      }

  .. caution::

      Even in a single-mode model, prediction scores must be encapsulated within a list
      so that structure is represented as ``"scores": [[.]]``.

  Here is an example of a two-mode model, with predictions for 6 samples:

  .. code-block:: json

      {
          "scores": [
              [ 0.646910, 0.442378, 0.342101, 0.457198, 0.549640, 0.331999 ],
              [ 0.623593, 0.453462, 0.370829, 0.466496, 0.542477, 0.359879 ]
          ]
      }

  In this example, scores for the same underlying sample are paired across the two
  lists. The first entry of each list corresponds to the first sample in a list of test
  samples, the second to the second, and so on.

- **ground-truth:** A list of ground-truth labels paired to each sample in the list or
  lists in ``scores``. Given a binary classification task, an example of
  ``ground-truth`` list with nine test samples is shown below:

  .. code-block:: json

      {
          "ground-truth": [
              1, 0, 0, 0, 0, 0, 0, 1, 0
          ]
      }

- **attributes:** A dictionary of sensitive attributes with each having a list of values
  composed of integers or strings. Similarly to ``ground-truth``, this entry **must be
  paired** with the entries in ``scores`` and ``ground-truth``. An example of
  ``attributes`` dictionary for ``gender`` and ``race`` demographic groups with nine
  test samples is shown below:

  .. code-block:: json

      {
          "attributes": {
              "gender": [
                  "f", "m", "f", "m", "f", "f", "f", "m", "m"
              ],
              "race": [
                  2, 0, 0, 1, 0, 0, 1, 0, 2
              ]
          }
      }

  for a classification task where gender is ``{female, male}`` as two categories ``{"m",
  "f"}`` and race is ``{Asian, Black, White}`` as three categories ``{0, 1, 2}``.

A complete JSON representation for a single binary classifier analzyed for race with
nine test samples is examplified as below:

.. code-block:: json

    {
        "scores": [
            [ 0.5077, 0.5165, 0.5073, 0.4777, 0.6062, 0.4830, 0.7178, 0.7152, 0.4331 ]
        ],
        "ground-truth": [
                0, 0, 0, 1, 1, 0, 0, 0, 1
        ],
        "attributes": {
            "race": [
                1, 0, 2, 1, 0, 0, 2, 0, 0
            ]
        }
    }

.. _fairical.usage.io.solutions:

Solutions
---------

As indicated in :ref:`fairical.datamodel`, :py:class:`fairical.Solutions` correspond to
configurable :ref:`utility and fairness performance metrics <fairical.metrics>`
corresponding to operating-points of ML being analyzed, considering **all of its
operating modes** (trade-offs). :py:class:`fairical.Solutions` are computed by this
library from :py:class:`fairical.Scores` and therefore can be saved to a disk
representation, in JSON format.  The user may equally provide a solution JSON file with
pre-calculated OMs for analysis, under-cutting fairical solving.

A valid JSON representation for :py:class:`fairical.Solutions` has utility and fairness
metrics evaluated for all OMs of a model in consideration. An example JSON of an ML
system with multiple OMs (trade-offs) with one non-dominated solution (NDS) and two
dominated solutions (DS) is shown below:

.. code-block:: json

    {
        "eod+race": [ 0.104166, 1.0, 1.0 ],
        "eod+gender": [ 0.398741, 1.0, 1.0 ],
        "acc": [ 0.652702, 0.0, 0.0 ]
    }

Here, there one considers two fairness (Equalized Odds Difference for race and gender)
and one utility metric (accuracy).

.. note::

    Dominated solutions in the example are selected to reflect the worst values in
    dimensions of metrics (1.0 for eod and 0.0 for acc).

.. include:: ../links.rst
