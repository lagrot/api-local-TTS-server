import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_mp3_header():
    response = client.post("/tts", json={"text": "Testar MP3-header"})
    assert response.status_code == 200
    # MP3-filer kan börja med ID3-tagg
    assert response.content[:3] == b'ID3'
