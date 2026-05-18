===========
Usage
===========

Basic Usage
============

Creating a simple synthesis:

.. code-block:: python

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
====================

Phonemes are specified as a list of strings:

.. code-block:: python

   import mbrola

   caffe = mbrola.MBROLA(
       word="caffè",
       phon=["k", "a", "f", "f", "E1"],
       durations=[100, 120, 100, 110, 150],
       pitch=100
   )

Specifying Durations
======================

Durations can be specified as:

- **Single integer:** Applied to all phonemes
- **List of integers:** One duration per phoneme

.. code-block:: python

   # All phonemes have 100ms duration
   durations = 100

   # Each phoneme has its own duration
   durations = [100, 120, 100, 110, 150]

Viewing Results
================

Display the phoneme sequence:

.. code-block:: python

   print(word)

This will output a structured representation of the phonemes, durations, and pitch values.