.. SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _fairical.install:

==============
 Installation
==============

Installation may follow one of two paths: deployment or development. Choose the
relevant section for details on each of those installation paths.


.. tab:: Deployment with uv

   Install using uv_, or your preferred Python project management solution.

   **Stable** release, from PyPI:

   .. code:: sh

      uv pip install fairical

   **Latest** development branch, from its git repository:

   .. code:: sh

      uv pip install git+https://gitlab.idiap.ch/medai/software/fairical@main


.. tab:: Development with pixi

   Checkout the repository, and then use pixi_ to setup a full development
   environment:

   .. code:: sh

      git clone git@gitlab.idiap.ch:medai/software/fairical
      pixi install --frozen

   .. tip::

      The ``--frozen`` flag will ensure that the latest lock-file available with sources is
      used.  If you'd like to update the lock-file to the latest set of compatible
      dependencies, remove that option.


.. include:: links.rst
