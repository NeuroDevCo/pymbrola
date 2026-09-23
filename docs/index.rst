========
pymbrola
========

.. image:: https://img.shields.io/github/actions/workflow/status/NeuroDevCo/pymbrola/testing.yml
   :alt: GitHub Actions Workflow Status

.. image:: https://img.shields.io/pypi/v/mbrola.svg
   :alt: PyPI - Version
   :target: https://pypi.org/project/mbrola

.. image:: https://img.shields.io/pypi/pyversions/mbrola.svg
   :alt: PyPI - Python Version
   :target: https://pypi.org/project/mbrola

.. image:: https://img.shields.io/github/license/NeuroDevCo/pymbrola
   :alt: GitHub License

.. image:: https://img.shields.io/codecov/c/github/NeuroDevCo/pymbrola
   :alt: Codecov

| A **Python** front-end for the `MBROLA <https://github.com/numediart/MBROLA>`__ speech synthesizer. **pymbrola** enables programmatic creation of MBROLA-compatible **.pho files** and automated **audio synthesis** with Python, supporting customizable phonemes, durations, and pitch contours.

.. code-block:: ipython
  :linenos:

   import mbrola

   # Create an MBROLA object
   word = mbrola.MBROLA(
       phon=["h", "e", "l", "@U"],
       durations=[75, 100, 100, 200],
       pitch=[50, 150, 175, 200]
   )

   # Export to PHO file
   word.export_pho("hello.pho")

   # Synthesize and save audio in WAV file
   word.make_sound("hello.wav", voice="en1")

.. audio:: _static/sounds/hello.wav

.. toctree::
   :hidden:

   Installation <installation>
   Usage <usage>
   About MBROLA <mbrola>
   API Reference <api/index>
   License <license>

Docker image
------------
For convenience, a `Docker image <https://hub.docker.com/repository/docker/gongcastro/pymbrola/general>`__ is available at Dockerhub:


.. code-block:: bash

   docker run -it gongcastro/pymbrola:latest


Troubleshooting
---------------
- Ensure MBROLA and the required voices are installed and available at `/usr/share/mbrola/<voice>/<voice>`.
- If you encounter an error about platform support, make sure you are running on Linux or WSL.
- Write an `issue <https://github.com/NeuroDevCo/pymbrola/issues>`__, I'll look into it ASAP.


Supported by
------------

Funded by the European Union. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or the European Research Council Executive Agency (ERCEA). Neither the European Union nor the granting authority can be held responsible for them. This work is supported by the ERC StG 101115991 (GALA) awarded to Chiara Santolin

.. image:: _static/img/EN_FundedbytheEU_RGB_POS.png
    :alt: erc
    :width: 400
    :target: https://erc.europa.eu/homepage
