---
title: 'pymbrola: A Python front-end for the MBROLA speech synthesizer'
tags:
  - Python
  - MBROLA
  - speech synthesis
  - speech
  - TTS
authors:
  - name: Gonzalo García-Castro
    orcid: 0000-0002-8553-4209
    equal-contrib: true
    affiliation: 1
  - name: Chiara Santolin
    orcid: 0000-0002-8361-5574
    affiliation: 1
affiliations:
 - name: Institut de Recerca Sant Joan de Déu (IRSJD)
   index: 1

date: 2 October 2026
bibliography: paper.bib
---

# Summary

MBROLA [@dutoit1996mbrola] is an open source software project aimed at supporting multi-language Text-To-Speech (TTS) synthesis. It is based on the Multi-Band Resynthesis OverLap Add (MBROLA) algorithm, which concatenates naturally pre-recorded diphones (i.e., combinations of two speech sounds, like /ke/ or /li/), this minimizes concatenation mismatches between audios and leads to higher-quality speech synthesis than most TTS software available at the time [@dutoit1993mbr]. Since its first release, MBROLA has served as one of the most relied upon backends for TTS, and its diphone database has been extended to at least 75 languages and dialects (refered to as *voices* by MBROLA) (<https://github.com/numediart/MBROLA-voices>).

More recent open source speech synthesisers have been released since MBROLA, most of which produce a much more natural-sounding output (e.g., VoiceStudio, GPT-SoVITS, GLM-TTS, Kokoro-82M). Those models are trained on massive amounts of text and speech data, learning how particular combinations of characters are supposed to sound like when read aloud in a particular language. This is very convenient when one simply wants some text to be "read" aloud by the machine. MBROLA works very differently. First, MBROLA takes phonetic symbols as input. It then looks up which diphones are available in the database of a particular language, and puts them together to produce a sound using the aforementioned MBROLA algorithm. The fact that MBROLA needs an extra layer of specification to act like an end-to-end TTS software represents a limitation compared to more recent sotfware, in which text and sounds are mapped directly. While some pieces of software have been developed to fill this gap (for instance eSpeakNG provides a text to phoneme translation step that later feeds to MBROLA to produce sound), it is precisely the direct phonological specification of the input that has made MBROLA of high interest for experimental psycholinguistic research.

Desiging an experimental study in psycholinguistics often involves presenting participants with auditory stimuili, some of which belong to a category or another. Different categories of auditory stimuli differ in a single linguistic feature of interest. During the presentation of different types of stimuli participants are asked to perform a task (e.g., responding if two stimuli are the sae or different) or some kind of neurophysiological response is registered (e.g., EEG, fMRI, fNIRS). In both cases, the registered responses or physiological signal informs researchers about participants' ability to distinguish or identify each type of stimuli, based on their differing linguistic feature. Researchers therefore require fine control over the linguistic features present in the auditory stimuli. To this end, MBROLA's phonological specification of the input provides an interface which can be used to 1) select the specific phonemes being presented, and 2) manipulate their duration and 3) modulate the pitch contour of the resulting materials at will. This is an advantage, compared to more rencently available TTS, which rarely allow phoneme-level manipulations of duration or quality, duration, or pitch.

# State of the field

MBROLA provides a terminal-based interface to users. The sequence of phonemes to synthesise, their duration, and their pitch contour is specified by the user in a PHO file, like this:

```
; PHO file kaffE.pho
_ 1
k 100 (0, 200)
a 100 (0, 200)
f 100 (0, 200)
f 100 (0, 200)
E 100 (0, 200)
_ 1
```

The first line starts with ";", which marks the start of a comment line. The second and last lines pad a one-millisecond silence at the start and the end of the synthesis. Every line in between specifies the phoneme to be played (e.g., `k`, which must be part of the phoneme reportoure of the language being used), its duration in milliseconds (e.g., `100 ms`), and the pitch to apply at a given millisecond inside the phoneme in Hertz (e.g., `(0, 200)`, which specifies a 200 Hz pitch at phoneme onset, which will remain constaint until phoneme offset). MBROLA can then be pointed to this file, and together with some extra parameters---mainly the voice to use (e.g., `it4`) and the path to the output file (e.g., `kaffE.wav`)---a sound will be saved as a file.

```bash
mbrola it4/it4 kaffE.pho kaffE.wav
```

While this interface is relatively intuitive to generate files on a one-to-one basis, users may sometimes need to synthesise a large number of files, each specified in a different PHO file. In these cases, the user may want to first write the corresponding PHO files, the call the `mbrola` iteratively in their terminal (e.g., Bash, PowerShell). Implementing such a solution requires some familiarity with these programming languages. Most linguistics and psycholinguistics researchers, however, use Python and R, which currently lack a direct interface to MBROLA.

We present `pymbrola` a Python interface to MBROLA, which provides a series of wrapper functions that allows 1) generating PHO files from the Python console specifying phonemes, duration and pitch with fine level of detail, and 2) call MBROLA to generate the sound file. It also provides helper functions to installing MBROLA and downloading MBROLA voices from the <https://github.com/numediart/MBROLA> and <https://github.com/numediart/MBROLA-voices> repositories. 

# Software design

**pymbrola** can be installed from the [PyPi](https://pypi.org/project/mbrola/) repository using [pip](https://pypi.org/project/mbrola/). Alternatively it can be installed using [uv](https://docs.astral.sh/uv/getting-started/installation/):

```sh
pip install pymbrola # pip installation
uv add pymbrola      # uv installation
```

MBROLA is currently available only on Linux-based systems like Ubuntu, or on Windows via the [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install). Native Windows and macOS are not yet compatible with the **pymbrola** package. Windows users may use the available [Docker image](https://hub.docker.com/repository/docker/gongcastro/mbrola/general) based on Ubuntu 22.04 with a ready-to-go installation of MBROLA, for convenience. Once Docker is installed in a local machine, the image can be pulled and started as a container using Docker Desktop or from the terminal:

```bash
docker run -it gongcastro/pymbrola
```

In either case, Python>=3.12 is required. **pymbrola** also requires a functinal MBROLA installation. This can be done from the Python console once **pymbrola** has been installed:

```python
from pymbrola import install

install.install_mbrola()
```

By default, MBROLA will be downladed and compiled in a newly created folder in the home folder `~/.mbrola`. Finally, the desired MBROLA voices can also be downloaded from the Python console:

```python
from pymbrola import install

install.install_voice("it4")  # install it4 voice
install.install_voice(["it4", "fr4"])  # install several voices
install.install_voice()  # install all voices (~534M)
```

The workhorse behind **pymbrola** is the `MBROLA` class. An instance of this class is initialised with at least a list of phonemes in the `phon` argument. Phonemes are specified as a list of strings. Each phoneme in the specified list must be included in the repertoire of phonemes in the MBROLA voice being used. In the previous example, the phoneme `"E1"` works because it is part of the `en1` voice (see here <https://github.com/numediart/MBROLA-voices/blob/master/data/en1/README.txt>). Using a phoneme that does not exist in the selected voice will result in an error. Which phonemes are available for each language can be consulted in the `README.txt` located in the voice's folder.

```python
from pymbrola import mbrola

# Create an MBROLA object
caffe = MBROLA(phon=["k", "a", "f", "f", "E1"])
```
Durations are specified in milliseconds, and can be provided as a single integer or as a list of integers. If a single integer, the specified duration is applied to all phonemes. Duration defaults to 100 ms for each phoneme. If a list of phonemes, each element in the list is sequentially matched with each phoneme (the list of durations must have same length as the list of phonemes).


```python
# All phonemes have 100 ms duration
caffe = mbrola.MBROLA(phon=phons, durations=100)


# Each phoneme has its own duration
durations = [100, 120, 100, 110, 150]
caffe = mbrola.MBROLA(phon=phons, durations=durations)
```

Pitch can be specified in several way. If pitch is specified as an **integer**, pitch is assumed constant across phonemes:

```python
caffe = mbrola.MBROLA(phon=phons, pitch=200)
```

If pitch is specified as a **list of integers**, with one value per provided phoneme, following MBROLA the resulting pitch contour will be remain constant at each value for the time spanned by its corresponding phoneme.

```python
pitch = [200, 50, 50, 75, 100]
caffe = mbrola.MBROLA(phon=phons, pitch=pitch)
```

If any elements in the list of pitch values is `None` or an empty list `[]`, that value is converted to the default pitch value (200 Hz), and treated as if such valuee had been provided as an integer instead.

```python
pitch = [300, [], 100, 50, []]
caffe = mbrola.MBROLA(phon=phons, pitch=pitch)
```

**pymbrola** supports the **piecewise linear description of pitch** from MBROLA. If pitch is specified as a **list** of tuples, each element will also be mapped to each phoneme. Non-empty lists in the pitch specification must consist of lists of tuples. Each tuple contains two values. The first value is the time (as a percentage of the duration of the phoneme) at which the pitch should be modified inside the phoneme (as a float or integer), and the second value is the pitch that should be set at that time (as an integer).

For instance, in the following example pitch is specified so that:

1) First phoneme (`k`): Pitch remains constant at 300 Hz.
2) Second phoneme (`a`): Pitch starts at 200 Hz, then changes to 50 Hz at 25 ms after phoneme onset, then changes to 100 Hz after 50 ms, then changes to 90 Hz after 90 ms.
3) Rest of the phonemes (`f`, `f`, `E1`): Pitch changes to 300 Hz after 50 ms.

```python
pitch = [300, [(25, 50), (50, 100), (75, 150), (90, 200)], 100, 100]
caffe = mbrola.MBROLA(phon=phons, pitch=pitch)
```

Under the hood, **pymbrola** transforms the provided inputs into a string formatted as a .pho file. These files contain the instructions that MBROLA needs to synthesise the sound. You can check what the .pho file of a `MBROLA` instance looks like using the `pho` attribute, or exporting it as a .pho file to your file system using the `export_pho` method:

```python
caffe = mbrola.MBROLA(phon=phons)

print(caffe.pho)
# ['; k a f f E1',
#'_ 1',
#'k 100 (0, 300)',
#'a 100 ',
#'f 100 (0, 100)',
#'f 100 (0, 50)',
#'E1 100 ',
#'_ 1']

caffe.export_pho("caffe.pho")
```

Finally, the audio can be synthesised and written in disk in WAV format by using the `to_sound` method:

```python
caffe.to_sound("caffe.wav", voice="it4")
```

# Research impact statement

# Citations

# Figures

# AI usage disclosure

No generative AI tools were used in the development of this software, the writing of this manuscript, or the preparation of supporting materials.

# Acknowledgements

# References