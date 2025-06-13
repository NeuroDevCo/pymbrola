"""Test validation functions."""

import pytest
from mbrola import mbrola

WORD = "mbrola"
PHON = list(WORD)


def test_validate_word():
    """Validate validate_word."""
    assert mbrola.validate_word(WORD)
    assert mbrola.validate_word(WORD) == WORD

    with pytest.raises(TypeError):
        mbrola.validate_word(1)

    with pytest.raises(ValueError):
        mbrola.validate_word("a" * 256)

    with pytest.raises(ValueError):
        mbrola.validate_word("a/")


def test_validate_phon():
    """Test validate_phon."""
    assert mbrola.validate_phon(PHON) == PHON
    assert mbrola.validate_phon("mbrola") == PHON
    assert mbrola.validate_phon([1, 2, 3]) == ["1", "2", "3"]

    with pytest.raises(TypeError):
        mbrola.validate_phon(1)


def test_validate_durations():
    """Test validate_durations."""
    nphon = len(PHON)
    assert mbrola.validate_durations(PHON, durations=100)
    assert mbrola.validate_durations(PHON, durations=100) == [100] * nphon
    assert mbrola.validate_durations(PHON, durations=[100] * nphon)
    assert mbrola.validate_durations(PHON, durations=[100] * nphon) == [100] * len(PHON)

    with pytest.raises(ValueError):
        mbrola.validate_durations(PHON, durations=[100])

    with pytest.raises(TypeError):
        mbrola.validate_durations(PHON, durations="100")


def test_validate_pitch():
    """Test validate_pitch."""
    nphon = len(PHON)
    pitch_int = 200
    output_int = [[200, 200]] * nphon
    pitch_list = [200, [200, 10, 200], 200, 200, 200, 200]
    output_list = [
        [200, 200],
        [200, 10, 200],
        [200, 200],
        [200, 200],
        [200, 200],
        [200, 200],
    ]

    assert mbrola.validate_pitch(PHON, pitch_int)
    assert mbrola.validate_pitch(PHON, pitch_int) == output_int
    assert mbrola.validate_pitch(PHON, [pitch_int] * nphon) == output_int
    assert mbrola.validate_pitch(PHON, pitch_list) == output_list

    with pytest.raises(TypeError):
        mbrola.validate_pitch(PHON, "200")
    with pytest.raises(TypeError):
        mbrola.validate_pitch(PHON, [200, "200", 200, 200, 200, 200])
    with pytest.raises(TypeError):
        mbrola.validate_pitch(PHON, [200, [200, "200"], 200, 200, 200, 200])
    with pytest.raises(TypeError):
        mbrola.validate_pitch(PHON, [200, (200, 200), 200, 200, 200, 200])
    with pytest.raises(ValueError):
        mbrola.validate_pitch(PHON, [200, 200])


def test_validate_outer_silences():
    """Test validate_outer_silences."""
    outer_silences = (1, 1)

    assert mbrola.validate_outer_silences(outer_silences) == outer_silences
    with pytest.raises(TypeError):
        mbrola.validate_outer_silences(outer_silences="2")
    with pytest.raises(TypeError):
        mbrola.validate_outer_silences(outer_silences=("a", 1))
