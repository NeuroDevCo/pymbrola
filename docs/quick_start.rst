===========
Quick start
===========

This is a quick walkthrough to get you up and running with **pymbrola**, you may find [this blog post](https://gongcastro.github.io/blog/pymbrola-using/pymbrola-using.html) I made useful.

Creating a simple synthesis:

.. code-block:: python
  :linenos:

   import mbrola

   # Create an MBROLA object
   word = mbrola.MBROLA(
       word="hello",
       phon=["h", "e", "l", "o"],
       durations=100,
       pitch=100
   )

   # Export to PHO file
   word.export_pho("hello.pho")

   # Synthesize and save audio
   word.make_sound("hello.wav", voice="en1")

Specifying Phonemes
===================

Phonemes are specified as a list of strings:

.. code-block:: python
  :linenos:

   import mbrola

   caffe = mbrola.MBROLA(
       word="caffè",
       phon=["k", "a", "f", "f", "E1"],
       durations=[100, 120, 100, 110, 150],
       pitch=100
   )

Specifying Durations
====================

Durations can be specified as:

- **Single integer:** Applied to all phonemes
- **List of integers:** One duration per phoneme

.. code-block:: python
  :linenos:
   # All phonemes have 100ms duration
   durations = 100

   # Each phoneme has its own duration
   durations = [100, 120, 100, 110, 150]

Viewing Results
===============

Display the phoneme sequence:

.. code-block:: python
  :linenos:
   print(word)

This will output a structured representation of the phonemes, durations, and pitch values.

Pitch Contours
==============

**pymbrola** supports piecewise linear pitch specification, allowing fine control over pitch dynamics.

Constant Pitch
--------------

If pitch is specified as an **integer**, pitch is assumed constant across phonemes:

.. code-block:: python
  :linenos:
   phon = list("kasa")
   pitch = 200
   validate_pitch(200, phon)

Result:

.. code-block:: python

   # [[(0, 200)], [(0, 200)], [(0, 200)], [(0, 200)]]

Pitch per Phoneme
-----------------

Specify pitch as a list, with one value per phoneme:

.. code-block:: python
  :linenos:
   phon = list("kasa")
   pitch = [200, 50, 50, 100]

Result:

.. code-block:: python

   # [[(0, 200)], [(0, 50)], [(0, 50)], [(0, 100)]]

Complex Pitch Contours
----------------------

If pitch is specified as a **list**, each element in mapped to each phoneme. Integers in the list are treated as before (constant pitch for the whole phoneme):

.. code-block:: python
  :linenos:
   phon = list("kasa")
   pitch = [[], [(25, 50), (50, 100), (75, 150), (90, 200)], [], 100]

Each tuple contains:

- **First value:** Time as a percentage of the phoneme duration (0-100)
- **Second value:** Pitch value in Hz

Result:

.. code-block:: python

   # [[], [(25, 50), (50, 100), (75, 150), (90, 200)], [], [(0, 100)]]

Using Empty Lists
-----------------

Empty lists inside the main list are treated as constant pitch sections:

.. code-block:: python
  :linenos:
   phon = list("kasa")
   pitch = [[], 50, [], 100]

Result:

.. code-block:: python

   # [[], [(0, 50)], [], [(0, 100)]]

Non-empty lists must consist in lists of tuples. Each tuple contains two values. The first value is the time (as a percentage of the duration of the phoneme) at which the pitch should be modified inside the phoneme (as a float or integer), and the second value is the pitch that should be set at that time (as an integer):

.. code-block:: python
  :linenos:
   phon = list("kasa")
   pitch = [[], [(25, 50), (50, 100), (75, 150), (90, 200)], [], 100]
   validate_pitch(pitch, phon)

Result:

.. code-block:: python

   # [[], [(25, 50), (50, 100), (75, 150), (90, 200)], [], [(0, 100)]]
