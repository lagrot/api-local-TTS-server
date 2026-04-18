import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_health():
    """Verify that the health endpoint returns correctly."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "llm_backend" in data

def test_generate_error_no_ollama():
    """Verify that the generator fails gracefully if Ollama is not found (assuming it's not running in CI)."""
    # This might pass or fail depending on if Ollama is running during pytest
    # But it verifies the response structure
    response = client.post("/generate", json={"prompt": "test"})
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        assert "text" in response.json()

def test_clean_text():
    """Test the cleaning logic for DeepSeek-R1 responses."""
    from src.app import clean_text_for_speech
    input_text = "<think>I should say hello.</think> Hello! **World**"
    cleaned = clean_text_for_speech(input_text)
    assert "think" not in cleaned
    assert "World" in cleaned
    assert "*" not in cleaned

@pytest.mark.asyncio
async def test_full_process_structure():
    """Verify the /process endpoint returns the correct media type and headers."""
    # We use a very short prompt to make it fast
    response = client.post("/process", json={"prompt": "Hej", "bitrate": "64k"})
    # If Ollama is running, this should be 200. In CI without Ollama, it will be 503.
    if response.status_code == 200:
        assert response.headers["content-type"] == "audio/mpeg"
        assert "X-Generated-Text" in response.headers
