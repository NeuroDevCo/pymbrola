import os
import platform
import shutil
import functools
import subprocess as sp


def validate_mbrola_args(self) -> None:
    nphon = len(self.phon)
    if isinstance(self.durations, list) and len(self.durations) != nphon:
        raise ValueError("`phon` and `durations` must have the same length")
    if isinstance(self.pitch, list):
        if len(self.pitch) != nphon:
            raise ValueError("`phon` and `pitch` must have the same length")
    if self.onset_silence <= 0:
        raise ValueError("`onset_silence` must be a positive integer")
    if self.offset_silence <= 0:
        raise ValueError("`offset_silence` must be a positive integer")
    return None


@functools.cache
def mbrola_cmd():
    """
    Get MBROLA command for system command line.
    """
    try:
        if is_wsl() or os.name == "posix":
            return "mbrola"
        if os.name == "nt":
            if wsl_available():
                return "wsl mbrola"
            else:
                raise Exception(
                    f"MBROLA only available on {platform.system()} using the Windows Subsystem for Linux (WSL). Please, follow the instructions in the WSL site: https://learn.microsoft.com/en-us/windows/wsl/install."
                )
    except:
        raise Exception(f"MBROLA not available for {platform.system()}")


@functools.cache
def is_wsl(version: str = platform.uname().release) -> int:
    """
    Returns ```True`` if Python is running in WSL, otherwise ```False``
    """
    return version.endswith("microsoft-standard-WSL2")


@functools.cache
def wsl_available() -> int:
    """
    Returns ```True`` if Windows Subsystem for Linux (WLS) is available from Windows, otherwise ```False``
    """
    if os.name != "nt" or not shutil.which("wsl"):
        return False
    try:
        return is_wsl(
            sp.check_output(["wsl", "uname", "-r"], text=True, timeout=15).strip()
        )
    except sp.SubprocessError:
        return False
