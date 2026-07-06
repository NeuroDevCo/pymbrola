=====================
Installation
=====================

Requirements
=============

- Python 3.10 or higher
- `MBROLA <https://github.com/numediart/MBROLA>`_ binary
- MBROLA voices

Installing MBROLA
===================

MBROLA is currently available only on Linux-based systems like Ubuntu, or on Windows via the `Windows Subsystem for Linux (WSL) <https://learn.microsoft.com/en-us/windows/wsl/install>`_.

Using the install script:

.. code-block:: bash

   sudo bin/install.sh --voice fr2 it4  # install voices fr2 and it4
   sudo bin/install.sh --voice all      # install all voices
   sudo bin/install.sh                  # install no voices

Using Docker
=============

A `Docker image <https://hub.docker.com/repository/docker/gongcastro/pymbrola/general>`_ with a ready-to-go MBROLA installation is available:

.. code-block:: bash

   docker run -it gongcastro/pymbrola:latest

Installing pymbrola
====================

Install the Python package via pip:

.. code-block:: bash

   pip install mbrola

Verifying Installation
========================

To verify that pymbrola is correctly installed:

.. code-block:: python

   import mbrola
   print(mbrola.__version__)