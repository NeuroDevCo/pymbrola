"""Util functions and wrappers for the MBROLA module."""

import os
import platform
import shutil
import subprocess as sp
import tarfile
import tempfile
from functools import cache, partial
from pathlib import Path

import requests

GITHUB_API = "https://api.github.com"
CODELOAD = "https://codeload.github.com"
RAW_BASE = "https://raw.githubusercontent.com"
REPO = "numediart/MBROLA-voices"

TIMEOUT = (10, 120)  # (connect, read) seconds


class PlatformException(Exception):
    """Raise error platform is not Linux or Windows Subsystem for Linux.

    Args:
        Exception (Exception): A super class Exception.
    """

    def __init__(self):
        self.message = f"MBROLA is only available on {platform.system()} using the Windows Subsystem for Linux (WSL).\nPlease, follow the instructions in the WSL site: https://learn.microsoft.com/en-us/windows/wsl/install."
        super().__init__(self.message)


class VoiceMissingException(Exception):
    """Fatal installer error; message is printed to stderr."""


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


def get_default_branch(repo: str) -> str:
    """Return the default branch of a GitHub repository."""
    headers = {"Accept": "application/vnd.github+json"}
    response = requests.get(
        f"{GITHUB_API}/repos/{repo}", headers=headers, timeout=TIMEOUT
    )
    if response.status_code == 404:
        raise VoiceInstallError(f"Repository '{repo}' not found.")

    response.raise_for_status()

    branch = response.json().get("default_branch")
    if not branch:
        raise VoiceInstallError(f"Error: Failed to fetch default branch for {repo}.")
    return branch


def fetch_repo_tree(repo: str, ref: str) -> dict:
    """
    Fetch the repository's full recursive tree with a single API request.

    Call this once per run and pass the result to download_single_voice()
    so that downloading N voices costs 2 API requests total (default
    branch + tree), not N + 1. api.github.com allows only 60
    unauthenticated requests per hour; raw.githubusercontent.com and
    codeload.github.com are served separately and are not subject to
    that quota.
    """
    headers = {"Accept": "application/vnd.github+json"}

    response = requests.get(
        f"{GITHUB_API}/repos/{repo}/git/trees/{ref}",
        params={"recursive": "true"},
        headers=headers,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    tree = response.json()
    if tree.get("truncated"):
        raise VoiceInstallError(
            "Repository tree is too large for one API call; clone it with git instead."
        )
    return tree


def get_data_dir(voices_src: Path, path: Path) -> bool:
    dir = Path(voices_src, "data/")

    if path.exists():
        shutil.rmtree(path)

    try:
        path.mkdir(parents=True, exist_ok=True)
        shutil.copytree(dir, path, dirs_exist_ok=True)
    except OSError as exc:
        raise VoiceInstallError("Error: Failed to install voices.") from exc

    return True


def install_voices(path: Path | None = None) -> bool:
    """
    Download and install every voice from the repository.

    Returns True if voices were installed, False if the user declined
    to replace an existing destination directory.
    """
    temp = Path(tempfile.mkdtemp(prefix="mbrola-voices-"))
    temp.mkdir(parents=True, exist_ok=True)

    if path is None:
        path = Path.home()

    path.mkdir(exist_ok=True, parents=True)

    branch = get_default_branch(REPO)

    print("Downloading all MBROLA voices...")
    archive = temp / f"voices-{branch}.tar.gz"

    url = f"{CODELOAD}/{REPO}/tar.gz/{branch}"
    try:
        with requests.get(url, stream=True, timeout=TIMEOUT) as r:
            r.raise_for_status()

            with open(archive, "wb") as fh:
                fh.writelines(r.iter_content(chunk_size=1 << 16))
    except requests.RequestException as exc:
        raise VoiceInstallError("Error: Failed to download MBROLA voices.") from exc

    # verify it is a valid gzip archive
    if not tarfile.is_tarfile(archive):
        archive.unlink(missing_ok=True)

        raise VoiceInstallError("Error: Downloaded file is not a valid gzip archive.")

    try:
        with tarfile.open(archive, "r:gz") as tar:
            try:
                # filter="data" blocks path-traversal attacks (Python >= 3.12).
                tar.extractall(temp, filter="data")
            except TypeError:  # Python < 3.12
                tar.extractall(temp)
    except tarfile.TarError as exc:
        raise VoiceInstallError(
            "Error: Failed to extract MBROLA voices archive."
        ) from exc

    # codeload tarballs have a single root folder
    repo_name = REPO.rsplit("/", 1)[-1]
    voices_src = temp / f"{repo_name.removesuffix('.git')}-{branch}"

    if not voices_src.is_dir():
        # Fallback: use the archive's single top-level directory.
        top = [p for p in temp.iterdir() if p.is_dir() and p != temp]

        if len(top) != 1:
            raise VoiceInstallError("Error: Unexpected archive layout")

        voices_src = top[0]

    get_data_dir(voices_src, path)
    shutil.rmtree(temp, ignore_errors=True)
    return True


if __name__ == "__main__":
    install_voices(path=Path("voices"))
