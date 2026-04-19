import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_tts_endpoint_bad_request():
    response = client.post("/tts", json={})
    assert response.status_code == 422
