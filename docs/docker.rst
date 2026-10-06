=====================
Docker image and WSL
=====================

Because compiling MBROLA in a Windows machine is somewhat complicated, **pymbrola** only supports Linux-based operative systems. If you are a Windows user there are two ways in which you could use **pymbrola**: Docker and Windows Subsystem for Linux (WSL). Both have their own advantages and disadvantages. My recommendation is to use Docker.

Docker
======

Install `Docker Desktop <https://docs.docker.com/desktop/setup/install/windows-install/>`__ in you machine, then run the following command in your terminal making sure Docker engine is running (having Docker open usually does this): 

.. code-block:: bash
  :linenos:

    docker run -it --user "$(id -u):$(id -g)" -v "~/.mbrola/output:/pymbrola/output" gongcastro/pymbrola:latest

This command will download the **gongcastro/pymbrola** Docker image from `DockerHub <https://hub.docker.com/repository/docker/gongcastro/pymbrola>`__ if necessary, then run it in a container. The result will be a Python session open in the terminal, in which you will be able to import the `mbrola` module. You may want to first run `mbrola.install_mbrola()` and `mbola_install_voice("it4")` first (replace `"it4"` with whichever voice or voices you are planning to use. Importantly, a volume is attached, so that any files inside the container under the folder `./output` will be persistently saved in the host machine wherever the command `~/.mbrola/out` takes you in your computer. This is where you will find your synthesised files after closing your Docker container.

Windows Subsystem for Linux (WSL)
=================================

If you want to use `Windows Subsystem for Linux (WSL) <https://learn.microsoft.com/en-us/windows/wsl/about>`__ to run **pymbrola**, make sure first that your WSL installation is up and working. MBROLA needs a few system dependencies. These allow to download the necessary code and compile MBROLA from source. We are also installing Python for using pymbrola later. Open the terminal and run the following lines (if using WSL enter the terminal by running wsl on your command prompt).

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

  import mbrola

  mbrola.install_mbrola()
  mbrola.install_voice(["it4", "fr4"])

  mbrola.MBROLA("kaffE").make_sound("kaffE.wav")
    

