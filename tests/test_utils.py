"""Test MBROLA utils."""

import os
import subprocess as sp
from unittest.mock import patch

import pytest

from src.pymbrola import mbrola as mb


@pytest.fixture(autouse=True)
def clear_cache():
    mb.wsl_available.cache_clear()
    yield
    mb.wsl_available.cache_clear()


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

    @pytest.mark.parametrize(
        "os_name, which_result, expected",
        [
            pytest.param("posix", "/usr/bin/wsl", False, id="not windows"),
            pytest.param("nt", None, False, id="windows but wsl not installed"),
        ],
    )
    def test_wsl_unavailable(self, os_name, which_result, expected, monkeypatch):
        monkeypatch.setattr(os, "name", os_name)
        monkeypatch.setattr("shutil.which", lambda _: which_result)

        assert mb.wsl_available() is expected

    @pytest.mark.parametrize(
        "uname_output, is_wsl_result, expected",
        [
            pytest.param(
                "5.15.153.1-microsoft-standard-WSL2", True, True, id="wsl kernel"
            ),
            pytest.param("6.1.0-18-amd64", False, False, id="non-wsl kernel"),
        ],
    )
    def test_wsl_check_output(self, uname_output, is_wsl_result, expected, monkeypatch):
        monkeypatch.setattr(os, "name", "nt")
        monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/wsl")
        monkeypatch.setattr(mb.is_wsl, "__call__", lambda s: is_wsl_result)
        monkeypatch.setattr(sp, "check_output", lambda *a, **k: uname_output)

        assert mb.wsl_available() is expected

    def test_wsl_subprocess_error(self, monkeypatch):
        monkeypatch.setattr(os, "name", "nt")
        monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/wsl")

        def raise_error(*args, **kwargs):
            raise sp.SubprocessError

        monkeypatch.setattr(sp, "check_output", raise_error)

        assert mb.wsl_available() is False

    def test_wsl_is_cached(self, monkeypatch):
        monkeypatch.setattr(os, "name", "nt")
        monkeypatch.setattr("shutil.which", lambda _: "/usr/bin/wsl")

        calls = []
        monkeypatch.setattr(
            "subprocess.check_output",
            lambda *a, **k: calls.append(a) or "5.15-microsoft-standard-WSL2",
        )

        mb.wsl_available()
        mb.wsl_available()

        assert len(calls) == 1  # second call hits the cache
