"""Test MBROLA module."""

import os
from pathlib import Path

import pytest

from src import mbrola as mb


@pytest.fixture
def mb_fix():
    return mb.MBROLA(["k", "a", "f", "f", "E1"], 100, 200, (1, 1))


class TestAttr:
    def test_mbrola(self):
        x = mb.MBROLA(["k", "a", "f", "f", "E1"], 100, 200, (1, 1))
        assert isinstance(x, mb.MBROLA)

    def test_string_phon(self):
        phon = "kaffe"
        x = mb.MBROLA(phon, 100, 200, (1, 1))
        assert isinstance(x.phon, list)
        assert len(x.phon) == len(phon)

        x = mb.MBROLA(phon[0], 100, 200, (1, 1))
        assert isinstance(x.phon, list)
        assert len(x.phon) == 1

    def test_attr(self, mb_fix):
        """Test MBROLA class attributes."""
        assert mb_fix
        assert hasattr(mb_fix, "phon")
        assert hasattr(mb_fix, "durations")
        assert hasattr(mb_fix, "pitch")
        assert hasattr(mb_fix, "outer_silences")
        assert hasattr(mb_fix, "pho")
        assert hasattr(mb_fix, "export_pho")
        assert hasattr(mb_fix, "make_sound")

    def test_attr_type(self, mb_fix):
        """Test MBROLA class attribute types."""
        assert isinstance(mb_fix.phon, list)
        assert isinstance(mb_fix.durations, list)
        assert isinstance(mb_fix.pitch, list)
        assert all(isinstance(p, list) for p in mb_fix.pitch)
        assert isinstance(mb_fix.outer_silences, tuple)
        assert hasattr(mb_fix, "pho")
        assert isinstance(mb_fix.pho, list)
        assert all(isinstance(p, str) for p in mb_fix.pho)
        assert callable(mb_fix.export_pho)
        assert callable(mb_fix.make_sound)

    def test_eq(self, mb_fix):
        mb2 = mb.MBROLA(["k", "a", "f", "f", "E1"], 100, 200, (1, 1))
        assert mb_fix == mb2

    def test_add(self, mb_fix):
        mb2 = mb.MBROLA(["k", "a", "f", "f", "E1"], 100, 200, (1, 1))
        added = mb_fix + mb2
        assert isinstance(added, mb.MBROLA)
        assert len(added) == len(mb_fix) + len(mb2)
        assert len(added.pho) == len(mb_fix.pho) + len(mb2.pho)


class TestPho:
    def test_pho(self, mb_fix):
        """Test mb.pho attribute."""
        assert mb_fix.pho[0].startswith("; ")
        assert mb_fix.pho[1].startswith("_ ")
        assert all(p.startswith(mb_fix.phon[i]) for i, p in enumerate(mb_fix.pho[2:-1]))

        def strip(x: str | int, chars="(), "):
            return str(x).strip(chars)

        for i, ph, d, p in zip(
            mb_fix.pho[2:-1], mb_fix.phon, mb_fix.durations, mb_fix.pitch
        ):
            pho = [strip(ti) for ti in i.split(" ", maxsplit=3)]
            pho_0, pho_1, pho_2, pho_3 = pho
            assert pho_0 == str(ph)
            assert pho_1 == str(d)
            assert pho_2 == str(p[0][0])
            assert pho_3 == str(p[0][1])

        assert mb_fix.pho[-1].startswith("_ ")

    def test_make(self):
        """Test make_pho function."""
        x = mb.MBROLA(phon=["b", "a", "k", "a"])
        assert mb._make_pho(x)

    def test_export(self, mb_fix):
        """Test MBROLA.export_pho method."""
        file = Path("tests", "mb_fix.pho")
        mb_fix.export_pho(file=file)
        assert file.exists()

        with open(file, encoding="utf-8") as f:
            lines = [line.strip("\n") for line in f.readlines()]

        assert lines == mb_fix.pho
        os.unlink(file)


class TestSound:
    def test_make_sound(self, mb_fix):
        """Test MBROLA.make_sound method."""
        file = Path("tests", "mb_fix.wav")
        mb_fix.make_sound(file=file)
        assert file.exists()
        os.unlink(file)

    def test_sp_error(self, mb_fix):
        with pytest.raises(RuntimeError):
            file = Path("bad_path", "mb_fix.wav")
            mb_fix.make_sound(file=file)
