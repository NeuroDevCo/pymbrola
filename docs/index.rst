===========
pymbrola
===========

A Python front-end for the `MBROLA <https://github.com/numediart/MBROLA>`_ speech synthesizer.

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

Overview
=========

**pymbrola** enables programmatic creation of MBROLA-compatible phoneme files and automated audio synthesis with Python. It provides a simple interface to the MBROLA speech synthesizer, supporting customizable phonemes, durations, and pitch contours.

Key Features
============

- **Front-end to MBROLA:** Easily create ``.pho`` files and synthesize audio with Python
- **Input validation:** Prevents invalid file and phoneme sequence errors
- **Customizable:** Easily set phonemes, durations, pitch contours, and leading/trailing silences
- **Cross-platform (Linux/WSL):** Automatically detects and adapts to Linux or Windows Subsystem for Linux environments

Requirements
=============

- Python 3.10+
- `MBROLA binary <https://github.com/numediart/MBROLA>`_ installed and available in your system path.
- MBROLA voices (e.g., ``it4``) installed at ``/usr/share/mbrola/<voice>/<voice>``

Installation
=============

.. code-block:: bash

   pip install mbrola

Quick Start
============

.. code-block:: python

   import mbrola

   # Create an MBROLA object
   caffe = mbrola.MBROLA(
       word="caffè",
       phon=["k", "a", "f", "f", "E1"],
       durations=100,
       pitch=[100, [200, 50, 200], 100, 100, 200]
   )

   # Synthesize and save audio
   caffe.make_sound("caffe.wav", voice="it4")

References
===========

Dutoit, T., Pagel, V., Pierret, N., Bataille, F., & Van der Vrecken, O. (1996, October).
The MBROLA project: Towards a set of high quality speech synthesizers free of use for non commercial purposes.
In Proceeding of Fourth International Conference on Spoken Language Processing. ICSLP'96 (Vol. 3, pp. 1393-1396). IEEE.
`https://doi.org/10.1109/ICSLP.1996.607874 <https://doi.org/10.1109/ICSLP.1996.607874>`_