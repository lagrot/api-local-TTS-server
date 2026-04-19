import os
import pytest
from src.tts_engine import TTSLoaderFactory

# Tvinga CPU för alla tester för att undvika VRAM-svält
os.environ["CUDA_VISIBLE_DEVICES"] = ""

@pytest.fixture(scope="session")
def mms_loader():
    return TTSLoaderFactory.get_loader("mms")

@pytest.fixture(scope="session")
def fish_loader():
    return TTSLoaderFactory.get_loader("fish")
