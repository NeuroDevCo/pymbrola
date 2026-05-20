import subprocess as sp
from unittest.mock import patch

import pytest

from src import mbrola, utils


@pytest.fixture
def mb_fix():
    return mbrola.MBROLA(["k", "a", "f", "f", "E1"], 100, 200, (1, 1))


class TestDurationValidation:
    def test_validate_durations(self, mb_fix):
        """Test validate_durations."""
        nphon = len(mb_fix)

        assert utils._validate_durations(100, mb_fix.phon)
        assert utils._validate_durations(100, mb_fix.phon) == [100] * nphon
        assert utils._validate_durations([100] * nphon, mb_fix.phon)
        assert utils._validate_durations([100] * nphon, mb_fix.phon) == [100] * len(
            mb_fix
        )

        with pytest.raises(ValueError):
            utils._validate_durations([100], mb_fix.phon)

        with pytest.raises(TypeError):
            utils._validate_durations("100", mb_fix.phon)

        with pytest.raises(TypeError):
            utils._validate_durations(1.0, mb_fix.phon)


class TestPitchValidation:
    """Test pitch validation."""

    def test_int(self, mb_fix, f: int | float = 200):
        """Test validate_pitch."""

        out = [[(0, f)]] * len(mb_fix)
        assert utils._validate_pitch(f, mb_fix.phon) == out

    def test_float(self, mb_fix, f: int | float = 200):
        out = [[(0, f)]] * len(mb_fix)
        with pytest.warns(UserWarning):
            assert utils._validate_pitch(200.1, mb_fix.phon) == out

    def test_int_list(self, mb_fix, f: int | float = 200):
        x = [f] * len(mb_fix)
        out = [[(0, f)]] * len(mb_fix)
        assert utils._validate_pitch(x, mb_fix.phon) == out

    def test_float_list(self, mb_fix, f: int | float = 200.0):
        x = [f] * len(mb_fix)
        out = [[(0, f)]] * len(mb_fix)

        with pytest.warns(UserWarning):
            assert utils._validate_pitch(x, mb_fix.phon) == out

        x = [int(f), [(f, int(f))], [(30, f)], 200.0, []]
        with pytest.warns(UserWarning):
            assert utils._validate_pitch(x, mb_fix.phon) == x

    def test_empty_list(self, mb_fix):
        x = [[]] * len(mb_fix)
        assert utils._validate_pitch(x, mb_fix.phon) == [[]] * len(mb_fix)

    def test_tuple_list(self, mb_fix, t: int | float = 0, f: int | float = 200):
        x = [[(t, f)], [(t, f)], [(t, f)], [(t + 50, f + 50)], [(t, f)]]
        assert utils._validate_pitch(x, mb_fix.phon) == x

    def test_tuple_list_empty(self, mb_fix, t: int | float = 0, f: int | float = 200):
        x = [[(t, f)], [], [], [(t + 50, f + 50)], []]
        assert utils._validate_pitch(x, mb_fix.phon) == x

    def test_bad_length(self, mb_fix, n: int = 4, f: int | float = 200):
        p = [f] * n
        with pytest.raises(ValueError):
            utils._validate_pitch(p, mb_fix.phon)

    def test_bad_type_str(self):
        with pytest.raises(TypeError):
            utils._validate_pitch("200")

    def test_bad_type_str_phon(self, mb_fix):
        with pytest.raises(TypeError):
            utils._validate_pitch("200", mb_fix.phon)

    def test_bad_type_list_str(self, mb_fix):
        with pytest.raises(TypeError):
            utils._validate_pitch(["200"] * len(mb_fix), mb_fix.phon)

    def test_bad_type_list_list_tuple_str(self, mb_fix, f: int | float = 200):
        with pytest.raises(TypeError):
            utils._validate_pitch([[(str(f), f)]] * len(mb_fix), mb_fix.phon)

        with pytest.raises(TypeError):
            utils._validate_pitch([[(200, str(f))]] * len(mb_fix), mb_fix.phon)

    def test_bad_type_list_list(self, mb_fix, f: int | float = 200):
        with pytest.raises(TypeError):
            utils._validate_pitch([[f, f], f, f, f, f], mb_fix.phon)

        with pytest.raises(TypeError):
            utils._validate_pitch([[(f,)], f, f, f, f], mb_fix.phon)

        with pytest.raises(TypeError):
            utils._validate_pitch([[(f, f, f)], f, f, f, f], mb_fix.phon)


class TestOuterSilenceValidation:
    def test_validate_outer_silences(self):
        """Test validate_outer_silences."""
        outer_silences = (1, 1)

        assert utils._validate_outer_silences(outer_silences) == outer_silences

        with pytest.raises(TypeError):
            utils._validate_outer_silences(outer_silences="2")  # ty: ignore[invalid-argument-type]

        with pytest.raises(TypeError):
            utils._validate_outer_silences(outer_silences=("a", 1))  # ty: ignore[invalid-argument-type]


class TestPlatformValidation:
    def test_wsl_available_on_linux(self):
        """Mock os.name as 'posix' (Linux)."""
        with patch("os.name", "posix"):
            assert utils._wsl_available() is False

    def test_wsl_available_wsl_not_in_path(self):
        """Mock os.name as 'nt' (Windows) and wsl not in PATH."""
        with (
            patch("os.name", "nt"),
            patch("shutil.which", return_value=None),
        ):
            assert utils._wsl_available() is False

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
            assert utils._wsl_available() is False

    def test_mbrola_cmd_returns_mbrola_on_posix(self):
        with patch("os.name", "posix"):
            assert utils._mbrola_cmd() == "mbrola"

    def test_mbrola_cmd_returns_mbrola_on_wsl(self):
        with patch("utils._is_wsl", return_value=True):
            assert utils._mbrola_cmd() == "mbrola"
