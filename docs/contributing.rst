==============
Contributing
==============

We welcome contributions to pymbrola! Here's how you can help:

Getting Started
================

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or fix
4. Make your changes
5. Submit a pull request

Development Setup
==================

Install development dependencies:

.. code-block:: bash

   pip install -e ".[dev]"

Running Tests
==============

Run the test suite:

.. code-block:: bash

   pytest

Run tests with coverage:

.. code-block:: bash

   pytest --cov=mbrola

Code Style
===========

We use `ruff <https://github.com/astral-sh/ruff>`_ for linting. Format your code:

.. code-block:: bash

   ruff check --fix .

Building Documentation
=======================

Build the documentation locally:

.. code-block:: bash

   cd docs
   make html

The built documentation will be available in ``_build/html/``.

License
========

By contributing to pymbrola, you agree that your contributions will be licensed under its MIT License.