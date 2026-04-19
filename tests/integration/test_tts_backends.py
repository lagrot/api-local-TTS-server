import pytest
from src.tts_engine import TTSLoaderFactory


@pytest.mark.parametrize("backend", ["mms", "piper"])
def test_backend_generation(backend):
    loader = TTSLoaderFactory.get_loader(backend)
    audio = loader.generate("Testar backend " + backend)
    assert audio is not None
    assert audio.size > 0
