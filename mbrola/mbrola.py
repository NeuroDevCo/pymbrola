"""
A Python front-end to MBROLA.

References:
    Dutoit, T., Pagel, V., Pierret, N., Bataille, F., & Van der Vrecken, O. (1996, October). The MBROLA project: Towards a set of high quality speech synthesizers free of use for non commercial purposes. In Proceeding of Fourth International Conference on Spoken Language Processing. ICSLP'96 (Vol. 3, pp. 1393-1396). IEEE. https://doi.org/10.1109/ICSLP.1996.607874
"""  # pylint: disable=line-too-long

import os
from pathlib import PurePosixPath, Path
import re
from collections.abc import Sequence
import platform
import shutil
from functools import singledispatch, cache, partial
import subprocess as sp


def validate_word(
    word: str, invalid_chars: str = r'[<>:"/\\|?*]', max_chars: int = 255
) -> str:
    """Validate argument `word`.

    Args:
        word (str): label for the mbrola sound.
        invalid_chars (str, optional): invalid characters to look for. Defaults to ``r'[<>:"/\\|?*]'``.
        max_chars (int, optional): maximum allowed characters in word. Defaults to 255.

    Raises:
        TypeError: if `word` is not a str.
        ValueError: if length if `word` exceeds 255 characters. This avoids accidentally very long inputs that could lead to memory issues.
        ValueError: if `word` contains at least one invalid character (['[', '<', '>', ':', '"', '/', '\\', '\\', '|', '?', '*', ']']).

    Returns:
        str: validated word.
    """  # pylint: disable=line-too-long
    if len(word) > max_chars:
        raise ValueError(f"`word` exceeds maximum characters ({max_chars})")
    if re.search(invalid_chars, word):
        raise ValueError(
            f"`word` cannot contain the following characters: {list(invalid_chars)}"
        )
    return word


@singledispatch
def validate_durations(
    durations: int | Sequence[int], phon: Sequence[str]
) -> list[int]:
    """Validate argument `durations`.

    Args:
        durations (int | Sequence[int], optional): phoneme duration in milliseconds. Defaults to 100.
        phon (Sequence[str]): string or list of phonemes.

    Raises:
        ValueError: if length of durations is different than length of phon.
        TypeError: if durations is not a list or int.

    Returns:
        list[int]: Phoneme durations.
    """  # pylint: disable=line-too-long
    raise TypeError(
        f"`durations` must be int or list, but {type(durations)} was provided"
    )


@validate_durations.register
def _(durations: int, phon: str | Sequence[str]) -> list[int]:
    return [durations] * len(phon)


@validate_durations.register
def _(durations: Sequence, phon: str | Sequence[str]) -> list[int]:
    if len(durations) != len(phon):
        raise ValueError(f"`{durations}` must be the same length as {phon}")
    return list(map(int, durations))


@singledispatch
def validate_pitch(pitch: int | Sequence, phon: Sequence[str]) -> list:
    """Validate argument `pitch`.

    Args:
        pitch (int | Sequence, optional): pitch in Hertz (Hz). Defaults to 200. If an integer is provided, the pitch contour of each phoneme is assumed to be constant at the indicated value. If a list of integers or strings is provided, each element in the list indicates the value at which the pitch contour of each phoneme is kept constant. If a list of lists (of integers or strings), each value in each element describes the pitch contour for each phoneme.
        phon (str | Sequence[str]): string or list of phonemes.

    Raises:
        TypeError: if pitch is not int or list.
        TypeError: if pitch is a list but at least one element is not list or int.
        TypeError: if pitch is a list of lists, and at least one element in at least one of the lists is not an int.
        ValueError: if pitch is a list of different length as phon.
    Returns:
        list: validated pitch.
    """
    raise TypeError(f"`pitch` must be int or Sequence, but {type(pitch)} was provided")


@validate_pitch.register
def _(pitch: int, phon: Sequence[str]) -> list:
    return [[pitch, pitch]] * len(phon)


@validate_pitch.register
def _(pitch: Sequence, phon: Sequence[str]) -> list:
    if len(pitch) != len(phon):
        raise ValueError("`pitch` must be of same length as `phon`")
    for i, p in enumerate(pitch):
        if not isinstance(p, (int, list)):
            raise TypeError(
                f"All elements in `pitch` must be int or list, but element {i} ({p}) is {type(p)}"
            )
        if isinstance(p, list) and not all(isinstance(pi, int) for pi in p):
            raise TypeError(
                f"List elements inside `pitch` must contain only int, but element {i} ({p}) contains an non-int."
            )
    return [[p, p] if isinstance(p, int) else p for p in pitch]


def validate_outer_silences(outer_silences: Sequence[int]):
    """Validate argument `outer_silences`.

    Args:
        outer_silences (Sequence[int]): duration in milliseconds of the silence intervals to be inserted at onset and offset. Defaults to (1, 1).

    Raises:
        TypeError: if outer_silences is not a tuple of int of length 2.

    Returns:
        tuple[int, int]: validated outer_silences.
    """

    if (
        not isinstance(outer_silences, tuple)
        or len(outer_silences) != 2
        or not all(isinstance(o, int) for o in outer_silences)
    ):
        raise TypeError("`outer_silences` must be a tuple of int of length 2")
    return outer_silences


class MBROLA:
    """A class for generating MBROLA sounds.

    An MBROLA class contains the necessary elements to synthesise an audio using MBROLA.

    Args:
        word (str): label for the mbrola sound.
        phon (list[str] | tuple[int]): list of phonemes.
        durations (int | Sequence[int], optional): phoneme duration in milliseconds. Defaults to 100. If an integer is provided, all phonemes in ``phon`` are assumed to be the same length. If a list is provided, each element in the list indicates the duration of each phoneme.
        pitch (list[int] | int, optional): pitch in Hertz (Hz). Defaults to 200. If an integer is provided, the pitch contour of each phoneme is assumed to be constant at the indicated value. If a list of integers or strings is provided, each element in the list indicates the value at which the pitch contour of each phoneme is kept constant. If a list of lists (of integers or strings), each value in each element describes the pitch contour for each phoneme.
        outer_silences (tuple[int, int], optional): duration in milliseconds of the silence interval to be inserted at onset and offset. Defaults to (1, 1).

    Attributes:
        word (str): label for the mbrola sound.
        phon (Sequence[str]): list of phonemes.
        durations (list[int] | int, optional): phoneme duration in milliseconds. Defaults to 100. If an integer is provided, all phonemes in ``phon`` are assumed to be the same length. If a list is provided, each element in the list indicates the duration of each phoneme.
        pitch (list[int] | int, optional): pitch in Hertz (Hz). Defaults to 200. If an integer is provided, the pitch contour of each phoneme is assumed to be constant at the indicated value. If a list of integers or strings is provided, each element in the list indicates the value at which the pitch contour of each phoneme is kept constant. If a list of lists (of integers or strings), each value in each element describes the pitch contour for each phoneme.
        outer_silences (tuple[int, int], optional): duration in milliseconds of the silence interval to be inserted at onset and offset. Defaults to (1, 1).
    Examples:
        >>> house = mb.MBROLA(
                word = "house",
                phonemes = ["h", "a", "U", "s"],
                durations = "100",
                pitch = [200, [200, 50, 200], 200, 100]
            )
    """  # pylint: disable=line-too-long

    def __init__(
        self,
        word: str,
        phon: str | Sequence[str],
        durations: int | Sequence[int] = 100,
        pitch: int | Sequence[int] = 200,
        outer_silences: Sequence[int] = (1, 1),
    ):
        self.word = validate_word(word)
        self.phon = list(map(str, phon))
        self.durations = validate_durations(durations, phon)
        self.pitch = validate_pitch(pitch, self.phon)
        self.outer_silences = validate_outer_silences(outer_silences)
        self.pho = make_pho(self)

    def __str__(self):
        return f"MBROLA object for word {self.word}:" + "\n" + "\n".join(self.pho)

    def __repr__(self):
        return f"MBROLA object for word '{self.word}':" + "\n" + "\n".join(self.pho)

    def __len__(self):
        return len(self.phon)

    def __eq__(self, other):
        return self.pho == other.pho

    def __add__(self, other, sep="_"):
        self.word = self.word + sep + other.word
        self.phon = self.phon + other.phon
        self.pho = self.pho + other

    def export_pho(self, file: str) -> None:
        """Save PHO file.

        Args:
            file (str): Path of the output PHO file.
        """
        try:
            with open(f"{file}", "w+", encoding="utf-8") as f:
                f.write("\n".join(self.pho))
        except FileNotFoundError:
            print(f"{file} is not a valid path")

    def make_sound(
        self,
        file: str,
        voice: str = "it4",
        f0_ratio: float = 1.0,
        dur_ratio: float = 1.0,
        remove_pho: bool = True,
    ):
        """Generate MBROLA sound WAV file.

        Args:
            file (str): Path to the output WAV file.
            voice (str, optional): MBROLA voice to use. Defaults to "it4". Note phoneme symbols may be specific to voices.
            f0_ratio (float, optional): Constant to multiply the fundamental frequency of the whole sound by. Defaults to 1.0 (same fundamental frequency).
            dur_ratio (float, optional): Constant to multiply the duration of the whole sound by. Defaults to 1.0 (same duration).
            remove_pho (bool, optional): Should the intermediate PHO file be deleted after the sound is created? Defaults to True.
        """
        with open("tmp.pho", mode="w", encoding="utf-8") as f:
            f.write("\n".join(self.pho))
        cmd_str = f"{mbrola_cmd()} -f {f0_ratio} -t {dur_ratio} /usr/share/mbrola/{voice}/{voice} tmp.pho {PurePosixPath(file)}"
        try:
            sp.check_output(cmd_str)
        except sp.CalledProcessError as e:
            print(f"Error when making sound for {file}: {e}")
        f.close()
        if remove_pho:
            os.remove("tmp.pho")


def make_pho(x) -> list[str]:
    """Generate PHO file.

    A PHO (.pho) file contains the phonological information of the speech sound in a format that MBROLA can read. See more examples in the MBROLA documentation (https://github.com/numediart/MBROLA).

    Arguments:
        x (MBROLA): MBROLA object to make a PHO file for.

    Raises:
        TypeError: if ``x`` is not a MBROLA object.
    Returns:
        list[str]: Lines in the PHO file.
    """
    if not isinstance(x, MBROLA):
        raise TypeError("`x` must be of type MBROLA")
    pho = [f"; {x.word}", f"_ {x.outer_silences[0]}"]
    for ph, d, p in zip(x.phon, x.durations, x.pitch):
        p_seq = " ".join([str(pi) for pi in p])
        pho.append(" ".join(map(str, [ph, d, p_seq])))
    pho.append(f"_ {x.outer_silences[1]}")
    return pho


class PlatformException(Exception):
    """Raise error platform is not Linux or Windows Subsystem for Linux.

    Args:
        Exception (Exception): A super class Exception.
    """

    def __init__(self):
        self.message = f"MBROLA only available on {platform.system()} using the Windows Subsystem for Linux (WSL).\nPlease, follow the instructions in the WSL site: https://learn.microsoft.com/en-us/windows/wsl/install."  # pylint: disable=line-too-long
        super().__init__(self.message)


@cache
def mbrola_cmd():
    """
    Get MBROLA command for system command line.
    """  # pylint: disable=line-too-long
    try:
        if is_wsl() or os.name == "posix":
            return "mbrola"
        if os.name == "nt" and wsl_available():
            return "wsl mbrola"
        raise PlatformException
    except PlatformException:
        return None


@cache
def is_wsl(version: str = platform.uname().release) -> bool:
    """Evaluate if function is running on Windows Subsystem for Linux (WSL).

    Returns:
        bool: returns ``True`` if Python is running in WSL, otherwise ``False``.
    """  # pylint: disable=line-too-long
    return version.endswith("microsoft-standard-WSL2")


@cache
def wsl_available() -> int:
    """
    Returns ``True` if Windows Subsystem for Linux (WLS) is available from Windows, otherwise ``False``
    """  # pylint: disable=line-too-long
    if os.name != "nt" or not shutil.which("wsl"):
        return False
    cmd = partial(sp.check_output, timeout=300, encoding="UTF-8", text=True)
    try:
        return is_wsl(cmd(["wsl", "uname", "-r"]).strip())
    except sp.SubprocessError:
        return False


if __name__ == "__main__":
    cafe = MBROLA(
        word="cafè",
        phon=["k", "a", "f", "f", "E1"],
        durations=100,
        pitch=[200, [200, 100, 100, 200], 200, 200, 200],
        outer_silences=(10, 10),
    )
    print(cafe)
    cafe.make_sound(Path("tests", "test.wav"))
