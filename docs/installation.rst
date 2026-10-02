=====================
Installation
=====================

You can install **pymbrola** from the `PyPi <https://pypi.org/project/mbrola/>__` repository using `pip <https://pypi.org/project/mbrola/>`__ or `uv <https://docs.astral.sh/uv/getting-started/installation/>`__:

.. code-block:: bash

   pip install mbrola # pip installation
   uv add mbrola      # uv installation

In either case, you will need Python>=3.10. To synthesise audios via MBROLA, you will need to download it and compile it. The **pymbrola** package has functions for this. This will download MBROLa from https://github.com/numediart/MBROLA to you home folder `~/.mbrola` and compile it.

.. code-block:: python
   import mbrola

   mbrola.install_mbrola()

.. admonition:: Platform compatibility
   :class: attention

   MBROLA is currently available only on Linux-based systems like Ubuntu, or on Windows via the `Windows Subsystem for Linux (WSL) <https://learn.microsoft.com/en-us/windows/wsl/install>`_. Native Windows and macOS are not yet compatible with the **pymbrola** package.

Finally, you will need to download some MBROLA voices from https://github.com/numediart/MBROLA-voices. These voices will be automatically downloaded and found by **pymbrola** at `~/.mbrola/Voices`:

.. code-block:: python

   mbrola.install_voice("it4")          # install it4 voice
   mbrola.install_voice(["it4", "fr4"]) # install several voices
   mbrola.install_voice()               # install all voices (~534M)


Using Docker
=============

A `Docker image <https://hub.docker.com/repository/docker/gongcastro/pymbrola/general>`_ with a ready-to-go MBROLA installation is available:

.. code-block:: bash

   docker run -it gongcastro/pymbrola:latest
