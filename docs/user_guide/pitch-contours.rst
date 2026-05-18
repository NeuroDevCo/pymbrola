==================
Pitch Contours
==================

Overview
=========

**pymbrola** supports piecewise linear pitch specification, allowing fine control over pitch dynamics.

Constant Pitch
===============

Specify pitch as an integer for constant pitch across all phonemes:

.. code-block:: python

   phon = list("kasa")
   pitch = 200

Result:

.. code-block:: python

   # [[(0, 200)], [(0, 200)], [(0, 200)], [(0, 200)]]

Pitch per Phoneme
===================

Specify pitch as a list, with one value per phoneme:

.. code-block:: python

   phon = list("kasa")
   pitch = [200, 50, 50, 100]

Result:

.. code-block:: python

   # [[(0, 200)], [(0, 50)], [(0, 50)], [(0, 100)]]

Complex Pitch Contours
=======================

Use lists of tuples for piecewise linear pitch changes within a phoneme:

.. code-block:: python

   phon = list("kasa")
   pitch = [[], [(25, 50), (50, 100), (75, 150), (90, 200)], [], 100]

Each tuple contains:

- **First value:** Time as a percentage of the phoneme duration (0-100)
- **Second value:** Pitch value in Hz

Result:

.. code-block:: python

   # [[], [(25, 50), (50, 100), (75, 150), (90, 200)], [], [(0, 100)]]

Using Empty Lists
===================

Empty lists in the pitch specification result in constant pitch sections:

.. code-block:: python

   phon = list("kasa")
   pitch = [[], 50, [], 100]

Result:

.. code-block:: python

   # [[], [(0, 50)], [], [(0, 100)]]