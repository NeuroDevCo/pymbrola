"""Util functions and wrappers for the MBROLA module."""

from functools import singledispatch, cache, partial
import os
import platform
import shutil
import subprocess as sp
import warnings

PITCH_TYPE = list[list[tuple[int, int]]]
PITCH_TYPE_INPUT = (
    int
    | int
    | list[int | float]
    | list[int | float | list[int | float | tuple[int | float, int | float]]]
)


class PlatformException(Exception):
    """Raise error platform is not Linux or Windows Subsystem for Linux.

    Args:
        Exception (Exception): A super class Exception.
    """

    def __init__(self):
        self.message = f"MBROLA is only available on {platform.system()} using the Windows Subsystem for Linux (WSL).\nPlease, follow the instructions in the WSL site: https://learn.microsoft.com/en-us/windows/wsl/install."
        super().__init__(self.message)


@singledispatch
def _validate_durations(durations: int | list[int], phon: list[str]) -> list[int]:
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


@_validate_durations.register
def _(durations: int, phon: str | list[str]) -> list[int]:
    return [durations] * len(phon)


@_validate_durations.register
def _(durations: list, phon: str | list[str]) -> list[int]:
    if len(durations) != len(phon):
        raise ValueError(f"`{durations}` must be the same length as {phon}")

    return list(map(int, durations))


@singledispatch
def _validate_pitch(pitch: PITCH_TYPE_INPUT) -> PITCH_TYPE:
    """Validate argument `pitch`.

    Args:
        pitch (int | list[int | float] | list[int | float | list[int | float | tuple[int | float, int | float]]]): pitch in Hertz (Hz). If an integer is provided, the pitch contour of each phoneme is assumed to be constant within and across phonemes (e.g., all phonemes will have a pitch of 200 Hz). If a list is provided, each element provides the pitch specification of the piecewise linear pitch curve of each phoneme. This list should have same length as `phon`. Each element in this list should be a list of an arbitrary number of tuples. Each tuple indicates the time (in percentage of the audio) at which the pitch should be modified, and the pitch value (in Hertz) that should be set.
        phon (str | Sequence[str]): string or list of phonemes.

    Raises:
        ValueError: if `pitch` is a list of different length as `phon`.
        TypeError: `pitch` is not an int or a list[tuple[float, int]]"

    Returns:
        int | list[int | float] | list[int | float | list[int | float | tuple[int | float, int | float]]]: validated pitch.

    """
    raise TypeError(f"`pitch` must be int or list, but {type(pitch)} was provided")


@_validate_pitch.register
def _(pitch: int | float, phon: list[str]) -> PITCH_TYPE:
    if isinstance(pitch, float):
        warn = "pitch values must be integers, floats have been forced to integers"
        warnings.warn(warn)

    return [[(0, int(pitch))]] * len(phon)


@_validate_pitch.register
def _(pitch: list, phon: list[str]) -> PITCH_TYPE:
    error = TypeError("All elements in `pitch` must be list[tuple[float, int]]")
    if len(pitch) != len(phon):
        raise ValueError("`pitch` must be of same length as `phon`")

    if all(isinstance(p, (int, float)) for p in pitch):
        if any(isinstance(p, float) for p in pitch):
            warn = "pitch values must be integers, floats have been forced to integers"
            warnings.warn(warn)
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


def _validate_outer_silences(outer_silences: tuple[int, int]) -> tuple[int, int]:
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


@cache
def _mbrola_cmd():
    """
    Get MBROLA command for system command line.
    """
    if _is_wsl() or os.name == "posix":
        return "mbrola"

    if os.name == "nt" and _wsl_available():
        return "wsl mbrola"

    raise PlatformException()


@cache
def _is_wsl(version: str = platform.uname().release) -> bool:
    """Evaluate if function is running on Windows Subsystem for Linux (WSL).

    Returns:
        bool: returns ``True`` if Python is running in WSL, otherwise ``False``.
    """
    return version.endswith("microsoft-standard-WSL2")


@cache
def _wsl_available() -> bool | int:
    """
    Check if Windows Subsystem for Linux (WSL is available).

    Returns:
        bool | int: ``True` if Windows Subsystem for Linux (WLS) is available from Windows, otherwise ``False``

    :meta private
    """
    if os.name != "nt" or not shutil.which("wsl"):
        return False

    cmd = partial(sp.check_output, timeout=5, encoding="UTF-8", text=True)

    try:
        return _is_wsl(cmd(["wsl", "uname", "-r"]).strip())
    except sp.SubprocessError:
        return False
