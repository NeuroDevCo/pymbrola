"""Test MBROLA module."""

import os
from pathlib import Path

import pytest

import mbrola as mb

cafe = mb.MBROLA("cafè", ["k", "a", "f", "f", "E1"], 100, 200, (1, 1))


WORD = "mbrola"
PHON = list(WORD)


class TestAttr:
    def test_mbrola_attr(self):
        """Test MBROLA class attributes."""
        assert cafe
        assert hasattr(cafe, "word")
        assert hasattr(cafe, "phon")
        assert hasattr(cafe, "durations")
        assert hasattr(cafe, "pitch")
        assert hasattr(cafe, "outer_silences")
        assert hasattr(cafe, "pho")
        assert hasattr(cafe, "export_pho")
        assert hasattr(cafe, "make_sound")

    def test_mbrola_attr_type(self):
        """Test MBROLA class attribute types."""
        assert isinstance(cafe.word, str)
        assert isinstance(cafe.phon, list)
        assert isinstance(cafe.durations, list)
        assert isinstance(cafe.pitch, list)
        assert all(isinstance(p, list) for p in cafe.pitch)
        assert all(isinstance(pi, int) for p in cafe.pitch for pi in p)
        assert isinstance(cafe.outer_silences, tuple)
        assert hasattr(cafe, "pho")
        assert isinstance(cafe.pho, list)
        assert all(isinstance(p, str) for p in cafe.pho)
        assert callable(cafe.export_pho)
        assert callable(cafe.make_sound)

    def test_mbrola_dunders(self):
        """Test that string is correct."""
        assert "MBROLA object for word" in str(cafe)
        assert "MBROLA object for word" in repr(cafe)


class TestPho:
    def test_mbrola_pho(self):
        """Test mbrola.pho attribute."""
        assert len(cafe.pho) == len(cafe.phon) + 3
        assert cafe.pho[0].startswith("; ")
        assert cafe.pho[1].startswith("_ ")
        assert all(p.startswith(cafe.phon[i]) for i, p in enumerate(cafe.pho[2:-1]))
        for i, d, p in zip(cafe.pho[2:-1], cafe.durations, cafe.pitch):
            assert i.split(" ")[1] == str(d)
            assert i.split(" ")[2] == str(p[0])
            assert i.split(" ")[3] == str(p[1])
        assert cafe.pho[-1].startswith("_ ")

    def test_make_pho(self):
        """Test make_pho function."""
        tree = mb.MBROLA(word="vaca", phon=["b", "a", "k", "a"])
        assert mb.make_pho(tree)

        with pytest.raises(TypeError):
            mb.make_pho("a")  # ty: ignore[invalid-argument-type]

    def test_export_pho(self):
        """Test MBROLA.export_pho method."""
        file = Path("tests", "cafe.pho")
        cafe.export_pho(file=file)
        assert file.exists()

        with open(file, encoding="utf-8") as f:
            lines = [line.strip("\n") for line in f.readlines()]
        assert lines == cafe.pho
        os.unlink(file)


class TestSound:
    def test_make_sound(self):
        """Test MBROLA.make_sound method."""
        file = Path("tests", "cafe.wav")
        cafe.make_sound(file=file)
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
        nphon = len(PHON)

        assert mb.validate_durations(100, PHON)
        assert mb.validate_durations(100, PHON) == [100] * nphon
        assert mb.validate_durations([100] * nphon, PHON)
        assert mb.validate_durations([100] * nphon, PHON) == [100] * len(PHON)

        with pytest.raises(ValueError):
            mb.validate_durations([100], PHON)

        with pytest.raises(TypeError):
            mb.validate_durations("100", PHON)

        with pytest.raises(TypeError):
            mb.validate_durations(1.0, PHON)

    def test_validate_pitch(self):
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

        assert mb.validate_pitch(pitch_int, PHON)
        assert mb.validate_pitch(pitch_int, PHON) == output_int
        assert mb.validate_pitch([pitch_int] * nphon, PHON) == output_int
        assert mb.validate_pitch(pitch_list, PHON) == output_list

        with pytest.raises(TypeError):
            mb.validate_pitch("200", PHON)

        with pytest.raises(TypeError):
            mb.validate_pitch([200, "200", 200, 200, 200, 200], PHON)

        with pytest.raises(TypeError):
            mb.validate_pitch([200, [200, "200"], 200, 200, 200, 200], PHON)

        with pytest.raises(TypeError):
            mb.validate_pitch([200, (200, 200), 200, 200, 200, 200], PHON)

        with pytest.raises(ValueError):
            mb.validate_pitch([200, 200], PHON)

        with pytest.raises(TypeError):
            mb.validate_pitch(1.0, PHON)

    def test_validate_outer_silences(self):
        """Test validate_outer_silences."""
        outer_silences = (1, 1)

        assert mb.validate_outer_silences(outer_silences) == outer_silences

        with pytest.raises(TypeError):
            mb.validate_outer_silences(outer_silences="2")  # ty: ignore[invalid-argument-type]

        with pytest.raises(TypeError):
            mb.validate_outer_silences(outer_silences=("a", 1))  # ty: ignore[invalid-argument-type]
