"""Test MBROLA install functions."""

from pathlib import Path

from src.pymbrola import install
from src.pymbrola import mbrola as mb


class TestDownloadVoices:
    def test_install_voices(self, mb_fix):
        test_langs = ["it4", "es3", "fr4"]

        assert install.install_voice(voice=test_langs)
        path = mb.mbrola_path() / "Voices"
        voices = [p.name for p in path.glob("*")]

        assert path.exists()
        assert path.is_dir()

        for l in test_langs:
            assert l in voices
            p = path / l
            assert p.exists()
            assert p.is_dir()
            assert len(list(p.glob("*")))

        mb_fix.to_sound(Path("tests/test.wav"), voice="it4")
        assert Path("tests/test.wav").exists()
