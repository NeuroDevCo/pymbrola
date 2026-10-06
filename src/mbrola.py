"""
A Python front-end to MBROLA.

The MBROLA class provides all necessary features to install MBROLA and MBROLA voices, specify the string of phonemes in a desired speech synthesis, their duration, their pitch, and to generate the resulting audio file locally.

References:
    Dutoit, T., Pagel, V., Pierret, N., Bataille, F., & Van der Vrecken, O. (1996, October). The MBROLA project: Towards a set of high quality speech synthesizers free of use for non commercial purposes. In Proceeding of Fourth International Conference on Spoken Language Processing. ICSLP'96 (Vol. 3, pp. 1393-1396). IEEE. https://doi.org/10.1109/ICSLP.1996.607874
"""

import os
import platform
import shutil
import subprocess as sp
from copy import deepcopy
from functools import cache, partial, singledispatch
from pathlib import Path
from typing import TypeAlias

import requests
from tqdm import tqdm

# global variables
_DOT_MBROLA = ".mbrola"
MBROLA_REPO = "numediart/MBROLA"
VOICES_REPO = "numediart/MBROLA-voices"
API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
TIMEOUT = (10, 120)  # (connect, read) seconds

# custom types
Number: TypeAlias = float | int
PitchElement: TypeAlias = Number | list[tuple[Number, Number]]
PitchInput: TypeAlias = Number | list[PitchElement] | list[tuple[Number, Number]]
PitchOutput: TypeAlias = list[list[tuple[float, float]]]


# exceptions
class MissingMBROLAException(RuntimeError):
    "Could not find mbrola file in specified location."


class MissingVoiceException(Exception):
    """Voice not found in voices folder."""


class PlatformException(Exception):
    """Raise error platform is not Linux or Windows Subsystem for Linux.

    Args:
        Exception (Exception): A super class Exception.
    """

    def __init__(self):
        self.message = f"MBROLA is only available on {platform.system()} using the Windows Subsystem for Linux (WSL).\nPlease, follow the instructions in the WSL site: https://learn.microsoft.com/en-us/windows/wsl/install."
        super().__init__(self.message)


class MBROLAInstallException(RuntimeError):
    """Unrecoverable error; mirrors `exit 1` in the original bash script."""


# main class
class MBROLA:
    """A class for generating MBROLA sounds.

        An MBROLA class contains the necessary elements to synthesise an audio using MBROLA.

        Args:
            phon (str | list[str]): list of phonemes.
            durations (float | list[float], optional): phoneme duration in milliseconds. Defaults to 100. If an integer is provided, all phonemes in `phon` are assumed to be the same length. If a list is provided, each element in the list indicates the duration of each phoneme.
            pitch (float | list[float] | list[float | list[float | tuple[float, float]]]): pitch in Hertz (Hz). If an integer is provided, the pitch contour of each phoneme is assumed to be constant within and across phonemes (e.g., all phonemes will have a pitch of 200 Hz). If a list is provided, each element provides the pitch specification of the piecewise linear pitch curve of each phoneme. This list should have same length as `phon`. Each element in this list should be a list of an arbitrary number of tuples. Each tuple indicates the time (in percentage of the audio) at which the pitch should be modified, and the pitch value (in Hertz) that should be set.
            outer_silences (tuple[float, float], optional): duration in milliseconds of the silence interval to be inserted at onset and offset. Defaults to (1, 1).

        Attributes:
            phon (list[str]): list of phonemes.
            durations (list[float] | float, optional): phoneme duration in milliseconds. Defaults to 100. If an integer is provided, all phonemes in `phon` are assumed to be the same length. If a list is provided, each element in the list indicates the duration of each phoneme.
            pitch (float | list[float] | list[tuple[float, float]]): pitch in Hertz (Hz). If an integer is provided, the pitch contour of each phoneme is assumed to be constant within and across phonemes (e.g., all phonemes will have a pitch of 200 Hz). If a list is provided, each element provides the pitch specification of the piecewise linear pitch curve of each phoneme. This list should have same length as `phon`. Each element in this list should be a list of an arbitrary number of tuples. Each tuple indicates the time (in percentage of the audio) at which the pitch should be modified, and the pitch value (in Hertz) that should be set.
            outer_silences (tuple[float, float], optional): duration in milliseconds of the silence interval to be inserted at onset and offset. Defaults to (1.0, 1.0).

        Examples:
            >>> house = MBROLA(
                    phon = ["h", "a", "U", "s"],
                    durations = 100,
                    pitch = 200
                )

    :meta public:
    """

    def __init__(
        self,
        phon: str | list[str],
        durations: Number | list[Number] = 100,
        pitch: PitchInput = 200,
        outer_silences: tuple[Number, Number] = (1, 1),
    ):
        """Initiate MBROLA instance.

        :meta private:
        """

        if isinstance(phon, str):
            phon = list(phon) if len(phon) > 1 else [phon]

        self.phon = list(map(str, phon))
        self.durations = validate_durations(durations, phon)
        self.pitch = validate_pitch(pitch, self.phon)
        self.outer_silences = validate_outer_silences(outer_silences)
        self.pho = make_pho(self)

    def __repr__(self) -> str:
        cls = self.__class__.__name__ + "("
        attrs = self.__dict__.items()

        for i, (k, v) in enumerate(attrs):
            if k == "pho":
                continue

            cls += f"{k}={v!r}, " if i != (len(attrs) - 2) else f"{k}={v!r}"

        return cls + ")"

    def __str__(self) -> str:
        cls = self.__class__.__name__ + "("
        attrs = self.__dict__.items()

        for i, (k, v) in enumerate(attrs):
            if k == "pho":
                continue

            cls += f"{k}={v!r}, " if i != (len(attrs) - 2) else f"{k}={v!r}"

        return cls + ")"

    def __len__(self) -> int:
        """Get number of phonemes in MBROLA instance.

            Returns:
                int: Number of phonemes in MBROLA instance.

            Examples:
                >>> house = MBROLA(phon = ["h", "a", "U", "s"])
                >>> len(house)
                4
        :meta public:
        """
        return len(self.phon)

    def __eq__(self, other) -> bool:
        """Check if two MBROLA instances are equal.

            Args:
                other (MBROLA): Another MBROLA instance to compare.
            Returns:
                bool: True if both MBROLA instances are equal.

            Examples:
                >>> house = MBROLA(phon = ["h", "a", "U", "s"])
                >>> house_1 = MBROLA(phon = ["h", "a", "U", "s"])
                >>> house==house_1
                True
                >>> house = MBROLA(phon = ["h", "a", "U", "s"])
                >>> caffe = MBROLA(phon = ["k", "a", "f", "f", "E"])
                >>> house_0==house_1
                False
                >>> house = MBROLA(phon = ["h", "a", "U", "s"])
                >>> house_300 = MBROLA(phon = ["h", "a", "U", "s"], duration=300)
                >>> house==house_300
                True

        :meta public:
        """
        return self.pho == other.pho

    def __add__(self, other):
        """Concatenate phonemes from two MBROLA instances.

        Args:
            other (MBROLA): Another MBROLA instance to concatenate.

        Returns:
            MBROLA: Concatenated MBROLA instance.

        Examples:
            >>> house = MBROLA(phon = ["h", "a", "U", "s"])
            >>> len(house)
            4
            >>> house_1 = MBROLA(phon = ["h", "a", "U", "s"])
            >>> len(house_1)
            4
            >>> len(house + house_1)
            8

        :meta public:
        """
        new = self.copy()
        new.phon = self.phon + other.phon
        new.pho = self.pho + other.pho

        return new

    def copy(self):
        """Make deep copy of MBROLA instance.

        Returns:
            MBROLA: Deep copy of original MBROLA instance.

        Examples:
            >>> house = MBROLA(phon = ["h", "a", "U", "s"])
            >>> house_1 = house.copy()
            >>> house == house_1
            True
            >>> house is house_1
            False

        :meta public:
        """
        return deepcopy(self)

    def export_pho(self, file: str | Path) -> None:
        """Save PHO file.

        Args:
            file (str): Path of the output PHO file.

        Examples:
            >>> house = MBROLA(phon = ["h", "a", "U", "s"])
            >>> house.export_pho("sample.pho")

        :meta public:
        """
        with Path(file).open("w", encoding="utf-8") as f:
            f.write("\n".join(self.pho))

    def make_sound(
        self,
        file: str | Path,
        voice: str = "it4",
        f0_ratio: float = 1.0,
        dur_ratio: float = 1.0,
        remove_pho: bool = True,
    ) -> None:
        """Generate MBROLA sound WAV file.

        Args:
            file (str): Path to the output WAV file.
            voice (str, optional): MBROLA voice to use. Defaults to "it4". Note phoneme symbols may be specific to voices.
            f0_ratio (float, optional): Constant to multiply the fundamental frequency of the whole sound by. Defaults to 1.0 (same fundamental frequency).
            dur_ratio (float, optional): Constant to multiply the duration of the whole sound by. Defaults to 1.0 (same duration).
            remove_pho (bool, optional): Should the intermediate PHO file be deleted after the sound is created? Defaults to True.

        Examples:
            >>> house = MBROLA(phon = ["h", "a", "U", "s"])
            >>> house.make_sound("sound.wav", voice="en1")
            >>> house.make_sound("sound.wav", f0_ratio=0.5, voice="en1") # reduce F0 to half the original Hz.
            >>> house.make_sound("sound.wav", dur_ratio=2.0, voice="en1") # make audio double as fast
            >>> house.make_sound("sound.wav", remove_pho=False, voice="en1") # keep pho file in same directory

        :meta public:
        """
        mbrola_path()
        file = Path(file)
        file_str = str(file)

        pho = file.with_suffix(".pho")
        voice_str = validate_voice(voice)

        with Path(pho).open(mode="w", encoding="utf-8") as f:
            f.write("\n".join(self.pho))

        cmd_str = (
            f"{mbrola_cmd()} -f {f0_ratio} -t {dur_ratio} {voice_str} {pho} {file_str}"
        )

        try:
            sp.check_output(cmd_str, shell=True)
        except sp.CalledProcessError as e:
            raise RuntimeError(f"Error when generating {file}:\n{e}")

        f.close()
        if remove_pho:
            pho.unlink()


def make_pho(x: MBROLA) -> list[str]:
    """Generate PHO file.

    A PHO (.pho) file contains the phonological information of the speech sound in a format that MBROLA can read. See more examples in the MBROLA documentation (https://github.com/numediart/MBROLA).

    Arguments:
        x (MBROLA): MBROLA object to make a PHO file for.

    Returns:
        list[str]: Lines in the PHO file.
    """
    pho = [f"; {' '.join(x.phon)}", f"_ {x.outer_silences[0]}"]

    for ph, d, p in zip(x.phon, x.durations, x.pitch):
        p_seq = " ".join([str(pi) for pi in p])
        pho.append(" ".join(map(str, [ph, d, p_seq])))

    pho.append(f"_ {x.outer_silences[1]}")

    return pho


# validation functions
def validate_voice(voice: str) -> str:
    """Checks that provided voice is available in MBROLA folder.

    Check available voices here https://github.com/numediart/MBROLA-voices, and isntall them using `install_voices()`.

    Args:
        voice (str): Voice to check.

    Raises:
        MissingVoiceException: If provided voice is not available.

    Returns:
        str: Path to validated voice.
    """
    voices_path = mbrola_path() / "Voices"

    available_voices = [p.name for p in voices_path.glob("*")]

    if voice not in available_voices:
        msg = f"Voice '{voice}' not found in `voices_path` '{voices_path}'. Please, install MBROLA voices using `install_voices({voice})` or use the `voices_path` argument to point to the folder that contains installed MBROLA voices."
        raise MissingVoiceException(msg)

    return str(voices_path / voice / voice)


@singledispatch
def validate_durations(
    durations: Number | list[Number], phon: list[str]
) -> list[float]:
    """Validate argument `durations`.

    Args:
        durations (float | list[float], optional): phoneme duration in milliseconds. Defaults to 100.
        phon (list[str]): string or list of phonemes.

    Raises:
        ValueError: if length of durations is different than length of phon.
        TypeError: if durations is not a float or a list of floats.

    Returns:
        list[float]: Phoneme durations.

    """
    raise TypeError(
        f"`durations` must be a float or list of floats with length {len(phon)}, but {type(durations)} was provided"
    )


@validate_durations.register
def _(durations: Number, phon: str | list[str]) -> list[float]:
    return [durations] * len(phon)


@validate_durations.register
def _(durations: list, phon: str | list[str]) -> list[float]:
    if len(durations) != len(phon):
        raise ValueError(f"`{durations}` must be the same length as {phon}")

    return list(map(float, durations))


@singledispatch
def validate_pitch(pitch: PitchInput, phon: str | list[str]) -> PitchOutput:
    """Validate argument `pitch`.

    Args:
        pitch (float | list[float] | list[float | list[float | tuple[float, float]]]): pitch in Hertz (Hz). If an integer is provided, the pitch contour of each phoneme is assumed to be constant within and across phonemes (e.g., all phonemes will have a pitch of 200 Hz). If a list is provided, each element provides the pitch specification of the piecewise linear pitch curve of each phoneme. This list should have same length as `phon`. Each element in this list should be a list of an arbitrary number of tuples. Each tuple indicates the time (in percentage of the audio) at which the pitch should be modified, and the pitch value (in Hertz) that should be set.
        phon (str | list[str]): string or list of phonemes.

    Raises:
        ValueError: if `pitch` is a list of different length as `phon`.
        TypeError: `pitch` is not an float or a list[tuple[float, float]]"

    Returns:
        float | list[float] | list[float | list[float | tuple[float, float]]]: validated pitch.

    """
    raise TypeError(
        f"`pitch` must be a float or list of floats, but {type(pitch)} was provided"
    )


@validate_pitch.register
def _(pitch: Number, phon: list[str]) -> PitchOutput:
    return [[(0, pitch)]] * len(phon)


@validate_pitch.register
def _(pitch: list, phon: list[str]) -> PitchOutput:
    error = TypeError("All elements in `pitch` must be list[tuple[float, float]]")
    if len(pitch) != len(phon):
        raise ValueError("`pitch` must be of same length as `phon`")

    for i, pit in enumerate(pitch):
        if isinstance(pit, Number):
            pit = [(0, pit)]
            pitch[i] = pit

        is_correct = (
            isinstance(pit, list)
            and all(isinstance(p, tuple) for p in pit if p)
            and all(len(p) == 2 for p in pit if p)
            and all(isinstance(p, Number) for pi in pit for p in pi)
        )
        if not is_correct:
            raise error

    return pitch


def validate_outer_silences(
    outer_silences: tuple[Number, Number],
) -> tuple[Number, Number]:
    """Validate argument `outer_silences`.

    Args:
        outer_silences (tuple[float, float]): duration in milliseconds of the silence intervals to be inserted at onset and offset. Defaults to (1, 1).

    Raises:
        TypeError: if `outer_silences` is not a tuple of float of length 2.

    Returns:
        tuple[float, float]: validated outer silences.
    """

    if (
        not isinstance(outer_silences, tuple)
        or len(outer_silences) != 2
        or not all(isinstance(o, Number) for o in outer_silences)
    ):
        raise TypeError("`outer_silences` must be a tuple of float of length 2")
    return outer_silences


# path functions
def mbrola_path() -> Path:
    """
    Retrieve (or get default '~/.mbrola') path to MBROLA installation folder, validate, and save in Python environment.

    Returns:
        Path: PAth to MBROLA installation folder.
    """
    if "MBROLA" in os.environ and len(os.environ["MBROLA"]) > 0:
        mbrola = Path(os.environ["MBROLA"])
    else:
        mbrola = Path(Path.home() / _DOT_MBROLA).expanduser()

    mbrola = validate_mbrola_path(mbrola)
    os.environ["MBROLA"] = str(mbrola)

    return mbrola


def validate_mbrola_path(path: Path) -> Path:
    """Validate MBROLA path.

    Args:
        path (Path): Path to MBROLA installation.

    Raises:
        MissingMBROLAException: If path does not exists, if path is not a directory, or if path does not contain a MBROLA file in 'Bin/'.

    Returns:
        Path: Validated path.
    """

    if not path.exists() or not path.is_dir():
        msg = f"Could not locate MBROLA directory in '{path}'. Please, set the appropriate path to your MBROLA installation using `set_mbrola_path()` or install MBROLA using `install_mbrola()` in your desired location."

        raise MissingMBROLAException(msg)

    file_path = path / "Bin" / "mbrola"

    if not file_path.exists():
        msg = f"Could not locate mbrola file in '{path}. Please, provide the path to you MBROLA file or install MBROLA using `install_mbrola()` in your desired location."

        raise MissingMBROLAException(msg)

    return path


def set_mbrola_path(path: Path | str) -> None:
    """
    Validate, then set MBROLA directory path in Python environment.

    Args:
        path: Path to MBROLA installation.
    """
    path = Path(path)
    validate_mbrola_path(path)
    os.environ["MBROLA"] = str(path)


@cache
def mbrola_cmd() -> str:
    """
    Get MBROLA command for system command line.

    Returns:
        str: Validated path to MBROLA file.
    """
    mbrola_file = mbrola_path() / "Bin/mbrola"
    if is_wsl() or os.name == "posix":
        return str(mbrola_file)

    if os.name == "nt" and wsl_available():
        return "wsl " + str(mbrola_path / mbrola_file)

    raise PlatformException()


@cache
def is_wsl(version: str = platform.uname().release) -> bool:
    """Evaluate if function is running on Windows Subsystem for Linux (WSL).

    Returns:
        bool: returns `True` if Python is running in WSL, otherwise `False`.
    """
    return version.endswith("microsoft-standard-WSL2")


@cache
def wsl_available() -> bool | int:
    """
    Check if Windows Subsystem for Linux (WSL is available).

    Returns:
        bool | int: `True` if Windows Subsystem for Linux (WLS) is available from Windows, otherwise `False`

    :meta private:
    """
    if os.name != "nt" or not shutil.which("wsl"):
        return False

    cmd = partial(sp.check_output, timeout=5, encoding="UTF-8", text=True)

    try:
        return is_wsl(cmd(["wsl", "uname", "-r"]).strip())
    except sp.SubprocessError:
        return False


# installation functions
def download_resource(url: str, path: Path):
    """Download resource from URL.

    Args:
        url (str): URL of file to download.
        path (Path): Destination path of downloaded file.

    Raises:
        MBROLAInstallException: If download fails.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with requests.get(url, stream=True, timeout=TIMEOUT) as r:
            r.raise_for_status()

            with open(path, "wb") as fh:
                fh.writelines(c for c in r.iter_content(chunk_size=1 << 16))
    except (requests.RequestException, OSError) as e:
        raise MBROLAInstallException(f"Failed to download {path.name}") from e


def get_filetree(url: str) -> list[str]:
    """Get file tree in URL.

    Args:
        url (str): URL to get file tree from.

    Raises:
        MBROLAInstallException: If repository is truncated (too large) or request exception is encountered.

    Returns:
        list[str]: List of files found in filetree.
    """
    try:
        r = requests.get(url, params={"recursive": "1"}, timeout=TIMEOUT)
        r.raise_for_status()
        tree = r.json()

        if tree.get("truncated"):
            raise MBROLAInstallException("Repository tree too large to list.")

        files = [e["path"] for e in tree["tree"] if e["type"] == "blob"]

    except requests.RequestException as e:
        raise MBROLAInstallException("Failed to list MBROLA voices.") from e

    return files


def install_voice(
    voice: str | list[str] | None = None, path: Path | None = None
) -> bool:
    """
    Download and install MBROLA voices from numediart/MBROLA-voices.

    voice (str | list[str] | None, optional): Voice names to install, e.g. ["es1", "de1"]. If None (default) or empty, installs every voice.
    path (Path | None, optional): Destination folder for MBROLA voices. Defaults to ~/.mbrola/voices.

    Returns:
        bool: True if voices were installed, False if the user declined to
        replace an existing destination directory.

    Examples:
        >>> install_voices("it4") # installs single voice
        >>> install_voices(["it4", "us1"]) # installs selected voices
        >>> install_voices() # installs all available voices
        >>> install_voices(path = Path("sounds")) # installs voices in folder "sounds"

    """
    if path is None:
        path = mbrola_path() / "Voices"

    if isinstance(voice, str):
        voice = [voice]

    Path(path).mkdir(exist_ok=True, parents=True)
    files = get_filetree(f"{API}/repos/{VOICES_REPO}/git/trees/master")

    if not voice:
        voice = sorted({f.split("/")[1] for f in files if "/" in f})

    for v in voice:  # guard against path traversal in user input
        if not v or "/" in v or v in (".", ".."):
            raise MBROLAInstallException(f"Invalid voice name {v!r}.")

    wanted = []
    for name in voice:
        prefix = f"data/{name}/"
        matches = [f for f in files if f.startswith(prefix)]

        if not matches:
            raise MBROLAInstallException(f"Unknown voice {name!r}.")

    pb = tqdm(range(len(wanted)))

    for file in wanted:
        url = f"{RAW}/{VOICES_REPO}/master/{file}"
        fn = file.split("/")  # strip leading "data/"
        download_resource(url, path / Path(*fn[1:]))
        pb.update(1)
        pb.set_description(f"Downloading {fn[1]}")

    return True


def install_mbrola(path: Path | str | None = None) -> None:
    """Install MBROLA.

    This function downloads and compiles MBROLA from https://github.com/numediart/MBROLA.

    Args:
        path (Path | str | None, optional): Desintatino path of MBROLA installation folder. Defaults to `~/.mbrola/`.

    Raises:
        MBROLAInstallException: If MBROLA repository cannot be reached, if download fails, or if compilation fails.
    """
    if isinstance(path, str):
        path = Path(path)

    if path is None:
        path = Path.home() / _DOT_MBROLA

    path.mkdir(exist_ok=True, parents=True)
    files = get_filetree(f"{API}/repos/{MBROLA_REPO}/git/trees/master")

    pb = tqdm(range(len(files)))

    for file in files:
        pb.set_description("Downloading MBROLA")
        url = f"{RAW}/{MBROLA_REPO}/master/{file}"
        download_resource(url, path / file)
        pb.update(1)

    pb.set_description("Compiling MBROLA")

    try:
        sp.run(["make"], cwd=path, capture_output=True, text=True, check=True)
    except OSError as e:
        raise MBROLAInstallException("Failed to compile MBROLA") from e


if __name__ == "__main__":
    install_mbrola()
    install_voice(["it4", "fr1"])

    cafe = MBROLA(
        phon=["k", "a", "f", "f", "E1"],
        durations=[200, 300, 200, 200, 200],
        pitch=[200, [(50.0, 400), (75, 500.0)], [(30, 200.1)], 200.0, []],
        outer_silences=(10, 10),
    )

    cafe.export_pho("test.pho")
    cafe.make_sound("test.wav")
    print(cafe)
