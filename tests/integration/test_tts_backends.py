import pytest

def test_backend_mms(mms_loader):
    audio = mms_loader.generate("Testar mms")
    assert audio is not None
    assert audio.size > 0

def test_backend_piper(piper_loader):
    audio = piper_loader.generate("Testar piper")
    assert audio is not None
    assert audio.size > 0

