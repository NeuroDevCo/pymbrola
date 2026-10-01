import subprocess as sp
from pathlib import Path
from unittest.mock import patch

import pytest

from src import mbrola, utils


@pytest.fixture
def mb_fix():
    return mbrola.MBROLA(["k", "a", "f", "f", "E1"], 100, 200, (1, 1))


@pytest.fixture(scope="session")
def voices_path(tmpdir_factory):
    return tmpdir_factory.mktemp("voices")


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


class TestDownloadVoices:
    def test_install_voices(self, voices_path):
        assert utils.install_voices(path=voices_path)
        path = Path(voices_path)
        voices = [p.name for p in path.glob("*")]

        assert path.exists()
        assert path.is_dir()

        test_langs = ["es3", "fr4"]
        for l in test_langs:
            assert l in voices
            p = path / l
            assert p.exists()
            assert p.is_dir()
            assert len(list(p.glob("*")))
