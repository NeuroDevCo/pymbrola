"""Test MBROLA module."""

import os
from pathlib import Path
import pytest
from mbrola import mbrola

cafe = mbrola.MBROLA("cafè", ["k", "a", "f", "f", "E1"], 100, 200, (1, 1))


def test_mbrola_attr():
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


def test_mbrola_attr_type():
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


def test_mbrola_pho():
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


def test_make_pho():
    """Test make_pho function."""
    tree = mbrola.MBROLA(word="vaca", phon=["b", "a", "k", "a"])
    assert mbrola.make_pho(tree)

    with pytest.raises(TypeError):
        mbrola.make_pho("a")


def test_export_pho():
    """Test MBROLA.export_pho method."""
    file = Path("tests", "cafe.pho")
    cafe.export_pho(file=file)
    assert file.exists()

    with open(file, encoding="utf-8") as f:
        lines = [line.strip("\n") for line in f.readlines()]
    assert lines == cafe.pho
    os.unlink(file)


def test_make_sound():
    """Test MBROLA.make_sound method."""
    file = Path("tests", "cafe.wav")
    cafe.make_sound(file=file)
    assert file.exists()
    os.unlink(file)
