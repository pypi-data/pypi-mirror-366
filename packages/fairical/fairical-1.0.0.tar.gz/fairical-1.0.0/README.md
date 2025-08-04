<!--
SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
SPDX-License-Identifier: GPL-3.0-or-later
-->

[![latest-docs](https://img.shields.io/badge/docs-v1.0.0-orange.svg)](https://fairical.readthedocs.io/en/v1.0.0/)
[![build](https://gitlab.idiap.ch/medai/software/fairical/badges/v1.0.0/pipeline.svg)](https://gitlab.idiap.ch/medai/software/fairical/commits/v1.0.0)
[![coverage](https://gitlab.idiap.ch/medai/software/fairical/badges/v1.0.0/coverage.svg)](https://www.idiap.ch/software/medai/docs/medai/software/fairical/v1.0.0/coverage/index.html)
[![repository](https://img.shields.io/badge/gitlab-project-0000c0.svg)](https://gitlab.idiap.ch/medai/software/fairical)

# Fairical

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

For installation and usage instructions, check-out our documentation.

If you use this library in published material, we kindly ask you to cite this work:

```bibtex
@misc{ozbulak_multi-objective_2025,
    title = {A Multi-Objective Evaluation Framework for Analyzing Utility-Fairness Trade-Offs in Machine Learning Systems},
    author = {Özbulak, Gökhan and Jimenez-del-Toro, Oscar and Fatoretto, Maíra and Berton, Lilian and Anjos, André},
    url = {https://arxiv.org/abs/2503.11120},
    doi = {10.48550/ARXIV.2503.11120},
    publisher = {{arXiv}},
    urldate = {2025-07-10},
    date = {2025},
}
```
