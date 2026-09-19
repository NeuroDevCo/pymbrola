============
About MBROLA
============

.. admonition:: About the name MBROLA
    :class: sidebar note

    MBROLA stands for the name of such algorithm, Multi-Band Resynthesis OverLap Add.

MBROLA [#c1]_ is a **speech synthesis software** developed in the 90s by Thierry Dutoit and Vinvent Pagel. Vaguely, it consists in a database of naturally **pre-recorded diphones** (combinations of two phones, like /ke/ or /li/), which are put together according to form the desired string of sounds that the user inputs. The result is an intelligible, yet somewhat robotic-like speech stored in a WAV file. The actual machinery behind MBROLA is much more complex than this, and the particular mechanisms that merge pre-recorded diphones is, to date, an important breakthrough in linguistics and speech synthesis research.

More recent speech synthesisers have been released since MBROLA, most of which produce a much more natural-sounding output. These models work very differently compared to MBROLA: they are being trained on massive amounts of text and speech data, and become very good at finding out how particular combinations of characters are supposed to sound like when read aloud. This is very convenient when one simply wants some text to be “read” aloud by the machine.

MBROLA works in a very different way. First, MBROLA takes phonetic symbols as input. It then looks up which diphones are available in the database of a particular language, and then puts them together to produce a sound using the aforementioned MBROLA algorithm. This is one of the best features of MBROLA: it provides **fine-grained control over the phonology of the output**. The user can also specify the duration of each phone, and modulate the pitch contour in an almost arbitrary way. Most importantly, the input consists in **phonetic symbols**, which provides much more control over the phonological features of the segments present in the output. For these reasons, many psycholinguistics researchers have relied on MBROLA to synthesise their auditory speech stimuli for experiments when fine control is required. For instance, this is the input that MBROLA takes to generate the word “caffè” (/kafˈfɛ/) in Italian::

    ; caffè
    ; first number after the phonetic symbol indicates the duration of the segment
    ; the rest of the numbers indicate F0 contour.
    _ 10
    k 100 200 200
    a 100 200 100 100 200
    f 100 200 200
    f 100 200 200
    E1 100 200 200
    _ 10

**MBROLA is not currently being mantained**, and their main website is down. Plus, there aren’t many up-to-date resources out there explaining how to use MBROLA. Getting MBROLA to run in your computer can be a bit daunting, so after having gone through it. Invite you to visit the *Installation* section to more details.

.. rubric:: Footnotes

.. [#c1] Dutoit, T., Pagel, V., Pierret, N., Bataille, F., & Van der Vrecken, O. (1996, October). The MBROLA project: Towards a set of high quality speech synthesizers free of use for non commercial purposes. In Proceeding of Fourth International Conference on Spoken Language Processing. ICSLP'96 (Vol. 3, pp. 1393-1396). IEEE. `https://doi.org/10.1109/ICSLP.1996.607874 <https://doi.org/10.1109/ICSLP.1996.607874>`_
