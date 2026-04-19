import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_tts_endpoint():
    response = client.post("/tts", json={"text": "Test"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"

def test_chat_endpoint_mock(mocker):
    # Mocka OllamaClient för att inte kräva en rullande tjänst i integrationstestet
    mock_generate = mocker.patch("src.llm_engine.OllamaClient.generate_text")
    mock_generate.return_value = "Hej från AI"
    
    response = client.post("/chat", json={"prompt": "Hej"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
