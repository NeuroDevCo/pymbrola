"""
A Python front-end to MBROLA.

References:
    Dutoit, T., Pagel, V., Pierret, N., Bataille, F., & Van der Vrecken, O. (1996, October). The MBROLA project: Towards a set of high quality speech synthesizers free of use for non commercial purposes. In Proceeding of Fourth International Conference on Spoken Language Processing. ICSLP'96 (Vol. 3, pp. 1393-1396). IEEE. https://doi.org/10.1109/ICSLP.1996.607874
"""

from copy import deepcopy
from pathlib import Path
import subprocess as sp

from src import utils


class MBROLA:
    """A class for generating MBROLA sounds.

    An MBROLA class contains the necessary elements to synthesise an audio using MBROLA.

    Args:
        phon (list[str] | tuple[int]): list of phonemes.
        durations (int | Sequence[int], optional): phoneme duration in milliseconds. Defaults to 100. If an integer is provided, all phonemes in ``phon`` are assumed to be the same length. If a list is provided, each element in the list indicates the duration of each phoneme.
        pitch (int | list[int | float] | list[int | float | list[int | float | tuple[int | float, int | float]]]): pitch in Hertz (Hz). If an integer is provided, the pitch contour of each phoneme is assumed to be constant within and across phonemes (e.g., all phonemes will have a pitch of 200 Hz). If a list is provided, each element provides the pitch specification of the piecewise linear pitch curve of each phoneme. This list should have same length as `phon`. Each element in this list should be a list of an arbitrary number of tuples. Each tuple indicates the time (in percentage of the audio) at which the pitch should be modified, and the pitch value (in Hertz) that should be set.

        outer_silences (tuple[int, int], optional): duration in milliseconds of the silence interval to be inserted at onset and offset. Defaults to (1, 1).

    Attributes:
        phon (list[str]): list of phonemes.
        durations (list[int] | int, optional): phoneme duration in milliseconds. Defaults to 100. If an integer is provided, all phonemes in ``phon`` are assumed to be the same length. If a list is provided, each element in the list indicates the duration of each phoneme.
        pitch (int | list[int | float] | list[int | float | list[int | float | tuple[int | float, int | float]]]): pitch in Hertz (Hz). If an integer is provided, the pitch contour of each phoneme is assumed to be constant within and across phonemes (e.g., all phonemes will have a pitch of 200 Hz). If a list is provided, each element provides the pitch specification of the piecewise linear pitch curve of each phoneme. This list should have same length as `phon`. Each element in this list should be a list of an arbitrary number of tuples. Each tuple indicates the time (in percentage of the audio) at which the pitch should be modified, and the pitch value (in Hertz) that should be set.
        outer_silences (Sequence[int, int], optional): duration in milliseconds of the silence interval to be inserted at onset and offset. Defaults to (1, 1).

    Examples:
        >>> house = mb.MBROLA(
                phonemes = ["h", "a", "U", "s"],
                durations = 100,
                pitch = 200
            )
    """

    def __init__(
        self,
        phon: str | list[str],
        durations: int | list[int] = 100,
        pitch: utils.PITCH_TYPE_INPUT = 200,
        outer_silences: tuple[int, int] = (1, 1),
    ):
        if isinstance(phon, str):
            if len(phon) > 1:
                phon = list(phon)
            else:
                phon = [phon]

        self.phon = list(map(str, phon))
        self.durations = utils._validate_durations(durations, phon)
        self.pitch = utils._validate_pitch(pitch, self.phon)
        self.outer_silences = utils._validate_outer_silences(outer_silences)
        self.pho = _make_pho(self)

    def __len__(self):
        return len(self.phon)

    def __eq__(self, other):
        return self.pho == other.pho

    def __add__(self, other):
        new = self.copy()
        new.phon = self.phon + other.phon
        new.pho = self.pho + other.pho
        return new

    def copy(self):
        return deepcopy(self)

    def export_pho(self, file: str | Path) -> None:
        """Save PHO file.

        Args:
            file (str): Path of the output PHO file.
        """
        with Path(file).open("w", encoding="utf-8") as f:
            f.write("\n".join(self.pho))

    def make_sound(
        self,
        file: str | Path,
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
        pho = Path("tmp.pho")

        with Path(pho).open(mode="w", encoding="utf-8") as f:
            f.write("\n".join(self.pho))

        cmd_str = f"{utils._mbrola_cmd()} -f {f0_ratio} -t {dur_ratio} /usr/share/mbrola/{voice}/{voice} {pho} {str(Path(file))}"

        try:
            sp.check_output(cmd_str, shell=True)
        except sp.CalledProcessError as e:
            raise RuntimeError(f"Error when generating {file}:\n{e}")

        f.close()
        if remove_pho:
            pho.unlink()


def _make_pho(x: MBROLA) -> list[str]:
    """Generate PHO file.

    A PHO (.pho) file contains the phonological information of the speech sound in a format that MBROLA can read. See more examples in the MBROLA documentation (https://github.com/numediart/MBROLA).

    Arguments:
        x (MBROLA): MBROLA object to make a PHO file for.

    Returns:
        list[str]: Lines in the PHO file.
    """
    pho = [f"; {' '.join(x.phon)}", f"_ {x.outer_silences[0]}"]

    for ph, d, p in zip(x.phon, x.durations, x.pitch):
        p_seq = " ".join([str(pi) for pi in p])
        pho.append(" ".join(map(str, [ph, d, p_seq])))

    pho.append(f"_ {x.outer_silences[1]}")

    return pho


if __name__ == "__main__":
    cafe = MBROLA(
        phon=["k", "a", "f", "f", "E1"],
        durations=[200, 300, 200, 200, 200],
        pitch=[200, [(50.0, 400)], [(30, 200.1)], 200.0, []],
        outer_silences=(10, 10),
    )

    cafe.export_pho("test.pho")
    print(cafe)
