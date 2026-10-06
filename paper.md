---
title: 'Gala: A Python package for galactic dynamics'
tags:
  - Python
  - astronomy
  - dynamics
  - galactic dynamics
  - milky way
authors:
  - name: Gonzalo García-Castro
    orcid: 0000-0002-8553-4209
    equal-contrib: true
    affiliation: 1
  - name: Chiara Santolin
    orcid: 0000-0002-8361-5574
    affiliation: 1
affiliations:
 - name: Institut de Recerca Sant Joan de Déu
   index: 1

date: 2 October 2026
bibliography: paper.bib
---

# Summary

MBROLA [@dutoit1996mbrola] is an open source software project aimed at supporting multi-language Text-To-Speech (TTS) synthesis. MBROLA is based on the Multi-Band Resynthesis OverLap Add (MBROLA) algorithm, which concatenates naturally pre-recorded diphones (i.e., combinations of two speech sounds, like /ke/ or /li/), in a way that minimizes concatenation mismatches between audios, ultimately leading to higher-quality speech synthesis than most TTS software available at the time [@dutoit1993mbr]. Since its first release, MBROLA has served as one of the most relied upon backends for TTS, and its diphone database has been extended to at least 75 languages and dialects (refered to as *voices* by MBROLA) (<https://github.com/numediart/MBROLA-voices>).

More recent speech synthesisers have been released since MBROLA, most of which produce a much more natural-sounding output. These models work very differently compared to MBROLA: they are being trained on massive amounts of text and speech data, and become very good at finding out how particular combinations of characters are supposed to sound like when read aloud. This is very convenient when one simply wants some text to be "read" aloud by the machine.

MBROLA works in a very different way. First, MBROLA takes phonetic symbols as input. It then looks up which diphones are available in the database of a particular language, and then puts them together to produce a sound using the aforementioned MBROLA algorithm.


The fact that MBROLA needs an extra layer of specification to act like an end-to-end TTS software represents a limitation compared to more recent softqware, in which text and sounds are mapped directly. While some later developed pieces of software have been developed to fill this gap...

However, it is precisely this direct manipulation of phonological properties of the output that has made MBROLA of high interest for experimental psycholinguistic research. Desiging an experimental study in psycholinguistics often involves presenting participants with auditory stimuili, some of which belong to a category or another. Participants are asked to perform a task

MBROLA is no longer being mantained and public copies of this software are limited

This is one of the best features of MBROLA: it provides fine-grained control over the phonology of the output. The user can also specify the duration of each phone, and modulate the pitch contour in an almost arbitrary way. Most importantly (IMO), the input consists in phonetic symbols, which provides much more control over the phonological features of the segments present in the output. For these reasons, many psycholinguistics researchers have relied on MBROLA to synthesise their auditory speech stimuli for experiments when fine control is required. For instance, this is the input that MBROLA takes to generate the word “caffè” (/kafˈfɛ/) in Italian:

# Statement of need


pymbrola provides certain benefits, compared to calling MBROLA from the terminal. First, while some Python users are familiar with bash (the programming language used to interact with the Linux kernel), many other users are not. Getting MBROLA to work using the terminal can take a while, especially if one wants to fine-tune some parameters like phoneme duration or pitch contours. If one needs to generate many audios, calling MBROLA commands for each one of the audios is quite inefficient, but its alternative—calling MBROLA using for loops—requires some bash programming abilities that some may not have the time to acquire.

I made pymbrola with the intention of providing an intermediate point, in which the Python user can call MBROLA commands from the Python console. This way, manipulating parameters or using for loops can be done within Python. Here, I will illustrate some use cases for pymbrola.

# State of the field

MBROLA is not currently being mantained, and their main website is down. Plus, there aren’t many up-to-date resources out there explaining how to use MBROLA. Getting MBROLA to run in your computer can be a bit daunting, so after having gone through it, I hope this small guide can help other people do it in a less painful way.

    
                                                                                    

# Software design

The authors note that this set of symbols is aligned with the SAMPA transcription system, which makes it a bit more predictable. They also provide some nice example to illustrate the phoneme that eah symbol refers to. Now we know we transcibe our word caffè as k a f f E11. Let’s now implement this transciption using pymbrola.

The main feature of the pymbrola module is the MBROLA class, which we can call specifying the word label (caffè), the list of phonmees to be played (k a f f E1).

This is a printed representation of the PHO file (.pho) which MBROLA will use to synthesise the word under the hood. Normally, one would manually write such a file, but pymbrola generates it automatically using the arguments passed to the instance of MBROLA. We can export this PHO file using the export_pho() method:

Inspecting this file, we can see that line comments are specified with the ; character2. pymbrola prints the word label in this first line, as a comment—it’s easier to read the word label than figuring it out from the phonological symbols that follow.

In the next few lines, we define the actual sounds that MBROLA will synthesise, specified sequentially in different rows. We first have a pause symbol (_). This symbol is universal for all MBROLA languages. MBROLA needs a silence before and after the other symbols3. The first character after each symbol corresponds to the duration of its associated sound in milliseconds. We are specifying the duration of this onset silence as a default value of 1 millisecond, which is imperceptible by the human ear, making it equivalent to almost no silence at onset. Same goes for the offset silence at the end of the document.


In the middle, we have several symbols corresponding to the phonemes that make up the word caffè in Italian: k, a, f, f, E1. Again, after each symbol we specify its duration. Since we did not specify otherwise, the duration of each phoneme is assigned 100 milliseconds by default. In next examples we will adjust this parameter at will. The two numbers that follow indicate the pitch contour inside the phoneme—how the pitch increases and decreases within each sound. Again, we are leaving the default options: the pitch starts and ends at 200 Hz with no changes in the middle.


The resulting MBROLA object we created is all MBROLA needs to synthesise the sounds we want. Let’s do it:

We can shorten or lengthen the whole audio by a constant (all sounds are modified equally) using the dur_ratio argument in the make_sound() method. A value of 1.0 leaves the audio unnmodified. Smaller values shorten the audio duration:


We can shorten or lengthen the whole audio by a constant (all sounds are modified equally) using the dur_ratio argument in the make_sound() method. A value of 1.0 leaves the audio unnmodified. Smaller values shorten the audio duration:

To manipulate the individual duration of each phoneme, we need to specify it when create the MBROLA instance. We can do this by specifying a single positive integer in the durations argument, or a list of positive integer with same length as number of phonemes. The former option leads to all phonemes being given that same value. The latter, a list, assigns each duration to each phoneme:

As you see, we have lengthened the two vowels a and E1, shortened the onset phoneme k and left the rest of the phonemes f and f equal4. Let’s see how it sounds, can you spot the difference?

We also have several methods to alter the pitch contour of the word-form. As we did before with duration, we can also modify the pitch of the whole word by a constant. Let’s raise the pitch to 400 Hz (double):

We can also pass a list of pitch values in a list of length equal to the number of phonemes:

Here we have passed a list of pitch values (in Hz) that make the first syllable have a higher pitch, compared to the second one. Can you hear the difference?

As you can see, I’ve specified a list of values for the pitch of the last phoneme E1: pitch starts at 200 Hz, continues at 250 Hz, 300 Hz, and finally, 44 Hz. The rest of the phonemes have the same values as in the previous example. I’ve also modified the duration of the last phoneme /e/ to 500 milliseconds to make the pith modulation easier to perceive. Under the hood, MBROLA will divide the time span of the last phoneme (500 ms) into equal intervals (where equals the number of values passed for the pitch contour of such phoneme), and change the pitch linear at each point by the corresponding value:

# Research impact statement

pymbrola provides a convenient Python interface to MBROLA, which allows modifying the duration and pitch contour of particular phonemes by simplify specifying the arguments provided in during the creation of a MBROLA instance, or during the synthesis of the audio when calling the make_sound() method. This makes it easier for the average Python user to generate multiple MBROLA sounds in a programmatic, faster, and more reproducible way.


# Citations

# Figures


# AI usage disclosure

No generative AI tools were used in the development of this software, the writing of this manuscript, or the preparation of supporting materials.

# Acknowledgements

# References