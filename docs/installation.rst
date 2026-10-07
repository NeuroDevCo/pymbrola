=====================
Installation
=====================

You can install **pymbrola** from the `PyPi <https://pypi.org/project/mbrola/>`__ repository using `pip <https://pypi.org/project/mbrola/>`__ or `uv <https://docs.astral.sh/uv/getting-started/installation/>`__:

.. code-block:: bash

   pip install mbrola # pip installation
   uv add mbrola      # uv installation

In either case, you will need Python>=3.10. To synthesise audios via MBROLA, you will need to download it and compile it. The **pymbrola** package has functions for this, which will download MBROLA from https://github.com/numediart/MBROLA to you home folder `~/.mbrola` and compile it.

.. code-block:: python
  from pymbrola import install

   install.install_mbrola()

You will also need to download some MBROLA voices from https://github.com/numediart/MBROLA-voices. These voices will be automatically downloaded and found by **pymbrola** at `~/.mbrola/Voices`:

.. code-block:: python

   install.install_voice("it4")          # install it4 voice
   install.install_voice(["it4", "fr4"]) # install several voices
   install.install_voice()               # install all voices (~534M)


.. admonition:: Platform compatibility
   :class: attention

   MBROLA is currently available only on Linux-based systems like Ubuntu, or on Windows via the `Windows Subsystem for Linux (WSL) <https://learn.microsoft.com/en-us/windows/wsl/install>`_. Native Windows and macOS are not yet compatible with the **pymbrola** package. If your are a Windows user, please see :ref:`windows-section` section.

.. _windows-section:

Windows users
=============

Because compiling MBROLA in a Windows machine is somewhat complicated, **pymbrola** only supports Linux-based operative systems. If you are a Windows user there are two ways in which you could use **pymbrola**: :ref:`docker-section` and :ref:`wsl-section`.

.. _docker-section:

Docker
------

Install `Docker Desktop <https://docs.docker.com/desktop/setup/install/windows-install/>`__ in you machine, then run the following command in your terminal making sure Docker engine is running (having Docker Desktop open usually does it): 

.. code-block:: bash
  :linenos:

    docker run -it -v "./.mbrola/output:/pymbrola/output" gongcastro/pymbrola:latest

This command will download the **gongcastro/pymbrola** Docker image from `DockerHub <https://hub.docker.com/repository/docker/gongcastro/pymbrola>`__ if necessary, then run it in a container. The result will be a Python session open in the terminal, in which you will be able to import the `mbrola` module. Once the container is running in your terminal, you may want to first run ``mbrola.install_mbrola()`` and ``mbola_install_voice("it4")``, replacing ``"it4"`` with whichever voice or voices you are planning to use. For example:

.. code-block:: python
  :linenos:

  from pymbrola import install, mbrola

  install.install_mbrola()
  install.install_voice(["it4", "fr4"])

  mbrola.MBROLA("kaffE").to_sound("output/kaffE.wav", voice="it4")
    
In order to be able to reach the generated files after you are done with the Docker container, a volume from your local host machine is attached to the container(``-v "./.mbrola/output:/pymbrola/output"``), so that any files generated inside it under the folder ``./output`` will be persistently saved in the host machine wherever the path ``./.mbrola/output`` (the dot ``"."`` usually in the same folder in which you opened in your temrinal before running Docker). To change the destination folder in your host machine, change ``./.mbrola/output`` for any other path of your preference. This is where you will find your synthesised files after closing your Docker container.

.. admonition:: Running the Docker image in Linux
  :class: hint

  If you are running the Docker image in a Linux distribution, you might need to start the container with setting some user permission:
    
  .. code-block:: bash
    :linenos:

    docker run -it --user "$(id -u):$(id -g)" -v "./.mbrola/output:/pymbrola/output" gongcastro/pymbrola:latest

.. _wsl-section:

Windows Subsystem for Linux (WSL)
---------------------------------

If you want to use `Windows Subsystem for Linux (WSL) <https://learn.microsoft.com/en-us/windows/wsl/about>`__ to run **pymbrola** inside Windows, make sure first that your WSL installation is up and working:

.. code-block:: bash
   :linenos:
   
   wsl --install
   wsl --version

MBROLA needs a few system dependencies. These allow to download the necessary code and compile MBROLA from source. We are also installing Python for using pymbrola later. Open the terminal and run the following lines (if using WSL enter the terminal by running wsl on your command prompt):

.. code-block:: bash
  :linenos:

  apt-get update
  apt-get install build-essential curl git gcc python3

Next, install **pymbrola** as you normally would:

.. code-block:: bash
  :linenos:

  python3 -m pip install mbrola
    
You are now set up! Now open a Python session and installing MBROLA and any desired voices:

.. code-block:: python
  :linenos:

  from pymbrola import install, mbrola

  install.install_mbrola()
  install.install_voice(["it4", "fr4"])

  mbrola.MBROLA("kaffE").to_sound("kaffE.wav", voice="it4")
    

