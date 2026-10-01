"""Util functions and wrappers for the MBROLA module."""

import os
import platform
import shutil
import subprocess as sp
from functools import cache, partial
from pathlib import Path

import requests
from tqdm import tqdm

REPO = "numediart/MBROLA-voices"
API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"

TIMEOUT = (10, 120)  # (connect, read) seconds


class PlatformException(Exception):
    """Raise error platform is not Linux or Windows Subsystem for Linux.

    Args:
        Exception (Exception): A super class Exception.
    """

    def __init__(self):
        self.message = f"MBROLA is only available on {platform.system()} using the Windows Subsystem for Linux (WSL).\nPlease, follow the instructions in the WSL site: https://learn.microsoft.com/en-us/windows/wsl/install."
        super().__init__(self.message)


class VoiceInstallError(RuntimeError):
    """Unrecoverable error; mirrors `exit 1` in the original bash script."""


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

    :meta private:
    """
    if os.name != "nt" or not shutil.which("wsl"):
        return False

    cmd = partial(sp.check_output, timeout=5, encoding="UTF-8", text=True)

    try:
        return _is_wsl(cmd(["wsl", "uname", "-r"]).strip())
    except sp.SubprocessError:
        return False


def install_voices(voices: list[str] | None = None, path: Path | None = None) -> bool:
    """
    Download and install MBROLA voices from numediart/MBROLA-voices.

    voices (list[str] | None, optional): Voice names to install, e.g. ["es1", "de1"]. If None (default) or empty, installs every voice.
    path (Path | None, optional): Destination folder for MBROLA voices. Defaults to ~/.mbrola/voices.

    Returns:
        bool: True if voices were installed, False if the user declined to
        replace an existing destination directory.

    Examples:
        >>> install_voices(["it4", "us1"]) # installs selected voices
        >>> install_voices() # installs all available voices
        >>> install_voices(path = Path("sounds")) # installs voices in folder "sounds"

    """
    if path is None:
        path = Path.home() / ".mbrola" / "voices"

    Path(path).mkdir(exist_ok=True, parents=True)
    try:
        r = requests.get(
            f"{API}/repos/{REPO}/git/trees/master",
            params={"recursive": "1"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        tree = r.json()
        if tree.get("truncated"):
            raise VoiceInstallError("Error: repository tree too large to list.")
        files = {e["path"]: e["size"] for e in tree["tree"] if e["type"] == "blob"}
    except requests.RequestException as exc:
        raise VoiceInstallError("Error: Failed to list MBROLA voices.") from exc

    if not voices:
        voices = sorted({f.split("/")[1] for f in files if "/" in f})

    for v in voices:  # guard against path traversal in user input
        if not v or "/" in v or v in (".", ".."):
            raise VoiceInstallError(f"Error: invalid voice name {v!r}.")

    wanted: dict[str, int] = {}
    for name in voices:
        prefix = f"data/{name}/"
        matches = {p: s for p, s in files.items() if p.startswith(prefix)}

        if not matches:
            raise VoiceInstallError(f"Error: unknown voice {name!r}.")

        wanted.update(matches)

    pb_settings = {
        "desc": "Downloading",
        "smoothing": True,
        "leave": False,
    }
    pb = tqdm(range(len(wanted)), **pb_settings)
    for rel_path in wanted:
        # strips the leading "data/" so voices land directly in `path`
        dest = path / Path(*rel_path.split("/")[1:])
        dest.parent.mkdir(parents=True, exist_ok=True)
        url = f"{RAW}/{REPO}/master/{rel_path}"

        try:
            with requests.get(url, stream=True, timeout=TIMEOUT) as r:
                r.raise_for_status()
                with open(dest, "wb") as fh:
                    fh.writelines(c for c in r.iter_content(chunk_size=1 << 16))
        except requests.RequestException as exc:
            raise VoiceInstallError(f"Error: failed to download {rel_path}.") from exc
        except OSError as exc:
            raise VoiceInstallError("Error: Failed to install voices.") from exc

        pb.update(1)
        pb.set_description(f"Downloading {rel_path.split('/')[1]}")

    return True


if __name__ == "__main__":
    install_voices(voices=["en1", "fr4", "es3", "us1"], path=Path("voices"))
