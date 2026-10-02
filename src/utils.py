"""Util functions and wrappers for the MBROLA module."""

import os
import platform
import shutil
import subprocess as sp
from functools import cache, partial
from pathlib import Path

import requests
from tqdm import tqdm

_DOT_MBROLA = ".mbrola"
MBROLA_REPO = "numediart/MBROLA"
VOICES_REPO = "numediart/MBROLA-voices"
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


class VoiceInstallException(RuntimeError):
    """Unrecoverable error; mirrors `exit 1` in the original bash script."""


class MBROLAInstallException(RuntimeError):
    """Unrecoverable error; mirrors `exit 1` in the original bash script."""


class MissingMBROLAException(RuntimeError):
    "Could not find mbrola file in specified location."


class MissingVoiceException(Exception):
    """Voice not found in voices folder."""


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


def check_voice(voice: str) -> str:
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
        msg = f"Voice '{voice}' not found in `voices_path` '{voices_path}'. Please, install MBROLA voices using `utils.install_voices({voice})` or use the `voices_path` argument to point to the folder that contains installed MBROLA voices."
        raise MissingVoiceException(msg)

    return str(voices_path / voice / voice)


@cache
def _mbrola_cmd() -> str:
    """
    Get MBROLA command for system command line.

    Returns:
        str: Validated path to MBROLA file.
    """
    mbrola_file = mbrola_path() / "Bin/mbrola"
    if _is_wsl() or os.name == "posix":
        return str(mbrola_file)

    if os.name == "nt" and _wsl_available():
        return "wsl " + str(mbrola_path / mbrola_file)

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
        bool | int: `True` if Windows Subsystem for Linux (WLS) is available from Windows, otherwise `False`

    :meta private:
    """
    if os.name != "nt" or not shutil.which("wsl"):
        return False

    cmd = partial(sp.check_output, timeout=5, encoding="UTF-8", text=True)

    try:
        return _is_wsl(cmd(["wsl", "uname", "-r"]).strip())
    except sp.SubprocessError:
        return False


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
    try:
        r = requests.get(
            f"{API}/repos/{VOICES_REPO}/git/trees/master",
            params={"recursive": "1"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        tree = r.json()
        if tree.get("truncated"):
            raise VoiceInstallException("Error: repository tree too large to list.")
        files = {e["path"]: e["size"] for e in tree["tree"] if e["type"] == "blob"}
    except requests.RequestException as exc:
        raise VoiceInstallException("Error: Failed to list MBROLA voices.") from exc

    if not voice:
        voice = sorted({f.split("/")[1] for f in files if "/" in f})

    for v in voice:  # guard against path traversal in user input
        if not v or "/" in v or v in (".", ".."):
            raise VoiceInstallException(f"Error: invalid voice name {v!r}.")

    wanted: dict[str, int] = {}
    for name in voice:
        prefix = f"data/{name}/"
        matches = {p: s for p, s in files.items() if p.startswith(prefix)}

        if not matches:
            raise VoiceInstallException(f"Error: unknown voice {name!r}.")

        wanted.update(matches)

    pb_settings = {"desc": "Downloading", "smoothing": True, "leave": False}
    pb = tqdm(range(len(wanted)), **pb_settings)

    for rel_path in wanted:
        # strips the leading "data/" so voices land directly in `path`
        dest = path / Path(*rel_path.split("/")[1:])
        dest.parent.mkdir(parents=True, exist_ok=True)
        url = f"{RAW}/{VOICES_REPO}/master/{rel_path}"

        try:
            with requests.get(url, stream=True, timeout=TIMEOUT) as r:
                r.raise_for_status()

                with open(dest, "wb") as fh:
                    fh.writelines(c for c in r.iter_content(chunk_size=1 << 16))
        except requests.RequestException as exc:
            raise VoiceInstallException(
                f"Error: failed to download {rel_path}."
            ) from exc
        except OSError as exc:
            raise VoiceInstallException("Error: Failed to install voices.") from exc

        pb.update(1)
        pb.set_description(f"Downloading {rel_path.split('/')[1]}")

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

    r = requests.get(
        f"{API}/repos/{MBROLA_REPO}/git/trees/master",
        params={"recursive": "1"},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    tree = r.json()

    if tree.get("truncated"):
        raise MBROLAInstallException("Error: repository tree too large to list.")

    files = {e["path"]: e["size"] for e in tree["tree"] if e["type"] == "blob"}

    pb_settings = {"desc": "Downloading MBROLA", "smoothing": True, "leave": False}
    pb = tqdm(range(len(files)), **pb_settings)

    for rel_path in files:
        # strips the leading "data/" so voices land directly in `path`
        dest = path / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        url = f"{RAW}/{MBROLA_REPO}/master/{rel_path}"

        try:
            with requests.get(url, stream=True, timeout=TIMEOUT) as r:
                r.raise_for_status()

                with open(dest, "wb") as fh:
                    fh.writelines(c for c in r.iter_content(chunk_size=1 << 16))
        except requests.RequestException as e:
            raise MBROLAInstallException(f"Error: failed to download {rel_path}") from e
        except OSError as e:
            raise MBROLAInstallException("Error: Failed to download MBROLA") from e

        pb.update(1)

    pb.set_description("Compiling MBROLA")

    try:
        sp.run(["make"], cwd=path, capture_output=True, text=True, check=True)
    except OSError as e:
        raise MBROLAInstallException("Error: Failed to compile MBROLA") from e


if __name__ == "__main__":
    # install_mbrola()
    install_voice(voice=["it4", "fr4"])
