.. SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _fairical.usage.paper:

==================
 Further Examples
==================

This example reproduces the empirical findings reported at
:cite:t:`ozbulak_multi-objective_2025`, for an empirical setup using 3 metrics (one for
utility, and two other for demographic fairness for different attributes).

.. note:: **Obtaining sample data**

  This example requires you download sample data for two example ML systems. You can
  download them from these links:

  * :download:`system_1.json <_static/empirical/system_1.json>`
  * :download:`system_2.json <_static/empirical/system_2.json>`

  On the example below, we assume you downloaded/copied these files into a directory
  named ``empirical``.

.. testsetup:: other

   import os
   os.chdir("doc/usage/_static")

.. testcode:: other

   import numpy

   import fairical.scores

   thresholds = list(numpy.linspace(0, 1, 11, dtype=float))
   metrics = ["eod+race", "eod+gender", "acc"]

   scores1 = fairical.scores.Scores.load("empirical/system_1.json")
   scores2 = fairical.scores.Scores.load("empirical/system_2.json")

   sol1 = scores1.solutions(metrics, thresholds=thresholds).deduplicate()
   sol2 = scores2.solutions(metrics, thresholds=thresholds).deduplicate()

   indicators = {"system_1": sol1.indicators(), "system_2": sol2.indicators()}
   print(fairical.utils.make_table(indicators))

The resulting table is shown below:

.. testoutput:: other

     System    RELATIVE-ONVG    ONVGR    UD    AS    HV    Area
   --------  ---------------  -------  ----  ----  ----  ------
   system_1             0.86     0.35  0.70  0.16  0.76    0.28
   system_2             1.00     0.46  0.77  0.15  0.73    0.35

To plot a graphical representation of this table, do the following:

.. testcode:: other

   import fairical.plot
   fig, ax = fairical.plot.radar_chart(indicators)
   fig.savefig("radar-empiric.svg")

This code should generate a plot like the following:

.. image:: img/radar-empiric.svg
   :width: 80%
   :align: center
   :alt: Simple radar chart in SVG format

The corresponding 3-D Pareto plot can be obtained with:

.. testcode:: other

   nds_ds = {
       "system 1": sol1.non_dominated_solutions(),
       "system 2": sol2.non_dominated_solutions()
   }

   fig, ax = fairical.plot.pareto_plot(nds_ds)
   fig.savefig("pareto-empiric.svg")

This code should generate a plot like the following:

.. image:: img/pareto-empiric.svg
   :width: 80%
   :align: center
   :alt: 3-D pareto plot in SVG format

Already with 3 (metric) dimensions, it becomes difficult to analyze the estimated Pareto
front (non-dominated solutions).  You can animate the pareto plot to better visualize
the system surfaces in 3 dimensions:

.. code:: python

   from matplotlib.animation import FuncAnimation

   def update(frame):
       ax.view_init(elev=10, azim=frame)
       return (fig,)

   animation = FuncAnimation(fig, update, frames=360, interval=20)
   animation.save("pareto_animation.mp4", fps=30, extra_args=["-vcodec", "libx264"])

The generated animation for these systems is shown below:

.. image:: img/pareto_animation-empiric.gif
   :align: center
   :width: 80%

.. testcleanup:: other

   os.chdir("../../..")
