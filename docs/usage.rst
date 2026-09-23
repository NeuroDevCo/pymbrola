=====
Usage
=====

This is a quick walkthrough to get you up and running with **pymbrola**. Here is a simple synthesis:

.. code-block:: python
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

Specifying Phonemes
===================

Phonemes are specified as a list of strings. Each phoneme in the specified list must be included in the repertoire of phonemes in the MBROLA voice being used. In the previous example, the phoneme `"E1"` works because it is part of the `en1` voice (see here https://github.com/numediart/MBROLA-voices/blob/master/data/en1/README.txt). Using a phoneme that does not exist in the selected voice will result in an error. You can consult which phonemes are available for each language in the `README.txt` located in the voice's folder.


.. code-block:: python
  :linenos:

   import mbrola

   phons = ["k", "a", "f", "f", "E1"]

   caffe = mbrola.MBROLA(
       phon=phons,
       durations=[100, 120, 100, 110, 150],
       pitch=100
   )

   print(caffe.phon)
   # ["k", "a", "f", "f", "E1"]

Specifying Durations
====================

Durations are provided as milliseconds, and can be specified as a single integer or as a list of integers. If a single integer, the specified duration is applied to all phonemes.

.. code-block:: python
  :linenos:

   # All phonemes have 100 ms duration
   caffe = mbrola.MBROLA(phon=phons, durations=100)

   print(caffe.durations)

If a list of phonemes, each element in the list is sequentially matched with each phoneme (the list of durations must have same length as the list of phonemes).

.. code-block:: python
  :linenos:

   durations = [100, 120, 100, 110, 150]

   # Each phoneme has its own duration
   caffe = mbrola.MBROLA(phon=phons, durations=durations)

   print(caffe.durations)

Pitch Contours
==============

Pitch can be specified in several way. If pitch is specified as an **integer**, pitch is assumed constant across phonemes:

.. code-block:: python
  :linenos:

   caffe = mbrola.MBROLA(phon=phons, pitch=200)

   print(phon.pitch)
   # [[(0, 200)], [(0, 200)], [(0, 200)], [(0, 200)]]

If pitch is specified as a **list of integers**, with one value per provided phoneme, following MBROLA the resulting pitch contour will be remain constant at each value for the time spanned by its corresponding phoneme.

.. code-block:: python
  :linenos:

   pitch = [200, 50, 50, 75, 100]

   caffe = mbrola.MBROLA(phon=phons, pitch=pitch)

   print(caffe.pitch)
   # [[(0, 200)], [(0, 50)], [(0, 50)], [(0, 75)], [(0, 100)]]


If any elements in the list of pitch values is `None` or an empty list `[]`, that value is converted to the default pitch value (200 Hz), and treated as if such valuee had been provided as an integer instead.

.. code-block:: python
  :linenos:

   pitch = [300, [], 100, 50, []]

   caffe = mbrola.MBROLA(phon=phons, pitch=pitch)

   print(caffe.pitch)
   # [[], [(25, 50), (50, 100), (75, 150), (90, 200)], [], [(0, 100)]]

**pymbrola** supports the **piecewise linear description of pitch** from MBROLA. If pitch is specified as a **list** of tuples, each element will also be mapped to each phoneme. Non-empty lists in the pitch specification must consist of lists of tuples. Each tuple contains two values. The first value is the time (as a percentage of the duration of the phoneme) at which the pitch should be modified inside the phoneme (as a float or integer), and the second value is the pitch that should be set at that time (as an integer).

For instance, in the following example pitch is specified so that:

1) First phoneme (`k`): Pitch remains constant at 300 Hz.
2) Second phoneme (`a`): Pitch starts at 200 Hz, then changes to 50 Hz at 25 ms after phoneme onset, then changes to 100 Hz after 50 ms, then changes to 90 Hz after 90 ms.
3) Rest of the phonemes (`f`, `f`, `E1`): Pitch changes to 300 Hz after 50 ms.

.. code-block:: python
  :linenos:

   pitch = [300, [(25, 50), (50, 100), (75, 150), (90, 200)], 100, 100]

   caffe = mbrola.MBROLA(phon=phons, pitch=pitch)

   print(caffe.pitch)
   # [[], [(25, 50), (50, 100), (75, 150), (90, 200)], [], [(0, 100)]]

Generating a .pho file
----------------------

Under the hood, **pymbrola** transforms the provided inputs into a string formatted as a .pho file. These files contain the instructions that MBROLA needs to synthesise the sound. You can check what the .pho file of a `MBROLA` instance looks like using the `pho` attribute, or exporting it as a .pho file to your file system using the `export_pho` method:

.. code-block:: python
  :linenos:

   caffe = mbrola.MBROLA(phon=phons)

   print(caffe.pho)
   #['; k a f f E1',
   #'_ 1',
   #'k 100 (0, 300)',
   #'a 100 ',
   #'f 100 (0, 100)',
   #'f 100 (0, 50)',
   #'E1 100 ',
   #'_ 1']

   caffe.export_pho("caffe.pho")

Synthesising the sound
----------------------

Finally, you can create the audio file in WAV format by using the `make_sound` method:

.. code-block:: python
  :linenos:

   caffe = mbrola.MBROLA(phon=phons)

   caffe.make_sound("caffe.wav")

Which results in this audio:

.. audio:: _static/sounds/caffe.wav
