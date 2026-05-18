==================
Troubleshooting
==================

Common Issues
==============

MBROLA not found
-----------------

**Error:** ``FileNotFoundError: MBROLA binary not found``

**Solution:** Ensure MBROLA is installed and available in your system PATH:

.. code-block:: bash

   which mbrola

If not installed, follow the :doc:`installation` guide.

Voices not found
-----------------

**Error:** ``FileNotFoundError: Voice file not found``

**Solution:** Ensure MBROLA voices are installed at ``/usr/share/mbrola/<voice>/<voice>``:

.. code-block:: bash

   ls /usr/share/mbrola/

Platform not supported
-----------------------

**Error:** ``OSError: Platform not supported. pymbrola requires Linux or WSL.``

**Solution:** pymbrola currently requires Linux or Windows Subsystem for Linux (WSL). Use Docker if on Windows:

.. code-block:: bash

   docker run -it gongcastro/pymbrola:latest

Invalid phoneme sequence
-------------------------

**Error:** ``ValueError: Invalid phoneme sequence``

**Solution:** Verify that your phoneme list is valid for the selected MBROLA voice. Check the voice documentation for available phonemes.

Getting Help
=============

If you encounter issues not listed here:

1. Check the `GitHub Issues <https://github.com/NeuroDevCo/pymbrola/issues>`_
2. `Create a new issue <https://github.com/NeuroDevCo/pymbrola/issues/new>`_ with:
   - The error message
   - Your pymbrola version
   - Your Python version
   - Your OS and how you installed MBROLA