# pymbrola documentation

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/NeuroDevCo/pymbrola/testing.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/mbrola.svg)](https://pypi.org/project/mbrola)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mbrola.svg)](https://pypi.org/project/mbrola)
![GitHub License](https://img.shields.io/github/license/NeuroDevCo/pymbrola)
![PyPI - Status](https://img.shields.io/pypi/status/mbrola)
![Docker Image Size (tag)](https://img.shields.io/docker/image-size/gongcastro/pymbrola/latest)
![GitHub Release](https://img.shields.io/github/v/release/NeuroDevCo/pymbrola)
![Codecov](https://img.shields.io/codecov/c/github/NeuroDevCo/pymbrola)


-----

Contents
--------
.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules


A Python interface for the [MBROLA](https://github.com/numediart/MBROLA) speech synthesizer, enabling programmatic creation of MBROLA-compatible phoneme files and automated audio synthesis. This module validates phoneme, duration, and pitch sequences, generates `.pho` files, and can call the MBROLA executable to synthesize speech audio from text-like inputs.

> **References:**
> Dutoit, T., Pagel, V., Pierret, N., Bataille, F., & Van der Vrecken, O. (1996, October).
> The MBROLA project: Towards a set of high quality speech synthesizers free of use for non commercial purposes.
> In Proceeding of Fourth International Conference on Spoken Language Processing. ICSLP'96 (Vol. 3, pp. 1393-1396). IEEE.
> [https://doi.org/10.1109/ICSLP.1996.607874](https://doi.org/10.1109/ICSLP.1996.607874)

## Features

- **Front-end to MBROLA:** Easily create `.pho` files and synthesize audio with Python.
- **Input validation:** Prevents invalid file and phoneme sequence errors.
- **Customizable:** Easily set phonemes, durations, pitch contours, and leading/trailing silences.
- **Cross-platform (Linux/WSL):** Automatically detects and adapts to Linux or Windows Subsystem for Linux environments.

## Requirements

- Python 3.10+
- [MBROLA binary](https://github.com/numediart/MBROLA) installed and available in your system path, or via WSL for Windows users. To install MBROLA in your UBUNTU or WSL instance, run the [mbrola/install.sh] script:

```bash
sudo bin/install.sh --voice fr2 it4 # install voices fr2 and it4
sudo bin/install.sh --voice all # install all voices
sudo bin/install.sh # install no voices
```

A [Docker image](https://hub.docker.com/repository/docker/gongcastro/mbrola/general) of Ubuntu 22.04 with a ready-to-go installation of MBROLA is available, for convenience.
- MBROLA voices (e.g., `it4`) must be installed at `/usr/share/mbrola/<voice>/<voice>`.

## Installation

MBROLA is currently available only on Linux-based systems like Ubuntu, or on Windows via the [Windows Susbsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install). Install MBROLA in your machine following the instructions in the [MBROLA repository](https://github.com/numediart/MBROLA). If you are using WSL, install MBROLA in WSL. After this, you should be ready to install **pymbrola** using pip.

```bash
pip install mbrola
```

## Usage

### Synthesize a Word

```python
import mbrola

# Create an MBROLA object
caffe = MBROLA(
    word="caffè",
    phon=["k", "a", "f", "f", "E1"],
    durations=100,  # or [100, 120, 100, 110]
    pitch=[100, [200, 50, 200], 100, 100, 200]
)

# Display phoneme sequence
print(caffe)

# Export PHO file
caffe.export_pho("caffe.pho")

# Synthesize and save audio (WAV file)
caffe.make_sound("caffe.wav", voice="it4")
```

The module uses the MBROLA command line tool under the hood. Ensure MBROLA is installed and available in your system path, or WSL if on Windows.

## Specifying the pitch contour

**pymbrola** implements the piecewise linear pitch specification as different inputs:

If pitch is specified as an **integer**, pitch is assumed constant across phonemes:

```python
phon = list("kasa")
pitch = 200
validate_pitch(200, phon)
# [[(0, 200)], [(0, 200)], [(0, 200)], [(0, 200)]]
```

If pitch is specified as a **list**, each element in mapped to each phoneme. Integers in the list are treated as before (constant pitch for the whole phoneme):

```python
phon = list("kasa")
pitch = [200, 50, 50, 100]
validate_pitch(pitch, phon)
# [[(0, 200)], [(0, 50)], [(0, 50)], [(0, 100)]]
```

Empty lists inside the main list are treated as constant pitch sections:

```python
phon = list("kasa")
pitch = [[], 50, [], 100]
validate_pitch(pitch, phon)
# [[], [(0, 50)], [], [(0, 100)]]
```

Non-empty lists must consist in lists of tuples. Each tuple contains two values. The first value is the time (as a percentage of the duration of the phoneme) at which the pitch should be modified inside the phoneme (as a float or integer), and the second value is the pitch that should be set at that time (as an integer):

```python
phon = list("kasa")
pitch = [[], [(25, 50), (50, 100), (75, 150), (90, 200)], [], 100]
validate_pitch(pitch, phon)
# [[], [(25, 50), (50, 100), (75, 150), (90, 200)], [], [(0, 100)]]
```

## Docker image

For convenience, a [Docker image](https://hub.docker.com/repository/docker/gongcastro/pymbrola/general) is available at Dockerhub:

```bash
docker run -it gongcastro/pymbrola:latest
``` 

## Troubleshooting

- Ensure MBROLA and the required voices are installed and available at `/usr/share/mbrola/<voice>/<voice>`.
- If you encounter an error about platform support, make sure you are running on Linux or WSL.
- Write an [issue](https://github.com/NeuroDevCo/pymbrola/issues), I'll look into it ASAP.

## License

`pymbrola` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
