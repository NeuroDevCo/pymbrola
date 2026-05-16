"""Test MBROLA module."""

import os
from pathlib import Path

import pytest

import mbrola as mb

cafe = mb.MBROLA("cafè", ["k", "a", "f", "f", "E1"], 100, 200, (1, 1))

@pytest.fixture
def mb():
    return mbrola.MBROLA(["k", "a", "f", "f", "E1"], 100, 200, (1, 1))


class TestAttr:
    def test_mbrola_attr(self, mb):
        """Test MBROLA class attributes."""
        assert mb
        assert hasattr(mb, "phon")
        assert hasattr(mb, "durations")
        assert hasattr(mb, "pitch")
        assert hasattr(mb, "outer_silences")
        assert hasattr(mb, "pho")
        assert hasattr(mb, "export_pho")
        assert hasattr(mb, "make_sound")

    def test_mbrola_attr_type(self, mb):
        """Test MBROLA class attribute types."""
        assert isinstance(mb.phon, list)
        assert isinstance(mb.durations, list)
        assert isinstance(mb.pitch, list)
        assert all(isinstance(p, list) for p in mb.pitch)
        assert isinstance(mb.outer_silences, tuple)
        assert hasattr(mb, "pho")
        assert isinstance(mb.pho, list)
        assert all(isinstance(p, str) for p in mb.pho)
        assert callable(mb.export_pho)
        assert callable(mb.make_sound)


class TestPho:
    def test_mbrola_pho(self, mb):
        """Test mbrola.pho attribute."""
        assert mb.pho[0].startswith("; ")
        assert mb.pho[1].startswith("_ ")
        assert all(p.startswith(mb.phon[i]) for i, p in enumerate(mb.pho[2:-1]))

        def strip(x: str | int, chars="(), "):
            return str(x).strip(chars)

        for i, ph, d, p in zip(mb.pho[2:-1], mb.phon, mb.durations, mb.pitch):
            pho = [strip(ti) for ti in i.split(" ", maxsplit=3)]
            pho_0, pho_1, pho_2, pho_3 = pho
            assert pho_0 == str(ph)
            assert pho_1 == str(d)
            assert pho_2 == str(p[0][0])
            assert pho_3 == str(p[0][1])

        assert mb.pho[-1].startswith("_ ")

    def test_make_pho(self):
        """Test make_pho function."""
        tree = mbrola.MBROLA(phon=["b", "a", "k", "a"])
        assert mbrola.make_pho(tree)

    def test_export_pho(self, mb):
        """Test MBROLA.export_pho method."""
        file = Path("tests", "mb.pho")
        mb.export_pho(file=file)
        assert file.exists()

        with open(file, encoding="utf-8") as f:
            lines = [line.strip("\n") for line in f.readlines()]
        assert lines == mb.pho
        os.unlink(file)


class TestSound:
    def test_make_sound(self, mb):
        """Test MBROLA.make_sound method."""
        file = Path("tests", "mb.wav")
        mb.make_sound(file=file)
        assert file.exists()
        os.unlink(file)


class TestValidations:
    def test_validate_word(self):
        """Validate validate_word."""
        assert mb.validate_word(WORD)
        assert mb.validate_word(WORD) == WORD

        with pytest.raises(TypeError):
            mb.validate_word(1)  # ty: ignore[invalid-argument-type]

        with pytest.raises(ValueError):
            mb.validate_word("a" * 256)

        with pytest.raises(ValueError):
            mb.validate_word("a/")

    def test_validate_durations(self):
        """Test validate_durations."""
        nphon = len(mb)

        assert mbrola.validate_durations(100, mb.phon)
        assert mbrola.validate_durations(100, mb.phon) == [100] * nphon
        assert mbrola.validate_durations([100] * nphon, mb.phon)
        assert mbrola.validate_durations([100] * nphon, mb.phon) == [100] * len(mb)

        with pytest.raises(ValueError):
            mbrola.validate_durations([100], mb.phon)

        with pytest.raises(TypeError):
            mbrola.validate_durations("100", mb.phon)

        with pytest.raises(TypeError):
            mbrola.validate_durations(1.0, mb.phon)


class TestPitchValidation:
    """Test pitch validation."""

    def test_int(self, mb, f: int | float = 200):
        """Test validate_pitch."""

        out = [[(0, f)]] * len(mb)
        assert mbrola.validate_pitch(f, mb.phon) == out

    def test_int_list(self, mb, f: int | float = 200):
        x = [f] * len(mb)
        out = [[(0, f)]] * len(mb)
        assert mbrola.validate_pitch(x, mb.phon) == out

    def test_float_list(self, mb, f: int | float = 200.0):
        x = [f] * len(mb)
        out = [[(0, f)]] * len(mb)

        with pytest.warns(UserWarning):
            assert mbrola.validate_pitch(x, mb.phon) == out

    def test_empty_list(self, mb):
        x = [[]] * len(mb)
        assert mbrola.validate_pitch(x, mb.phon) == [[]] * len(mb)

    def test_tuple_list(self, mb, t: int | float = 0, f: int | float = 200):
        x = [[(t, f)], [(t, f)], [(t, f)], [(t + 50, f + 50)], [(t, f)]]
        assert mbrola.validate_pitch(x, mb.phon) == x

    def test_tuple_list_empty(self, mb, t: int | float = 0, f: int | float = 200):
        x = [[(t, f)], [], [], [(t + 50, f + 50)], []]
        assert mbrola.validate_pitch(x, mb.phon) == x

    def test_bad_type_str(self, mb):
        with pytest.raises(TypeError):
            mbrola.validate_pitch("200", mb.phon)

    def test_bad_type_list_str(self, mb):
        with pytest.raises(TypeError):
            mbrola.validate_pitch(["200"] * len(mb), mb.phon)

    def test_bad_type_list_list_tuple_str(self, mb, f: int | float = 200):
        with pytest.raises(TypeError):
            mbrola.validate_pitch([[(str(f), f)]] * len(mb), mb.phon)

        with pytest.raises(TypeError):
            mbrola.validate_pitch([[(200, str(f))]] * len(mb), mb.phon)

    def test_bad_type_list_list(self, mb, f: int | float = 200):
        with pytest.raises(TypeError):
            mbrola.validate_pitch([[f, f], f, f, f], mb.phon)

        with pytest.raises(TypeError):
            mbrola.validate_pitch([[(f,)], f, f, f], mb.phon)

        with pytest.raises(TypeError):
            mbrola.validate_pitch([[(f, f, f)], f, f, f], mb.phon)


class TestOuterSilenceValidation:
    def test_validate_outer_silences(self):
        """Test validate_outer_silences."""
        outer_silences = (1, 1)

        assert mb.validate_outer_silences(outer_silences) == outer_silences

        with pytest.raises(TypeError):
            mb.validate_outer_silences(outer_silences="2")  # ty: ignore[invalid-argument-type]

        with pytest.raises(TypeError):
            mb.validate_outer_silences(outer_silences=("a", 1))  # ty: ignore[invalid-argument-type]
