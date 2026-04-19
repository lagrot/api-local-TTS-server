import os
import pytest
from unittest.mock import MagicMock
from src.tts_engine import TTSLoaderFactory

# Tvinga CPU för alla tester för att undvika VRAM-svält
os.environ["CUDA_VISIBLE_DEVICES"] = ""

@pytest.fixture(autouse=True)
def enforce_cpu():
    # Säkerställ att CUDA_VISIBLE_DEVICES är satt under testets livscykel
    os.environ["CUDA_VISIBLE_DEVICES"] = ""

@pytest.fixture(scope="session")
def mms_loader():
    # Vi mockar loader för att undvika tung modell-laddning i enhets-tester
    loader = MagicMock()
    return loader

@pytest.fixture(scope="session")
def fish_loader():
    # Vi mockar loader för att undvika tung modell-laddning i enhets-tester
    loader = MagicMock()
    return loader

