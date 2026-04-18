import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_tts_endpoint():
    print("QA: Testar /tts (MP3 via FFmpeg)...")
    response = client.post("/tts", json={"text": "Detta är ett test av MP3 via FFmpeg"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    print("QA: TTS MP3 endpoint test passed!")

if __name__ == "__main__":
    test_tts_endpoint()
