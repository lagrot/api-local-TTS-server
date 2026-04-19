import pytest
from unittest.mock import MagicMock
from src.tts_engine import TTSLoaderFactory

def test_mms_loader_mock(mocker):
    # Skapa en mock-loader
    mock_loader = MagicMock()
    mock_loader.generate.return_value = MagicMock() # Representerar numpy-array
    mock_loader.generate.return_value.size = 3
    
    # Patcha factoryn så att den returnerar vår mock
    mocker.patch("src.tts_engine.TTSLoaderFactory.get_loader", return_value=mock_loader)
    
    # Använd factoryn
    loader = TTSLoaderFactory.get_loader("mms")
    audio = loader.generate("Test text")
    
    assert audio.size == 3
    loader.generate.assert_called_once_with("Test text")
