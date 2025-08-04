.. SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _fairical.metrics:

===================
 Supported Metrics
===================

Utility
-------

Utility metrics are defined by the literal
:py:obj:`fairical.metrics.UtilityMetricsType`. The column named *Exclusive* indicates if
this utility metric can be used alone in system evaluations.  If not, one should ensure
to pick two (or more metrics) containing from **both** negative and positive samples.

============ ============= ============= =========== =============================================
 Metric       Range         Objective     Exclusive   Description
============ ============= ============= =========== =============================================
``fpr``      :math:`[0,1]`   minimize        no       `False positive rate <https://en.wikipedia.org/wiki/False_positive_rate>`_
``tpr``      :math:`[0,1]`   maximize        no       `True positive rate  (a.k.a. Recall) <https://en.wikipedia.org/wiki/True_positive_rate>`_
``tnr``      :math:`[0,1]`   maximize        no       `True negative rate <https://en.wikipedia.org/wiki/True_negative_rate>`_
``fnr``      :math:`[0,1]`   minimize        no       `False negative rate <https://en.wikipedia.org/wiki/False_negative_rate>`_
``roc_auc``  :math:`[0,1]`   maximize        yes      `Area under the ROC curve (FPR x TPR) <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html>`_
``prec``     :math:`[0,1]`   maximize        yes      `Precision <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_score.html>`_
``rec``      :math:`[0,1]`   maximize        no       `Recall (a.k.a. True positive rate) <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.recall_score.html>`_
``avg_prec`` :math:`[0,1]`   maximize        yes      `Average Precision (Area under the PR curve) <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html>`_
``f1``       :math:`[0,1]`   maximize        yes      `F1-score <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html>`_
``acc``      :math:`[0,1]`   maximize        yes      `Accuracy <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.accuracy_score.html>`_
``bal_acc``  :math:`[0,1]`   maximize        yes      `Balanced Accuracy <https://scikit-learn.org/stable/modules/generated/sklearn.metrics.balanced_accuracy_score.html>`_
============ ============= ============= =========== =============================================

Implementation of these metrics rely mostly on the ``scikit-learn`` toolkit
(:cite:t:`pedregosa_scikit_2011`).

Fairness
--------

Fairness metrics are defined by literals :py:obj:`fairical.metrics.FairnessMetricsType`
and :py:obj:`fairical.metrics.MinMaxFairnessMetricsType`. The first literal type includes
fairness metrics which are parameterised only by a protected attribute (such as ``age``,
or ``gender``).  The second class of fairness metrics correspond to min-max criteria
comparing specific utility metrics types (see above) between protected groups. It
therefore requires two parameters: The utility metric (as per table above), and a
protected attribute. Separate parameters of a metric using the ``+`` (plus sign).
Examples are provided on the next table.


============ ============= =================== ============= ============= =============================================
 Metric       Parameters    Example             Range         Objective     Description
============ ============= =================== ============= ============= =============================================
``dpd``       attribute     ``dpd+age``        :math:`[0,1]`   minimize     `Demographic parity difference <https://fairlearn.org/main/api_reference/generated/fairlearn.metrics.demographic_parity_difference.html>`_
``dpr``       attribute     ``dpr+age``        :math:`[0,1]`   maximize     `Demographic parity ratio <https://fairlearn.org/main/api_reference/generated/fairlearn.metrics.demographic_parity_ratio.html>`_
``eod``       attribute     ``eod+age``        :math:`[0,1]`   minimize     `Equalized odds difference <https://fairlearn.org/main/api_reference/generated/fairlearn.metrics.equalized_odds_difference.html>`_
``eor``       attribute     ``eod+age``        :math:`[0,1]`   maximize     `Equalized odds ratio <https://fairlearn.org/main/api_reference/generated/fairlearn.metrics.equalized_odds_ratio.html>`_
``minmaxd``  attr., util.  ``minmaxd+acc+age`` :math:`[0,1]`   minimize     `Min-Max difference <https://fairlearn.org/main/user_guide/assessment/custom_fairness_metrics.html#custom-fairness-metrics>`_
``minmaxr``  attr., util.  ``minmaxr+acc+age`` :math:`[0,1]`   maximize     `Min-Max ratio <https://fairlearn.org/main/user_guide/assessment/custom_fairness_metrics.html#custom-fairness-metrics>`_
============ ============= =================== ============= ============= =============================================

Implementation of these metrics rely on the ``fairlearn`` toolkit
(:cite:t:`weerts_fairlearn_2023`).
