import pytest
from fastapi.testclient import TestClient
from src.main import app
import os

client = TestClient(app)

def test_tts_endpoint():
    print("QA: Testar /tts endpoint...")
    response = client.post("/tts?text=Hej+världen")
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert os.path.exists("audio_out/output.wav")
    print("QA: TTS endpoint test passed!")

if __name__ == "__main__":
    test_tts_endpoint()
