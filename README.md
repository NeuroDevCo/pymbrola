# pymbrola

[![PyPI - Version](https://img.shields.io/pypi/v/mbrola.svg)](https://pypi.org/project/mbrola)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mbrola.svg)](https://pypi.org/project/mbrola)

-----


## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

MBROLA is currently available only on Linux-based systems like Ubuntu, or on Windows via the [Windows Susbsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install). Install MBROLA in your machine following the instructions in the [MBROLA repository](https://github.com/numediart/MBROLA). If you are using WSL, install MBROLA in WSL. After this, you should be ready to install **pymbrola** using pip.

```console
pip install mbrola
```

## Usage

The mbrola module provides the `MBROLA` class, which contains the necessary information to generate the audio file later. The `make_sound` generates a WAV file. 

```python
import mbrola as mb

house = mb.MBROLA(
    word = "house", 
    phonemes = ["h", "a", "U", "s"],
    durations = "100",
    pitch = 200
)

house.export_pho("house.pho")
house.make_sound("house.wav", voice = "en1")
```

## License

`pymbrola` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
