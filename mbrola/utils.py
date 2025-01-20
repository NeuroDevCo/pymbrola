"""
Util functions for the MBROLA class.
"""

import os
import platform
import shutil
import functools
import subprocess as sp


class PlatformException(Exception):
    """Raise error platform is not Linux or Windows Subsystem for Linux.

    Args:
        Exception (Exception): A super class Exception.
    """

    def __init__(self):
        self.message = f"MBROLA only available on {platform.system()} using the Windows Subsystem for Linux (WSL).\nPlease, follow the instructions in the WSL site: https://learn.microsoft.com/en-us/windows/wsl/install."  # pylint: disable=line-too-long
        super().__init__(self.message)


def validate_mbrola_args(self) -> None:
    """Validate MBROLA arguments.

    Raises:
        ValueError: ``phon`` and ``durations`` must have the same length.
        ValueError: ``phon`` and ``pitch`` must have the same length.
        ValueError: ``outer_silences`` must be a tuple of length 2.
        ValueError: ``outer_silences`` must be a positive integer.
    """
    nphon = len(self.phon)
    if isinstance(self.durations, list) and len(self.durations) != nphon:
        raise ValueError("`phon` and `durations` must have the same length")
    if isinstance(self.pitch, list):
        if len(self.pitch) != nphon:
            raise ValueError("`phon` and `pitch` must have the same length")
    if len(self.outer_silences) != 2:
        raise ValueError("`outer_silences` must be a tuple of length 2")
    if self.outer_silences[0] <= 0:
        raise ValueError("`outer_silences` must be a tuple of positive integers")
    if self.outer_silences[1] <= 0:
        raise ValueError("`outer_silences` must be a tuple positive integers")


@functools.cache
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


@functools.cache
def is_wsl(version: str = platform.uname().release) -> int:
    """
    Returns ```True`` if Python is running in WSL, otherwise ```False``
    """  # pylint: disable=line-too-long
    return version.endswith("microsoft-standard-WSL2")


@functools.cache
def wsl_available() -> int:
    """
    Returns ``True` if Windows Subsystem for Linux (WLS) is available from Windows, otherwise ``False``
    """  # pylint: disable=line-too-long
    if os.name != "nt" or not shutil.which("wsl"):
        return False
    try:
        return is_wsl(
            sp.check_output(["wsl", "uname", "-r"], text=True, timeout=15).strip()
        )
    except sp.SubprocessError:
        return False
