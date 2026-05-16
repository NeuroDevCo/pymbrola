"""
A Python front-end to MBROLA.

References:
    Dutoit, T., Pagel, V., Pierret, N., Bataille, F., & Van der Vrecken, O. (1996, October). The MBROLA project: Towards a set of high quality speech synthesizers free of use for non commercial purposes. In Proceeding of Fourth International Conference on Spoken Language Processing. ICSLP'96 (Vol. 3, pp. 1393-1396). IEEE. https://doi.org/10.1109/ICSLP.1996.607874
"""

from pytest import CaptureFixture

from functools import singledispatch, cache, partial
import os
from pathlib import Path
import platform
import shutil
import subprocess as sp
import warnings

PITCH_TYPE = list[list[tuple[int, int]]]


@singledispatch
def validate_durations(durations: int | list[int], phon: list[str]) -> list[int]:
    """Validate argument `durations`.

    Args:
        durations (int | Sequence[int], optional): phoneme duration in milliseconds. Defaults to 100.
        phon (Sequence[str]): string or list of phonemes.

    Raises:
        ValueError: if length of durations is different than length of phon.
        TypeError: if durations is not a list or int.

    Returns:
        list[int]: Phoneme durations.
    """
    raise TypeError(
        f"`durations` must be int or list length {len(phon)}, but {type(durations)} was provided"
    )


@validate_durations.register
def _(durations: int, phon: str | list[str]) -> list[int]:
    return [durations] * len(phon)


@validate_durations.register
def _(durations: list, phon: str | list[str]) -> list[int]:
    if len(durations) != len(phon):
        raise ValueError(f"`{durations}` must be the same length as {phon}")

    return list(map(int, durations))


@singledispatch
def validate_pitch(
    pitch: int
    | int
    | list[int | float]
    | list[int | float | list[int | float | tuple[int | float, int | float]]],
    phon: list[str],
) -> PITCH_TYPE:
    """Validate argument `pitch`.

    Args:
        pitch (int | list[int | float] | list[int | float | list[int | float | tuple[int | float, int | float]]]): pitch in Hertz (Hz). If an integer is provided, the pitch contour of each phoneme is assumed to be constant within and across phonemes (e.g., all phonemes will have a pitch of 200 Hz). If a list is provided, each element provides the pitch specification of the piecewise linear pitch curve of each phoneme. This list should have same length as `phon`. Each element in this list should be a list of an arbitrary number of tuples. Each tuple indicates the time (in percentage of the audio) at which the pitch should be modified, and the pitch value (in Hertz) that should be set.
        phon (str | Sequence[str]): string or list of phonemes.

    Raises:
        TypeError: if pitch is not int or list.
        TypeError: if pitch is a list but at least one element is not list or int.
        TypeError: if pitch is a list of lists, and at least one element in at least one of the lists is not an int.
        ValueError: if pitch is a list of different length as phon.
    Returns:
        list: validated pitch.
    """
    raise TypeError(f"`pitch` must be int or list, but {type(pitch)} was provided")


@validate_pitch.register
def _(pitch: int | float, phon: list[str]) -> PITCH_TYPE:
    if isinstance(pitch, float):
        warnings.warn(
            "pitch values must be integers, floats have been forced to integers"
        )

    return [[(0, int(pitch))]] * len(phon)


@validate_pitch.register
def _(pitch: list, phon: list[str]) -> PITCH_TYPE:
    error = TypeError("All elements in `pitch` must be list[tuple[float, int]]")
    if len(pitch) != len(phon):
        raise error

    if all(isinstance(p, int) for p in pitch):
        return [[(0, p)] for p in pitch]

    if any(isinstance(p, float) for p in pitch):
        warnings.warn(
            "pitch values must be integers, floats have been forced to integers"
        )
        return [[(0, int(p))] for p in pitch]

    for i, pit in enumerate(pitch):
        if isinstance(pit, (float, int)):
            pit = [(0, pit)]
            pitch[i] = pit
        if not isinstance(pit, list):
            raise error

        if not all(isinstance(p, tuple) for p in pit if p):
            raise error

        if not all(len(p) == 2 for p in pit if p):
            raise error

        for j, (t, p) in enumerate(pit):
            if not (isinstance(t, (float, int)) and isinstance(p, (int, float))):
                raise error

            if isinstance(p, float):
                pitch[i][j] = (t, int(p))
                warnings.warn(
                    "pitch values must be integers, floats have been forced to integers"
                )
    return pitch


def validate_outer_silences(outer_silences: tuple[int, int]):
    """Validate argument `outer_silences`.

    Args:
        outer_silences (tuple[int, int]): duration in milliseconds of the silence intervals to be inserted at onset and offset. Defaults to (1, 1).

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
        phon (list[str] | tuple[int]): list of phonemes.
        durations (int | Sequence[int], optional): phoneme duration in milliseconds. Defaults to 100. If an integer is provided, all phonemes in ``phon`` are assumed to be the same length. If a list is provided, each element in the list indicates the duration of each phoneme.
        pitch (int | list[int | float] | list[int | float | list[int | float | tuple[int | float, int | float]]]): pitch in Hertz (Hz). If an integer is provided, the pitch contour of each phoneme is assumed to be constant within and across phonemes (e.g., all phonemes will have a pitch of 200 Hz). If a list is provided, each element provides the pitch specification of the piecewise linear pitch curve of each phoneme. This list should have same length as `phon`. Each element in this list should be a list of an arbitrary number of tuples. Each tuple indicates the time (in percentage of the audio) at which the pitch should be modified, and the pitch value (in Hertz) that should be set.

        outer_silences (tuple[int, int], optional): duration in milliseconds of the silence interval to be inserted at onset and offset. Defaults to (1, 1).

    Attributes:
        phon (list[str]): list of phonemes.
        durations (list[int] | int, optional): phoneme duration in milliseconds. Defaults to 100. If an integer is provided, all phonemes in ``phon`` are assumed to be the same length. If a list is provided, each element in the list indicates the duration of each phoneme.
        pitch (int | list[int | float] | list[int | float | list[int | float | tuple[int | float, int | float]]]): pitch in Hertz (Hz). If an integer is provided, the pitch contour of each phoneme is assumed to be constant within and across phonemes (e.g., all phonemes will have a pitch of 200 Hz). If a list is provided, each element provides the pitch specification of the piecewise linear pitch curve of each phoneme. This list should have same length as `phon`. Each element in this list should be a list of an arbitrary number of tuples. Each tuple indicates the time (in percentage of the audio) at which the pitch should be modified, and the pitch value (in Hertz) that should be set.
        outer_silences (Sequence[int, int], optional): duration in milliseconds of the silence interval to be inserted at onset and offset. Defaults to (1, 1).
    Examples:
        >>> house = mb.MBROLA(
                phonemes = ["h", "a", "U", "s"],
                durations = 100,
                pitch = 200
            )
    """

    def __init__(
        self,
        phon: str | list[str],
        durations: int | list[int] = 100,
        pitch: int
        | list[int | float]
        | list[int | float | list[int | float | tuple[int | float, int | float]]] = 200,
        outer_silences: tuple[int, int] = (1, 1),
    ):
        if isinstance(phon, str):
            phon = [phon]

        self.phon = list(map(str, phon))
        self.durations = validate_durations(durations, phon)
        self.pitch = validate_pitch(pitch, self.phon)
        self.outer_silences = validate_outer_silences(outer_silences)
        self.pho = make_pho(self)

    def __len__(self):
        return len(self.phon)

    def __eq__(self, other):
        return self.pho == other.pho

    def __add__(self, other, sep="_"):
        self.phon = self.phon + other.phon
        self.pho = self.pho + other

    def export_pho(self, file: str | Path) -> None:
        """Save PHO file.

        Args:
            file (str): Path of the output PHO file.
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
    ):
        """Generate MBROLA sound WAV file.

        Args:
            file (str): Path to the output WAV file.
            voice (str, optional): MBROLA voice to use. Defaults to "it4". Note phoneme symbols may be specific to voices.
            f0_ratio (float, optional): Constant to multiply the fundamental frequency of the whole sound by. Defaults to 1.0 (same fundamental frequency).
            dur_ratio (float, optional): Constant to multiply the duration of the whole sound by. Defaults to 1.0 (same duration).
            remove_pho (bool, optional): Should the intermediate PHO file be deleted after the sound is created? Defaults to True.
        """
        pho = Path("tmp.pho")

        with Path(pho).open(mode="w", encoding="utf-8") as f:
            f.write("\n".join(self.pho))

        cmd_str = f"{mbrola_cmd()} -f {f0_ratio} -t {dur_ratio} /usr/share/mbrola/{voice}/{voice} {pho} {str(Path(file))}"

        try:
            sp.check_output(cmd_str, shell=True)
        except sp.CalledProcessError as e:
            print(f"Error when making sound for {file}: {e}")

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


class PlatformException(Exception):
    """Raise error platform is not Linux or Windows Subsystem for Linux.

    Args:
        Exception (Exception): A super class Exception.
    """

    def __init__(self):
        self.message = f"MBROLA is only available on {platform.system()} using the Windows Subsystem for Linux (WSL).\nPlease, follow the instructions in the WSL site: https://learn.microsoft.com/en-us/windows/wsl/install."
        super().__init__(self.message)


@cache
def mbrola_cmd():
    """
    Get MBROLA command for system command line.
    """
    try:
        if is_wsl() or os.name == "posix":
            return "mbrola"

        if os.name == "nt" and wsl_available():
            return "wsl mbrola"

        raise PlatformException()

    except PlatformException:
        return None


@cache
def is_wsl(version: str = platform.uname().release) -> bool:
    """Evaluate if function is running on Windows Subsystem for Linux (WSL).

    Returns:
        bool: returns ``True`` if Python is running in WSL, otherwise ``False``.
    """
    return version.endswith("microsoft-standard-WSL2")


@cache
def wsl_available() -> bool | int:
    """
    Check if Windows Subsystem for Linux (WSL is available).

    Returns:
        bool | int: ``True` if Windows Subsystem for Linux (WLS) is available from Windows, otherwise ``False``
    """
    if os.name != "nt" or not shutil.which("wsl"):
        return False

    cmd = partial(sp.check_output, timeout=5, encoding="UTF-8", text=True)

    try:
        return is_wsl(cmd(["wsl", "uname", "-r"]).strip())
    except sp.SubprocessError:
        return False


if __name__ == "__main__":
    cafe = MBROLA(
        phon=["k", "a", "f", "f", "E1"],
        durations=[200, 300, 200, 200, 200],
        pitch=[200, [(50, 400)], [(30, 200)], [], []],
        outer_silences=(10, 10),
    )

    cafe.export_pho("test.pho")
    print(cafe)
