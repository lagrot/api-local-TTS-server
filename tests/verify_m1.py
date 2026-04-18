import os
from src.tts_engine_mms import generate_audio

def test_mms():
    print("🚀 Verifierar MMS-motorn...")
    os.makedirs("audio_out", exist_ok=True)
    output = "audio_out/mms_test.mp3"
    generate_audio("Detta är ett test av Meta MMS-motorn.", output)
    assert os.path.exists(output)
    print("✅ MMS Verifierad!")

if __name__ == "__main__":
    test_mms()
