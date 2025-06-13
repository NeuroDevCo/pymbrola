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


def test_validate_durations():
    """Test validate_durations."""
    nphon = len(PHON)
    assert mbrola.validate_durations(100, PHON)
    assert mbrola.validate_durations(100, PHON) == [100] * nphon
    assert mbrola.validate_durations([100] * nphon, PHON)
    assert mbrola.validate_durations([100] * nphon, PHON) == [100] * len(PHON)
    with pytest.raises(ValueError):
        mbrola.validate_durations([100], PHON)
    with pytest.raises(ValueError):
        mbrola.validate_durations("100", PHON)
    with pytest.raises(TypeError):
        mbrola.validate_durations(1.0, PHON)


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
    assert mbrola.validate_pitch(pitch_int, PHON)
    assert mbrola.validate_pitch(pitch_int, PHON) == output_int
    assert mbrola.validate_pitch([pitch_int] * nphon, PHON) == output_int
    assert mbrola.validate_pitch(pitch_list, PHON) == output_list
    with pytest.raises(ValueError):
        mbrola.validate_pitch("200", PHON)
    with pytest.raises(TypeError):
        mbrola.validate_pitch([200, "200", 200, 200, 200, 200], PHON)
    with pytest.raises(TypeError):
        mbrola.validate_pitch([200, [200, "200"], 200, 200, 200, 200], PHON)
    with pytest.raises(TypeError):
        mbrola.validate_pitch([200, (200, 200), 200, 200, 200, 200], PHON)
    with pytest.raises(ValueError):
        mbrola.validate_pitch([200, 200], PHON)
    with pytest.raises(TypeError):
        mbrola.validate_pitch(1.0, PHON)


def test_validate_outer_silences():
    """Test validate_outer_silences."""
    outer_silences = (1, 1)
    assert mbrola.validate_outer_silences(outer_silences) == outer_silences
    with pytest.raises(TypeError):
        mbrola.validate_outer_silences(outer_silences="2")
    with pytest.raises(TypeError):
        mbrola.validate_outer_silences(outer_silences=("a", 1))
