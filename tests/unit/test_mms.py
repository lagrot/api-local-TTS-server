from src.tts_engine import MMSLoader


def test_mms_loader():
    print("QA: Initierar MMSLoader...")
    loader = MMSLoader()
    # Modellen laddas vid __init__
    assert loader.model is not None
    print("QA: MMS Model Loader test passed!")


if __name__ == "__main__":
    test_mms_loader()
