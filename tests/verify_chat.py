import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_chat_endpoint():
    print("\nQA: Testar /chat endpoint...")
    response = client.post("/chat", json={"prompt": "Svara med ordet 'okej'."})
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    print("QA: Chat endpoint test passed!")

if __name__ == "__main__":
    test_chat_endpoint()
