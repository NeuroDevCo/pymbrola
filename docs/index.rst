========
pymbrola
========

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Contents

   Installation <installation>
   Usage <usage>
   About MBROLA <mbrola>
   API Reference <api/index>
   License <license>

.. |gh-actions| image:: https://img.shields.io/github/actions/workflow/status/NeuroDevCo/pymbrola/testing.yml
   :alt: GitHub Actions Workflow Status
   :class: display

.. |pypi-version| image:: https://img.shields.io/pypi/v/mbrola.svg
   :alt: PyPI - Version
   :target: https://pypi.org/project/mbrola

.. |pypi-pyversions| image:: https://img.shields.io/pypi/pyversions/mbrola.svg
   :alt: PyPI - Python Version
   :target: https://pypi.org/project/mbrola

.. |license| image:: https://img.shields.io/github/license/NeuroDevCo/pymbrola
   :alt: GitHub License

.. |codecov| image:: https://img.shields.io/codecov/c/github/NeuroDevCo/pymbrola
   :alt: Codecov

|gh-actions| |pypi-version| |pypi-pyversions| |license| |codecov|

| A **Python** front-end for the `MBROLA <https://github.com/numediart/MBROLA>`__ speech synthesizer. **pymbrola** enables programmatic creation of MBROLA-compatible **.pho files** and automated **audio synthesis** with Python, supporting customizable phonemes, durations, and pitch contours.

.. code-block:: python
  :linenos:

   from pymbrola import mbrola

   # Create an MBROLA object
   word = mbrola.MBROLA(
       phon=["h", "e", "l", "@U"],
       durations=[75, 100, 100, 200],
       pitch=[50, 150, 175, 200]
   )

   # Export to PHO file
   word.export_pho("hello.pho")

   # Synthesize and save audio in WAV file
   word.to_sound("hello.wav", voice="en1")

.. audio:: _static/sounds/hello.wav

Supported by
------------

Funded by the European Union. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or the European Research Council Executive Agency (ERCEA). Neither the European Union nor the granting authority can be held responsible for them. This work is supported by the ERC StG 101115991 (GALA) awarded to Chiara Santolin

.. image:: _static/img/EN_FundedbytheEU_RGB_POS.png
    :alt: erc
    :width: 400
    :target: https://erc.europa.eu/homepage
