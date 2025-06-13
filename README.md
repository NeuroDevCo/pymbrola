# pymbrola

[![PyPI - Version](https://img.shields.io/pypi/v/mbrola.svg)](https://pypi.org/project/mbrola)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mbrola.svg)](https://pypi.org/project/mbrola)

-----

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

- Python 3.8+
- [MBROLA binary](https://github.com/numediart/MBROLA) installed and available in your system path, or via WSL for Windows users.
- MBROLA voices (e.g., `it4`) must be installed at `/usr/share/mbrola/<voice>/<voice>`.

## Installation

MBROLA is currently available only on Linux-based systems like Ubuntu, or on Windows via the [Windows Susbsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install). Install MBROLA in your machine following the instructions in the [MBROLA repository](https://github.com/numediart/MBROLA). If you are using WSL, install MBROLA in WSL. After this, you should be ready to install **pymbrola** using pip.

```console
pip install mbrola
```

## Usage

### Synthesize a Word

```python
import mbrola

# Create an MBROLA object
house = mbrola.MBROLA(
    word="house",
    phon=["h", "a", "U", "s"],
    durations=100,  # or [100, 120, 100, 110]
    pitch=[200, [200, 50, 200], 200, 100]
)

# Display phoneme sequence
print(house)

# Export PHO file
house.export_pho("house.pho")

# Synthesize and save audio (WAV file)
house.make_sound("house.wav", voice="it4")
```

The module uses the MBROLA command line tool under the hood. Ensure MBROLA is installed and available in your system path, or WSL if on Windows.


## Troubleshooting

- Ensure MBROLA and the required voices are installed and available at `/usr/share/mbrola/<voice>/<voice>`.
- If you encounter an error about platform support, make sure you are running on Linux or WSL.
- Write an [issue](https://github.com/NeuroDevCo/pymbrola/issues), I'll look into it ASAP.

## License

`pymbrola` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
