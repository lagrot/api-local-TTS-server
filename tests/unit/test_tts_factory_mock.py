import pytest
from unittest.mock import MagicMock
from src.tts_engine import TTSLoaderFactory

def test_mms_loader_mock():
    # Mocka modellen så vi slipper ladda den
    loader = TTSLoaderFactory.get_loader("mms")
    loader.generate = MagicMock(return_value=pytest.importorskip("numpy").array([0.1, 0.2, 0.3], dtype='float32'))
    
    audio = loader.generate("Test text")
    assert audio.size == 3
    loader.generate.assert_called_once_with("Test text")
