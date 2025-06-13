"""Functions for installing MBROLA."""

import os
import functools
import platform
import subprocess as sp


def install_mbrola():
    """Install MBROLA.

    Raises:
        GitMissingError: if git is not installed.
        MakeMissingError: if gcc is not installed.

    Returns:
        bool: if installation is successful.
    """
    if not is_git_installed():
        raise GitMissingError("git must be installed, please run `apt-get install git`")
    if not is_gcc_installed():
        raise MakeMissingError(
            "gcc must be installed, please run `apt-get install buil-essential`"
        )
    mbrola_download()
    mbrola_compile()
    mbrola_download_voices()


def cmd(x: str, timeout: int = 300, encoding: str = "UTF-8", **kwargs):
    """Run command using subprocess.

    Args:
        x (str): command to run.
        timeout (int, optional): timeout upper limit in seconds. Defaults to 15.
        encoding (str, optional): output encoding. Defaults to "UTF-8".

    Returns:
        any: whatever output the subprocess generates.
    """
    return sp.check_output(x, timeout=timeout, encoding=encoding, **kwargs)


@functools.cache
def is_wsl(version: str = platform.uname().release) -> int:
    """
    Returns ```True`` if Python is running in WSL, otherwise ```False``
    """  # pylint: disable=line-too-long
    return version.endswith("microsoft-standard-WSL2")


class GitMissingError(Exception):
    """If git is not installed."""


class MakeMissingError(Exception):
    """If make is not installed."""


class InstallError(Exception):
    """If error is encountered during installation."""


def add_wsl_prefix(x: dict) -> dict:
    """Add `wls` prefix to commands if using Windows Subsystem for Linux (WSL).

    Args:
        x (dict): Commands to add prefix to, if necessary.

    Returns:
        dict: Commands with prefix added, if necessary.
    """
    if os.name == "nt" and is_wsl():
        return {k: ["wsl"] + v for k, v in x.items()}
    return x


def is_gcc_installed():
    """Check if gcc is installed.

    Returns:
        str or bool: gcc version number if True, False otherwise.
    """  # pylint: disable=line-too-long
    x = add_wsl_prefix({"version": ["gcc", "--version"]})
    try:
        version = cmd(x["version"])
        return version.strip()
    except (sp.SubprocessError, FileNotFoundError):
        return False


def is_git_installed():
    """Check if Git is installed.

    Returns:
        str or bool: git version number if True, False otherwise.
    """  # pylint: disable=line-too-long
    x = add_wsl_prefix({"version": ["git", "--version"]})
    try:
        version = cmd(x["version"])
        return version.strip()
    except (sp.SubprocessError, FileNotFoundError):
        return False


def mbrola_download(url: str = "https://github.com/numediart/MBROLA.git") -> bool:
    """Download and install MBROLA.

    Args:
        url (str, optional): URL to clone MBROLA from. Defaults to "https://github.com/numediart/MBROLA.git".

    Raises:
        InstallError: if an error is encountered during installation.

    Returns:
        bool: True if successful installation.
    """  # pylint: disable=line-too-long
    x = add_wsl_prefix(
        {
            "install": ["apt-get", "install", "mbrola", "-y"],
            "pull": ["git", "pull"],
            "clone": ["git", "clone", url, "/home/MBROLA"],
        }
    )
    try:
        cmd(x["install"])
        mbdir = os.path.join("/home", "MBROLA")
        if os.path.exists(mbdir):
            cmd(x["pull"], cwd=mbdir)
        else:
            cmd(x["clone"], cwd="/home")
    except sp.SubprocessError as e:
        raise InstallError("Error during MBROLA downloading: " + str(e)) from e


def mbrola_compile():
    """Compile MBROLA.

    Raises:
        InstallError: if error is encountered during compilation.

    Returns:
        bool: True if compilation is successful.
    """
    x = add_wsl_prefix(
        {
            "make": ["make"],
            "copy": ["cp", "mbrola", "/usr/bin/mbrola"],
        }
    )
    path = os.path.join("/home/MBROLA/")
    try:
        cmd(x["make"], cwd=path)
        cmd(x["copy"], cwd=os.path.join(path, "Bin"))
    except sp.SubprocessError as e:
        raise InstallError("Error during MBROLA compilation: " + str(e)) from e


def mbrola_download_voices(url: str = "https://github.com/numediart/MBROLA-voices.git"):
    """Download MBROLA voices.

    Args:
        url (str, optional): URL to download MBROLA voices from. Defaults to "https://github.com/numediart/MBROLA-voices.git".

    Raises:
        InstallError: If an error is encountered.
    """  # pylint: disable=line-too-long
    path = os.path.join("/home", "MBROLA-voices")
    x = add_wsl_prefix(
        {
            "clone": ["git", "clone", url, path],
            "copy": ["cp", "-r", "data/.", "/usr/share/mbrola/"],
        }
    )
    try:
        cmd(x["clone"])
        cmd(x["copy"], cwd=path)
    except sp.SubprocessError as e:
        raise InstallError("Error during MBROLA voices downloading: " + str(e)) from e


if __name__ == "__main__":
    install_mbrola()
