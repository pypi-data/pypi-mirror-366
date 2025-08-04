.. SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _fairical.usage.cli:

=============
 CLI Example
=============

Fairical provides :ref:`fairical.cli` to help generating and visualizing solutions to
evaluate the unified performance of Machine Learning (ML) systems under multiple utility
and fairness constraints. There are three stages to produce an assessment as shown next.

.. note:: **Obtaining sample data**

   The examples below require you download sample data for two ML systems. You can
   download them from these links:

   * :download:`system_1.json <_static/sample/system_1.json>`
   * :download:`system_2.json <_static/sample/system_2.json>`

   On the examples below, we assume you downloaded/copied these files into a directory
   named ``sample``.


1. **Generate solutions or operating modes** (`solve command
   <../cli.html#fairical-solve>`_): This step converts prediction scores of ML systems
   into metric operating modes (a.k.a. "solutions"). Here is an example of the solution
   generation for two systems with the ``accuracy`` and ``equalized odds difference``
   for the ``gender`` attribute, available inside the JSON files:

   .. code:: sh

      fairical solve -vv --thresholds=10 sample/system_{1,2}.json

   This step will generate two files on the current directory, with the same name as the
   input files, containing the operating modes of both system 1 and system 2.  You may
   inspect different options and their defaults by looking at the `solve command
   <../cli.html#fairical-solve>`_ documentation.

2. **Evaluate indicators** (`evaluate command <../cli.html#fairical-evaluate>`_): This
   step estimates the Pareto front formed by the operating modes (solutions) found on
   the previous step, and outputs 5 indicators that characterize that front.

   Here is an example for two systems whose solutions were calculated on the previous
   step:

   .. code:: sh

      fairical evaluate -vv system_{1,2}.json --radar radar.pdf

   This command generates a table like the one below:

   ========  ===============  =======  ====  ====  ====  ======
   System    RELATIVE-ONVG    ONVGR    UD    AS    HV    Area
   ========  ===============  =======  ====  ====  ====  ======
   system_1             1.00     0.33  0.66  0.15  0.70    0.29
   system_2             0.85     0.08  0.56  0.13  0.74    0.18
   ========  ===============  =======  ====  ====  ====  ======

   And, the radar chart, which displays a graphical representation of various
   indicators.

   .. image:: img/radar.svg
      :width: 80%
      :align: center
      :alt: Simple radar chart in SVG format

3. **Visualize the Pareto front (estimate)** (`plot command
   <../cli.html#fairical-plot>`_): You may *optionally* display the organization of
   non-dominated operating modes (solutions) on a plot, forming an estimated Pareto
   front. Naturally, this step is only possible when computing solutions for 2 or 3
   metrics at a time.

   Here is an example of this optional step:

   .. code:: sh

      fairical plot -vv system_{1,2}.json --pareto pareto.pdf

   This command should generate a plot like the following:

   .. image:: img/pareto.svg
      :width: 80%
      :align: center
      :alt: Simple pareto plot in SVG format
