import pytest
from src.tts_engine import TTSLoaderFactory

@pytest.fixture(scope="session")
def mms_loader():
    return TTSLoaderFactory.get_loader("mms")

@pytest.fixture(scope="session")
def piper_loader():
    return TTSLoaderFactory.get_loader("piper")

@pytest.fixture(scope="session")
def fish_loader():
    return TTSLoaderFactory.get_loader("fish")
