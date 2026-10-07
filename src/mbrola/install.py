"""Functions to install MBROLA and MBROLA voices."""

import argparse
import subprocess as sp
from pathlib import Path

import requests
from tqdm import tqdm

from src.mbrola.mbrola import _DOT_MBROLA, mbrola_path

# global variables
MBROLA_REPO = "numediart/MBROLA"
VOICES_REPO = "numediart/MBROLA-voices"
API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
TIMEOUT = (10, 120)  # (connect, read) seconds


# exceptions
class MBROLAInstallException(RuntimeError):
    """Error during MBROLA installation."""


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

    for name in voice:
        prefix = f"data/{name}/"
        matches = [f for f in files if f.startswith(prefix)]

        if not matches:
            raise MBROLAInstallException(f"Unknown voice {name!r}.")

        pb = tqdm(range(len(matches)))
        pb.set_description(f"Downloading {name}")

        for file in matches:
            url = f"{RAW}/{VOICES_REPO}/master/{file}"
            fn = file.split("/")  # strip leading "data/"
            download_resource(url, path / Path(*fn[1:]))
            pb.update(1)

    return True


def install_mbrola(path: Path | str | None = None) -> None:
    """Install MBROLA.

    This function downloads and compiles MBROLA from https://github.com/numediart/MBROLA.

    Args:
        path (Path | str | None, optional): Desintatino path of MBROLA installation folder. Defaults to ``~/.mbrola/``.

    Raises:
        MBROLAInstallException: If MBROLA repository cannot be reached, if download fails, or if compilation fails.

    Examples:
        >>> install_mbrola()
        >>> install_mbrola("./custom-path/")
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
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--install", action="store_true")
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        help="Path to install MBROLA at",
        default=None,
    )
    parser.add_argument(
        "-v",
        "--voice",
        type=lambda x: x.split(","),
        default=None,
        help="MBROLA voices to install",
    )
    args = parser.parse_args()

    if args.install:
        install_mbrola(args.path)

    if args.voice:
        install_voice(args.voice, path=args.path)
