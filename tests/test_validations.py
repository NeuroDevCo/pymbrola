"""Test MBROLA validations module."""

import pytest

from src.pymbrola import mbrola as mb


class TestDurationValidation:
    def test_validate_durations(self, mb_fix):
        """Test validate_durations."""
        nphon = len(mb_fix)

        assert mb.validate_durations(100, mb_fix.phon)
        assert mb.validate_durations(100, mb_fix.phon) == [100] * nphon
        assert mb.validate_durations([100] * nphon, mb_fix.phon)
        assert mb.validate_durations([100] * nphon, mb_fix.phon) == [100] * len(mb_fix)

        with pytest.raises(ValueError):
            mb.validate_durations([100], mb_fix.phon)

        with pytest.raises(TypeError):
            mb.validate_durations("100", mb_fix.phon)

        with pytest.raises(TypeError):
            mb.validate_durations(None, mb_fix.phon)


class TestPitchValidation:
    """Test pitch validation."""

    def test_int(self, mb_fix, f: float = 200):
        """Test validate_pitch."""

        out = [[(0, f)]] * len(mb_fix)
        assert mb.validate_pitch(f, mb_fix.phon) == out

    def test_float(self, mb_fix, f: float = 200):
        out = [[(0, f)]] * len(mb_fix)
        assert mb.validate_pitch(f, mb_fix.phon) == out

    def test_int_list(self, mb_fix, f: float = 200):
        x = [f] * len(mb_fix)
        out = [[(0, f)]] * len(mb_fix)
        assert mb.validate_pitch(x, mb_fix.phon) == out

    def test_float_list(self, mb_fix, f: float = 200.0):
        x = [f] * len(mb_fix)
        out = [[(0, f)]] * len(mb_fix)
        assert mb.validate_pitch(x, mb_fix.phon) == out

    def test_empty_list(self, mb_fix):
        x = [[]] * len(mb_fix)
        assert mb.validate_pitch(x, mb_fix.phon) == [[]] * len(mb_fix)

    def test_tuple_list(self, mb_fix, t: float = 0, f: float = 200):
        x = [[(t, f)], [(t, f)], [(t, f)], [(t + 50, f + 50)], [(t, f)]]
        assert mb.validate_pitch(x, mb_fix.phon) == x

    def test_tuple_list_empty(self, mb_fix, t: float = 0, f: float = 200):
        x = [[(t, f)], [], [], [(t + 50, f + 50)], []]
        assert mb.validate_pitch(x, mb_fix.phon) == x

    def test_bad_length(self, mb_fix, n: int = 4, f: float = 200):
        p = [f] * n
        with pytest.raises(ValueError):
            mb.validate_pitch(p, mb_fix.phon)

    def test_bad_type_str(self):
        with pytest.raises(TypeError):
            mb.validate_pitch("200")

    def test_bad_type_str_phon(self, mb_fix):
        with pytest.raises(TypeError):
            mb.validate_pitch("200", mb_fix.phon)

    def test_bad_type_list_str(self, mb_fix):
        with pytest.raises(TypeError):
            mb.validate_pitch(["200"] * len(mb_fix), mb_fix.phon)

    def test_bad_type_list_list_tuple_str(self, mb_fix, f: float = 200):
        with pytest.raises(TypeError):
            mb.validate_pitch([[(str(f), f)]] * len(mb_fix), mb_fix.phon)

        with pytest.raises(TypeError):
            mb.validate_pitch([[(200, str(f))]] * len(mb_fix), mb_fix.phon)

    def test_bad_type_list_list(self, mb_fix, f: float = 200):
        with pytest.raises(TypeError):
            mb.validate_pitch([[f, f], f, f, f, f], mb_fix.phon)

        with pytest.raises(TypeError):
            mb.validate_pitch([[(f,)], f, f, f, f], mb_fix.phon)

        with pytest.raises(TypeError):
            mb.validate_pitch([[(f, f, f)], f, f, f, f], mb_fix.phon)


class TestOuterSilenceValidation:
    def test_validate_outer_silences(self):
        """Test validate_outer_silences."""
        outer_silences = (1, 1)

        assert mb.validate_outer_silences(outer_silences) == outer_silences

        with pytest.raises(TypeError):
            mb.validate_outer_silences(outer_silences="2")  # ty: ignore[invalid-argument-type]

        with pytest.raises(TypeError):
            mb.validate_outer_silences(outer_silences=("a", 1))  # ty: ignore[invalid-argument-type]
