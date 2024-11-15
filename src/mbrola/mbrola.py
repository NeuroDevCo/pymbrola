import os
import subprocess as sp
import platform
import shutil
import functools


class MBROLA:
    """A class for generating MBROLA sounds.

    An MBROLA class contains the necessary elements to synthesise an audio using MBROLA.

    Args:
        word (str): label for the mbrola sound.
        phon (list[str]): list of phonemes.
        durations (list[int] | int, optional): phoneme duration in milliseconds. Defaults to 100.
        If an integer is provided, all phonemes in ``phon`` are assumed to be the same length. If a list is provided, each element in the list indicates the duration of each phoneme.
        pitch (list[int] | int, optional): pitch in Hertz (Hz). Defaults to 200.
        If an integer is provided, the pitch contour of each phoneme is assumed to be constant at the indicated value. If a list of integers or strings is provided, each element in the list indicates the value at which the pitch contour of each phoneme is kept constant. If a list of lists (of integers or strings), each value in each element describes the pitch contour for each phoneme.
        onset_silence (int, optional): duration in milliseconds of the silence interval to be inserted at onset. Defaults to 1.
        offset_silence (int, optional): duration in milliseconds of the silence interval to be inserted at offset. Defaults to 1.

    Attributes:
        word (str): label for the mbrola sound.
        phon (list[str]): list of phonemes.
        durations (list[int] | int, optional): phoneme duration in milliseconds. Defaults to 100.
        If an integer is provided, all phonemes in ``phon`` are assumed to be the same length. If a list is provided, each element in the list indicates the duration of each phoneme.
        pitch (list[int] | int, optional): pitch in Hertz (Hz). Defaults to 200.
        If an integer is provided, the pitch contour of each phoneme is assumed to be constant at the indicated value. If a list of integers or strings is provided, each element in the list indicates the value at which the pitch contour of each phoneme is kept constant. If a list of lists (of integers or strings), each value in each element describes the pitch contour for each phoneme.
        onset_silence (int, optional): duration in milliseconds of the silence interval to be inserted at onset. Defaults to 1.
        offset_silence (int, optional): duration in milliseconds of the silence interval to be inserted at offset. Defaults to 1.

    Raises:
        ValueError: ``word`` must be a string
        ValueError: ``phon`` must be a list of strings
        ValueError: ``durations`` must be a list of integers or an integer
        ValueError: ``phon`` and ``durations`` must have the same length
        ValueError: ``pitch`` must be a list of integers or an integer
        ValueError: ``phon`` and ``pitch`` must have the same length
        ValueError: ``onset_silence`` must be an integer
        ValueError: ``offset_silence`` must be an integer
    """

    def __init__(
        self,
        word: str,
        phon: list[str],
        durations: list[int] | int = 100,
        pitch: list[int] | int = 200,
        onset_silence: int = 1,
        offset_silence: int = 1,
    ):
        self.word = word
        self.phon = phon
        self.durations = durations
        self.pitch = pitch
        self.onset_silence = onset_silence
        self.offset_silence = offset_silence

        nphon = len(self.phon)

        if isinstance(self.durations, int):
            self.durations = [self.durations] * nphon
        self.durations = list(map(str, self.durations))
        if isinstance(self.pitch, int):
            self.pitch = [[self.pitch, self.pitch]] * nphon
        if isinstance(self.pitch[0], int):
            self.pitch = [list(map(str, [p, p])) for p in self.pitch]
        self.pitch = [list(map(str, p)) for p in self.pitch]

        validate_mbrola_args(self)

        self.pho = make_pho(self)

    def __str__(self):
        return str("\n".join(self.pho))

    def __repr__(self):
        return str("\n".join(self.pho))

    def export_pho(self, file: str):
        try:
            with open(f"{file}", "w+") as f:
                f.write("\n".join(self.pho))
        except FileNotFoundError:
            print(f"{file} is not a valid path")

    def make_sound(
        self,
        file: str,
        voice: str = "it4",
        f0_ratio: float = 1.0,
        dur_ratio: float = 1.0,
        remove_pho: bool = True,
    ):
        with open("tmp.pho", mode="w") as f:
            f.write("\n".join(self.pho))

        cmd = f"{mbrola_cmd()} -f {f0_ratio} -t {dur_ratio} /usr/share/mbrola/{voice}/{voice} tmp.pho {file}"

        try:
            sp.check_output(cmd)
        except sp.CalledProcessError as e:
            print(f"Error when making sound for {file}")
        f.close()
        if remove_pho:
            os.remove("tmp.pho")
        return None


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


def make_pho(self) -> list[str]:
    pho = [f"; {self.word}", f"_ {self.onset_silence}"]
    for ph, d, p in zip(self.phon, self.durations, self.pitch):
        p_seq = " ".join(p)
        pho.append(" ".join([ph, d, p_seq]))
    pho.append(f"_ {self.offset_silence}")
    return pho


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
