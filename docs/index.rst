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

| A Python front-end for the `MBROLA <https://github.com/numediart/MBROLA>`__ speech synthesizer. **pymbrola** enables programmatic creation of MBROLA-compatible phoneme files and automated audio synthesis with Python. It provides a simple interface to the MBROLA speech synthesizer, supporting customizable phonemes, durations, and pitch contours.


.. toctree::
   :hidden:

   Installation <installation>
   Quick start <quick_start>
   About MBROLA <mbrola>
   API Reference <api/index>
   Contributing <contributing>
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


References
----------

Dutoit, T., Pagel, V., Pierret, N., Bataille, F., & Van der Vrecken, O. (1996, October).
The MBROLA project: Towards a set of high quality speech synthesizers free of use for non commercial purposes.
In Proceeding of Fourth International Conference on Spoken Language Processing. ICSLP'96 (Vol. 3, pp. 1393-1396). IEEE.
`https://doi.org/10.1109/ICSLP.1996.607874 <https://doi.org/10.1109/ICSLP.1996.607874>`_

License
-------

`pymbrola` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

Supported by
------------

Funded by the European Union. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or the European Research Council Executive Agency (ERCEA). Neither the European Union nor the granting authority can be held responsible for them. This work is supported by the ERC StG 101115991 (GALA) awarded to Chiara Santolin

.. image:: _static/img/EN_FundedbytheEU_RGB_POS.png
    :alt: erc
    :width: 400
    :target: https://erc.europa.eu/homepage
