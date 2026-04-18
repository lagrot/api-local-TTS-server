import os
from src.tts_engine import generate_audio

def test_generate_audio():
    os.makedirs("audio_out", exist_ok=True)
    output = "audio_out/test.mp3"
    result = generate_audio("Detta är ett test av den stabila motorn.", output)
    assert os.path.exists(result), "Filen skapades inte"
    assert os.path.getsize(result) > 1000, "Filen är för liten"
    print("✅ Ticket #1 Verifierad.")

if __name__ == "__main__":
    test_generate_audio()
