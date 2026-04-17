import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_read_main():
    """Verifierar att API-dokumentationen är nåbar."""
    response = client.get("/docs")
    assert response.status_code == 200

def test_generate_endpoint():
    """Smoke test för textgenerering."""
    payload = {"text": "Hej, hur mår du?"}
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    assert "text" in response.json()
    assert len(response.json()["text"]) > 0

def test_speak_endpoint():
    """Smoke test för ljudgenerering."""
    payload = {"text": "Det här är ett test av den svenska rösten."}
    response = client.post("/speak", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"

@pytest.mark.asyncio
async def test_full_process():
    """Testar hela kedjan från fråga till ljud."""
    payload = {"text": "Berätta en mycket kort vits."}
    response = client.post("/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "audio" in data