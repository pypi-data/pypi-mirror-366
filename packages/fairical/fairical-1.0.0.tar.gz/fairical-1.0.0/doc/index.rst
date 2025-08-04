.. SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _fairical:

==========
 Fairical
==========

.. todolist::

Fairical is a Python library for rigorously evaluating and comparing demographically
fair machine-learning systems through the lens of multi-objective optimization. Rather
than treating fairness as a single constraint, Fairical recognizes that real-world
deployments must balance multiple, often conflicting fairness metrics (e.g., demographic
parity, equalized odds across race, gender, age) alongside traditional utility measures
like accuracy. It implements a model-agnostic evaluation framework that approximates
Pareto fronts of utility-fairness trade-offs, then distills each system's performance
into a compact measurement table and radar chart. By calculating convergence (how close
models get to optimal trade-offs), diversity (uniform distribution and spread of
solutions), capacity (number of non-dominated points), and a unified
convergence-diversity score via hypervolume, Fairical delivers both quantitative rigor
and qualitative clarity.

.. image:: usage/img/radar.svg
   :width: 49%
.. image:: usage/img/pareto.svg
   :width: 49%


Built for both black-box and white-box analyses, Fairical seamlessly ingests prediction
outputs or tunable model scores to generate N-dimensional trade-off approximations. It
supports any combination of utility and fairness metrics, normalizing all indicators to
a [0,1] scale for intuitive comparison. Side-by-side visualizations—radar charts and
Pareto front plots—make it easy to spot which strategies offer the best compromise under
given fairness requirements.

If you use this library in published material, we kindly ask you to cite this work:

.. code:: bibtex

   @misc{ozbulak_multi-objective_2025,
       title = {A Multi-Objective Evaluation Framework for Analyzing Utility-Fairness Trade-Offs in Machine Learning Systems},
       author = {Özbulak, Gökhan and Jimenez-del-Toro, Oscar and Fatoretto, Maíra and Berton, Lilian and Anjos, André},
       url = {https://arxiv.org/abs/2503.11120},
       doi = {10.48550/ARXIV.2503.11120},
       publisher = {{arXiv}},
       urldate = {2025-07-10},
       date = {2025},
   }


Documentation
-------------

.. toctree::
   :maxdepth: 2

   install
   datamodel
   usage/index
   api
   cli
   bibliography


.. include:: links.rst
