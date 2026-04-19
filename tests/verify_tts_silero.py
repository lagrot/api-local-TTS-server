from fastapi.testclient import TestClient
from src.main import app

def test_tts_endpoint():
    client = TestClient(app)
    response = client.post("/tts", json={"text": "Hej, detta är ett test."})
    assert response.status_code == 200
    assert len(response.content) > 0
