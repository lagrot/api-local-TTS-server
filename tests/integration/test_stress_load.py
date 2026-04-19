import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


@pytest.mark.slow
def test_long_text_stress():
    # Skicka en text som är tillräckligt lång för att testa pipeline-stabilitet
    long_text = "Detta är ett stresstest. " * 50
    response = client.post("/tts_direct", json={"text": long_text})
    assert response.status_code == 200
    assert len(response.content) > 0
