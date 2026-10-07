import pytest

from src.pymbrola import mbrola as mb


@pytest.fixture(scope="session", autouse=True)
def mb_fix():
    return mb.MBROLA(["k", "a", "f", "f", "E1"], 100, 200, (1, 1))


@pytest.fixture(scope="session", autouse=True)
def voices_path(tmpdir_factory):
    return tmpdir_factory.mktemp("voices")
