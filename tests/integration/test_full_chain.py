import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_full_chain():
    print("\nQA: Stort integrationstest (Full kedja)...")
    # Testar tts_direct med ett längre manus
    manus = "Detta är ett officiellt integrationstest av systemet. Kvaliteten är nu optimerad för radio och TV. Allt körs lokalt."
    response = client.post("/tts_direct", json={"text": manus})
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert len(response.content) > 10000 # Borde vara betydande fil
    print(f"QA: Test passerat, ljudfil genererad ({len(response.content)} bytes)")

if __name__ == "__main__":
    test_full_chain()
