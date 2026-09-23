"""Util functions and wrappers for the MBROLA module."""

import os
import platform
import shutil
import subprocess as sp
from functools import cache, partial, singledispatch
from typing import TypeAlias

Number: TypeAlias = float | int
PitchElement: TypeAlias = Number | list[tuple[Number, Number]]
PitchInput: TypeAlias = Number | list[PitchElement] | list[tuple[Number, Number]]
PitchOutput: TypeAlias = list[list[tuple[float, float]]]


class PlatformException(Exception):
    """Raise error platform is not Linux or Windows Subsystem for Linux.

    Args:
        Exception (Exception): A super class Exception.
    """

    def __init__(self):
        self.message = f"MBROLA is only available on {platform.system()} using the Windows Subsystem for Linux (WSL).\nPlease, follow the instructions in the WSL site: https://learn.microsoft.com/en-us/windows/wsl/install."
        super().__init__(self.message)


@singledispatch
def _validate_durations(
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


@_validate_durations.register
def _(durations: Number, phon: str | list[str]) -> list[float]:
    return [durations] * len(phon)


@_validate_durations.register
def _(durations: list, phon: str | list[str]) -> list[float]:
    if len(durations) != len(phon):
        raise ValueError(f"`{durations}` must be the same length as {phon}")

    return list(map(float, durations))


@singledispatch
def _validate_pitch(pitch: PitchInput, phon: str | list[str]) -> PitchOutput:
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


@_validate_pitch.register
def _(pitch: Number, phon: list[str]) -> PitchOutput:
    return [[(0, pitch)]] * len(phon)


@_validate_pitch.register
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


def _validate_outer_silences(
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
        bool: returns `True` if Python is running in WSL, otherwise `False`.
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
