"""Test MBROLA module."""

import os
from pathlib import Path
import subprocess as sp
from unittest.mock import patch

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
        assert mb.make_pho(x)

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
            mb.validate_durations(1.0, mb_fix.phon)


class TestPitchValidation:
    """Test pitch validation."""

    def test_int(self, mb_fix, f: int | float = 200):
        """Test validate_pitch."""

        out = [[(0, f)]] * len(mb_fix)
        assert mb.validate_pitch(f, mb_fix.phon) == out

    def test_float(self, mb_fix, f: int | float = 200):
        out = [[(0, f)]] * len(mb_fix)
        with pytest.warns(UserWarning):
            assert mb.validate_pitch(200.1, mb_fix.phon) == out

    def test_int_list(self, mb_fix, f: int | float = 200):
        x = [f] * len(mb_fix)
        out = [[(0, f)]] * len(mb_fix)
        assert mb.validate_pitch(x, mb_fix.phon) == out

    def test_float_list(self, mb_fix, f: int | float = 200.0):
        x = [f] * len(mb_fix)
        out = [[(0, f)]] * len(mb_fix)

        with pytest.warns(UserWarning):
            assert mb.validate_pitch(x, mb_fix.phon) == out

        x = [int(f), [(f, int(f))], [(30, f)], 200.0, []]
        with pytest.warns(UserWarning):
            assert mb.validate_pitch(x, mb_fix.phon) == x

    def test_empty_list(self, mb_fix):
        x = [[]] * len(mb_fix)
        assert mb.validate_pitch(x, mb_fix.phon) == [[]] * len(mb_fix)

    def test_tuple_list(self, mb_fix, t: int | float = 0, f: int | float = 200):
        x = [[(t, f)], [(t, f)], [(t, f)], [(t + 50, f + 50)], [(t, f)]]
        assert mb.validate_pitch(x, mb_fix.phon) == x

    def test_tuple_list_empty(self, mb_fix, t: int | float = 0, f: int | float = 200):
        x = [[(t, f)], [], [], [(t + 50, f + 50)], []]
        assert mb.validate_pitch(x, mb_fix.phon) == x

    def test_bad_length(self, mb_fix, n: int = 4, f: int | float = 200):
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

    def test_bad_type_list_list_tuple_str(self, mb_fix, f: int | float = 200):
        with pytest.raises(TypeError):
            mb.validate_pitch([[(str(f), f)]] * len(mb_fix), mb_fix.phon)

        with pytest.raises(TypeError):
            mb.validate_pitch([[(200, str(f))]] * len(mb_fix), mb_fix.phon)

    def test_bad_type_list_list(self, mb_fix, f: int | float = 200):
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


class TestPlatformValidation:
    def test_wsl_available_on_linux(self):
        """Mock os.name as 'posix' (Linux)."""
        with patch("os.name", "posix"):
            assert mb.wsl_available() is False

    def test_wsl_available_wsl_not_in_path(self):
        """Mock os.name as 'nt' (Windows) and wsl not in PATH."""
        with (
            patch("os.name", "nt"),
            patch("shutil.which", return_value=None),
        ):
            assert mb.wsl_available() is False

    def test_wsl_available_subprocess_error(self):
        """Mock os.name as 'nt', wsl in PATH, but subprocess raises an error."""
        with (
            patch("os.name", "nt"),
            patch("shutil.which", return_value="/usr/bin/wsl"),
            patch(
                "mbrola.sp.check_output",
                side_effect=sp.SubprocessError("WSL command failed"),
            ),
        ):
            assert mb.wsl_available() is False

    def test_mbrola_cmd_returns_mbrola_on_posix(self):
        with patch("os.name", "posix"):
            assert mb.mbrola_cmd() == "mbrola"

    def test_mbrola_cmd_returns_mbrola_on_wsl(self):
        with patch("mbrola.is_wsl", return_value=True):
            assert mb.mbrola_cmd() == "mbrola"
