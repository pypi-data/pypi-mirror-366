.. SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _fairical.usage.api:

=============
 API Example
=============

By directly accessing the :ref:`Fairical Python API <fairical.api>` you may use
functionality functionality of the library.  For example, all :ref:`fairical.cli`
provide a comprehensive correspondence in API, including further customisation
parameters.  You will find below the equivalent :ref:`fairical.usage.cli` directly using
the available API.

.. note::

  See :ref:`fairical.usage.cli` for obtaining sample data for this example.

.. testsetup:: api

   import os
   os.chdir("doc/usage/_static")

1. **Generate solutions or operating modes**:

   .. testcode:: api

      import numpy
      import fairical.scores

      thresholds = list(numpy.linspace(0, 1, 10, dtype=float))
      metrics = ["acc", "eod+gender"]

      scores1 = fairical.scores.Scores.load("sample/system_1.json")
      scores2 = fairical.scores.Scores.load("sample/system_2.json")

      sol1 = scores1.solutions(metrics, thresholds=thresholds).deduplicate()
      sol2 = scores2.solutions(metrics, thresholds=thresholds).deduplicate()

.. note:: **Save/load data**

   It's possible to save (or load) the solutions directly to (from) a JSON
   representation (see :ref:`fairical.usage.io.solutions`).

   .. testcode:: api

      import pathlib
      import tempfile

      with tempfile.TemporaryDirectory() as p:
          sol1.save(pathlib.Path(p) / "system_1.json")
          sol2.save(pathlib.Path(p) / "system_2.json")

2. **Evaluate indicators** (of estimated Pareto front - non-dominated solutions), print
   table and radar chart:

   .. testcode:: api

      import fairical.utils

      ind1 = sol1.indicators()
      ind2 = sol2.indicators()

      indicators = {"system 1": ind1, "system 2": ind2}
      table = fairical.utils.make_table(indicators, fmt="simple")
      print(table)

   .. testoutput:: api

            System    RELATIVE-ONVG    ONVGR    UD    AS    HV    Area
          --------  ---------------  -------  ----  ----  ----  ------
          system 1             1.00     0.33  0.66  0.15  0.70    0.29
          system 2             0.85     0.08  0.56  0.13  0.74    0.18

   To plot a graphical representation of this table, do the following:

   .. testcode:: api

      import fairical.plot
      fig, ax = fairical.plot.radar_chart(indicators)
      fig.savefig("radar.pdf")

   This code should generate a plot like the following:

   .. image:: img/radar.svg
      :width: 80%
      :align: center
      :alt: Simple radar chart in SVG format

3. **Visualize the Pareto front (estimate)**:

   .. testcode:: api

      nds_ds = {
          "system 1": sol1.non_dominated_solutions(),
          "system 2": sol2.non_dominated_solutions()
      }

      fig, ax = fairical.plot.pareto_plot(nds_ds)
      fig.savefig("pareto.pdf")

   This code should generate a plot like the following:

   .. image:: img/pareto.svg
      :width: 80%
      :align: center
      :alt: Simple pareto plot in SVG format

.. testcleanup:: api

   os.chdir("../../..")
