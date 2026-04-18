from src.tts_engine import MMSLoader

def test_mms_loader():
    print("QA: Initierar MMSLoader...")
    loader = MMSLoader()
    success = loader.load()
    assert success == True
    print("QA: MMS Model Loader test passed!")

if __name__ == "__main__":
    test_mms_loader()
