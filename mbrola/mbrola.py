"""
A Python front-end to MBROLA.

References:
    Dutoit, T., Pagel, V., Pierret, N., Bataille, F., & Van der Vrecken, O. (1996, October). The MBROLA project: Towards a set of high quality speech synthesizers free of use for non commercial purposes. In Proceeding of Fourth International Conference on Spoken Language Processing. ICSLP'96 (Vol. 3, pp. 1393-1396). IEEE. https://doi.org/10.1109/ICSLP.1996.607874
"""  # pylint: disable=line-too-long

import os
import subprocess as sp
from mbrola import utils


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
        outer_silences (tuple, optional): duration in milliseconds of the silence intervals to be inserted at onset and offset. Defaults to (1, 1).

    Attributes:
        word (str): label for the mbrola sound.
        phon (list[str]): list of phonemes.
        durations (list[int] | int, optional): phoneme duration in milliseconds. Defaults to 100.
        If an integer is provided, all phonemes in ``phon`` are assumed to be the same length. If a list is provided, each element in the list indicates the duration of each phoneme.
        pitch (list[int] | int, optional): pitch in Hertz (Hz). Defaults to 200.
        If an integer is provided, the pitch contour of each phoneme is assumed to be constant at the indicated value. If a list of integers or strings is provided, each element in the list indicates the value at which the pitch contour of each phoneme is kept constant. If a list of lists (of integers or strings), each value in each element describes the pitch contour for each phoneme.
        outer_silences (int, optional): duration in milliseconds of the silence interval to be inserted at onset and offset. Defaults to (1, 1).
    Examples:
        >>> house = mb.MBROLA(
                word = "house",
                phonemes = ["h", "a", "U", "s"],
                durations = "100",
                pitch = 200
            )
    Raises:
        ValueError: ``word`` must be a string
        ValueError: ``phon`` must be a list of strings
        ValueError: ``durations`` must be a list of integers or an integer
        ValueError: ``phon`` and ``durations`` must have the same length
        ValueError: ``pitch`` must be a list of integers or an integer
        ValueError: ``phon`` and ``pitch`` must have the same length
        ValueError: ``outer_silences`` must be a tuple of positive integers of length 2
    """  # pylint: disable=line-too-long

    def __init__(
        self,
        word: str,
        phon: list[str],
        durations: list[int] | int = 100,
        pitch: list[int] | int = 200,
        outer_silences: int = (1, 1),
    ):
        self.word = word
        self.phon = phon
        self.durations = durations
        self.pitch = pitch
        self.outer_silences = outer_silences

        nphon = len(self.phon)

        if isinstance(self.durations, int):
            self.durations = [self.durations] * nphon
        self.durations = list(map(str, self.durations))
        if isinstance(self.pitch, int):
            self.pitch = [[self.pitch, self.pitch]] * nphon
        if isinstance(self.pitch[0], int):
            self.pitch = [list(map(str, [p, p])) for p in self.pitch]
        self.pitch = [list(map(str, p)) for p in self.pitch]

        utils.validate_mbrola_args(self)

        self.pho = make_pho(self)

    def __str__(self):
        return str("\n".join(self.pho))

    def __repr__(self):
        return str("\n".join(self.pho))

    def export_pho(self, file: str) -> None:
        """Save PHO file.

        Args:
            file (str): Path of the output PHO file.
        """
        try:
            with open(f"{file}", "w+", encoding="utf-8") as f:
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
        """Generate MBROLA sound WAV file.

        Args:
            file (str): Path to the output WAV file.
            voice (str, optional): MBROLA voice to use. Defaults to "it4". Note phoneme symbols may be specific to voices.
            f0_ratio (float, optional): Constant to multiply the fundamental frequency of the whole sound by. Defaults to 1.0 (same fundamental frequency).
            dur_ratio (float, optional): Constant to multiply the duration of the whole sound by. Defaults to 1.0 (same duration).
            remove_pho (bool, optional): Should the intermediate PHO file be deleted after the sound is created? Defaults to True.
        """
        with open("tmp.pho", mode="w", encoding="utf-8") as f:
            f.write("\n".join(self.pho))

        cmd = f"{utils.mbrola_cmd()} -f {f0_ratio} -t {dur_ratio} /usr/share/mbrola/{voice}/{voice} tmp.pho {file}"

        try:
            sp.check_output(cmd)
        except sp.CalledProcessError:
            print(f"Error when making sound for {file}")
        f.close()
        if remove_pho:
            os.remove("tmp.pho")


def make_pho(self) -> list[str]:
    """Generate PHO file.

    A PHO (.pho) file contains the phonological information of the speech sound in a format that MBROLA can read. See more examples in the MBROLA documentation (https://github.com/numediart/MBROLA).

    Returns:
        list[str]: Lines in the PHO file.
    """
    pho = [f"; {self.word}", f"_ {self.outer_silences[0]}"]
    for ph, d, p in zip(self.phon, self.durations, self.pitch):
        p_seq = " ".join(p)
        pho.append(" ".join([ph, d, p_seq]))
    pho.append(f"_ {self.outer_silences[1]}")
    return pho


if __name__ == "__main__":
    house = MBROLA(word="house", phon=["h", "a", "U", "s"], durations="100", pitch=200)
