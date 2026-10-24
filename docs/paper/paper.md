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

This paper introduces Pymbrola, a Python interface to the MBROLA speech synthesiser. Pymbrola provides a series of functions and wrappers to 1) install MBROLA in Linux-based systems (or Windows Subsystem for Linux, WSL), 2) download MBROLA voices, 3) create PHO files with fine details about the phonological specifications of the synthesised speech, and 4) generate WAV files with the resulting synthetisation.

# Statement of need

MBROLA [@dutoit1996mbrola] is an open source software project aimed at supporting multi-language Text-To-Speech (TTS) synthesis. It is based on the Multi-Band Resynthesis OverLap Add (MBROLA) algorithm, which concatenates pre-recorded diphones (i.e., combinations of two speech sounds, like /ke/ or /li/). This concatenation algorithm minimizes mismatches between audios and leads to higher-quality speech synthesis than most TTS software available at the time [@dutoit1993mbr]. Since its first release, MBROLA has served as one of the most relied upon backends for TTS, and its diphone database has been extended to at least 75 languages and dialects (referred to as *voices* by MBROLA) [@tits2019mbrola].

MBROLA provides a user interface to specify the phonological features present in the synthesized speech sample with fine detail. The user can choose which specific phonemes will be uttered from a list of available phonemes in the database of a given language (e.g., `e` for /e/ or `E1` for /ɛ/), instead of relying in grapheme-to-phoneme conversion rules that characterize classical end-to-end TTS. Phoneme-level durations be specified, and pitch can also be modulated across the time course of the speech sample. Such a direct manipulation of phonological features has made MBROLA of high interest for speech science, particularly for experimental work in language processing research. One notable use of MBROLA in language research is the generation of auditory stimuli that participants of experiments are presented with: by manipulating phoneme quality, duration, or pitch contour, research are able to generate and test predictions about cognitive and neural underpinnings of speech processing [e.g., @ferry2016edge; @assaneo2019spontaneous; @onnis2008learn; @hochmann2011consonants; @marchetto2013words; @lopez2013word; @buiatti2009investigating; @peter2022language].

MBROLA provides a terminal-based interface to users. The sequence of phonemes to synthesize, their duration, and their pitch contour is specified by the user in a PHO file, like this:

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

The first line starts with ";", which marks the start of a comment line. The second and last lines pad a one-millisecond silence at the start and the end of the synthesis. Every line in between specifies the phoneme to be played (e.g., `k`, which must be part of the phoneme repertoire of the language being used), its duration in milliseconds (e.g., `100 ms`), and the pitch to apply at a given millisecond inside the phoneme in Hertz (e.g., `(0, 200)`, which specifies a 200 Hz pitch at phoneme onset, which will remain constant until phoneme offset). MBROLA can then be pointed to this file, and together with some extra parameters---mainly the voice to use (e.g., `it4`) and the path to the output file (e.g., `kaffE.wav`)---a sound will be saved as a file.

``` bash
mbrola it4/it4 kaffE.pho kaffE.wav
```

While this interface is relatively intuitive to generate files on a one-to-one basis, users may sometimes need to synthesize a large number of files, each specified in a different PHO file. In these cases, the user may want to first write the corresponding PHO files, then call the `mbrola` command iteratively in a shell language (e.g., Bash, PowerShell). While implementing this solution is possible, language researchers are rarely familiar with such programming languages, limiting the extent to which MBROLA can be used efficiently across many research contexts.

# State of the field

To our knowledge, no open source interfaces to MBROLA are publicly available in Python or R, two of the most popular programming languages in language research. To make programmatic access to MBROLA's capabilities more available to language researchers, we developed Pymbrola, a Python package that provides a series of wrapper functions that 1) allow generating PHO files from the Python console specifying phonemes, duration, and pitch with fine level of detail, and 2) call MBROLA to generate the sound file. It also provides helper functions to installing MBROLA and downloading MBROLA voices from the [numediart/MBROLA](https://github.com/numediart/MBROLA){.uri} and [numediart/MBROLA-voices](https://github.com/numediart/MBROLA-voices){.uri} GitHub repositories.

# Software design

## Installation and setup

Pymbrola can be installed from the [PyPi](https://pypi.org/project/mbrola/) repository using [pip](https://pypi.org/project/mbrola/). Alternatively it can be installed using [uv](https://docs.astral.sh/uv/getting-started/installation/):

``` sh
pip install pymbrola # pip installation
uv add pymbrola      # uv installation
```

MBROLA is currently available only on Linux-based systems like Ubuntu. For users of other operative systems like Windows or macOS, a [Docker image](https://hub.docker.com/repository/docker/gongcastro/mbrola/general) built on Ubuntu 22.04 is available with all system and Python requirements installed. Once Docker is installed in a local machine, the image can be pulled and started as a container using Docker Desktop or using the terminal:

``` bash
docker run -it gongcastro/pymbrola
```

Windows users may also use the [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install). In either case, Python\>=3.12 is required. Pymbrola also requires a compiled MBROLA installation. This can be done from the Python console once Pymbrola has been installed using the `install` module:

``` python
from pymbrola import install

install.install_mbrola()
```

By default, MBROLA will be downloaded and compiled in a newly created folder in the home folder `~/.mbrola`. Finally, the desired MBROLA voices can also be downloaded from the Python console:

``` python
from pymbrola import install

install.install_voice("it4")  # install it4 voice
install.install_voice(["it4", "fr4"])  # install several voices
install.install_voice()  # install all voices (~534M)
```

## The `MBROLA` class

The workhorse behind Pymbrola is the `MBROLA` class. An instance of this class is initialized with at least a list of phonemes in the `phon` argument. Phonemes are specified as a list of strings. Each phoneme in the specified list must be included in the repertoire of phonemes in the MBROLA voice being used. In the previous example, the phoneme `"E1"` works because it is part of the `it4` voice (see here <https://github.com/numediart/MBROLA-voices/blob/master/data/en1/README.txt>). Using a phoneme that does not exist in the selected voice will result in an error. Which phonemes are available for each language can be consulted in the `README.txt` located in the voice's folder.

``` python
from pymbrola import mbrola

# Create an MBROLA object
phons = ["k", "a", "f", "f", "E1"]
kaffE1 = MBROLA(phon=phons)
```

## Phoneme durations

Phoneme durations are specified in milliseconds (ms), and can be provided as a single integer or as a list of integers. If a single integer, the specified duration is applied to all phonemes. Duration defaults to 100 ms for each phoneme. If a list of phonemes, each element in the list is sequentially matched with each phoneme (the list of durations must have same length as the list of phonemes).

``` python
# All phonemes have 100 ms duration
kaffE1 = mbrola.MBROLA(phon=phons, durations=100)


# Each phoneme has its own duration
durations = [100, 120, 100, 110, 150]
kaffE1 = mbrola.MBROLA(phon=phons, durations=durations)
```

## Pitch contours

Pitch is specified in Hertz (Hz) and can provided in several ways. If pitch is specified as an **integer**, pitch is assumed constant across phonemes:

``` python
kaffE1 = mbrola.MBROLA(phon=phons, pitch=200)
```

If pitch is specified as a **list of integers**, with one value per provided phoneme, the resulting pitch contour will be remain constant at each value for the time spanned by its corresponding phoneme.

``` python
pitch = [200, 50, 50, 75, 100]
kaffE1 = mbrola.MBROLA(phon=phons, pitch=pitch)
```

If any elements in the list of pitch values is `None` or an empty list `[]`, that value is converted to the default pitch value (200 Hz), and treated as if such value had been provided as an integer instead.

``` python
pitch = [300, [], 100, 50, []]
kaffE1 = mbrola.MBROLA(phon=phons, pitch=pitch)
```

Pymbrola supports the piecewise linear description of pitch from MBROLA. If pitch is specified as a list of tuples (pairs of values), each element in the list will be mapped to each phoneme. Non-empty lists in the pitch specification must consist of lists of tuples. Each tuple contains two values. The first value is the time (as a percentage of the duration of the phoneme) at which the pitch should be modified inside the phoneme (as a float or integer), and the second value is the pitch that should be set at that time (as an integer).

For instance, in the following example pitch is specified so that:

1)  First phoneme (`k`): Pitch remains constant at 300 Hz.
2)  Second phoneme (`a`): Pitch starts at 200 Hz, then changes to 50 Hz at 25 ms after phoneme onset, then changes to 100 Hz after 50 ms, then changes to 90 Hz after 90 ms.
3)  Rest of the phonemes (`f`, `f`, `E1`): Pitch changes to 300 Hz after 50 ms.

``` python
pitch = [300, [(25, 50), (50, 100), (75, 150), (90, 200)], 100, 100]
kaffE1 = mbrola.MBROLA(phon=phons, pitch=pitch)
```

## PHO files

Under the hood, Pymbrola transforms the provided inputs into a string formatted as a PHO file. These files contain the instructions that MBROLA needs to synthesize the sound. You can check what the PHO file of a `MBROLA` instance looks like using the `pho` attribute, or exporting it as a PHO file to your file system using the `export_pho` method:

``` python
kaffE1 = mbrola.MBROLA(phon=phons)

print(kaffE1.pho)
# ['; k a f f E1',
#'_ 1',
#'k 100 (0, 300)',
#'a 100 ',
#'f 100 (0, 100)',
#'f 100 (0, 50)',
#'E1 100 ',
#'_ 1']

kaffE1.export_pho("kaffE1.pho")
```

## Audio file synthesis

Finally, the audio can be synthesized and written in disk in WAV format by using the `to_sound` method and specifying the desired voice to use:

``` python
kaffE1.to_sound("kaffE1.wav", voice="it4")
```

![Oscillogram and Mel-spectrogram for `k a f f E1`, synthesized with `it4` voice.](kaffE1.png)

# Research impact statement

# Citations

# AI usage disclosure

AI was used to generate boilerpolate code for unit tests of the Python functions. In all instances, the authors have reviewed the suggestions and edited them if necessary.

# Acknowledgements

Funded by the European Union. Views and opinions expressed are however those of the author(s) only and do not necessarily reflect those of the European Union or the European Research Council Executive Agency (ERCEA). Neither the European Union nor the granting authority can be held responsible for them. This work is supported by the ERC StG 101115991 (GALA) awarded to Chiara Santolin.

# References