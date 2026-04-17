import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app, clean_text_for_speech
import os
import asyncio

TEST_OUTPUT_DIR = "test_audio_out"

@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    if not os.path.exists(TEST_OUTPUT_DIR):
        os.makedirs(TEST_OUTPUT_DIR)
    yield
    if os.path.exists(TEST_OUTPUT_DIR):
        for f in os.listdir(TEST_OUTPUT_DIR):
            if f.endswith(".wav"):
                os.remove(os.path.join(TEST_OUTPUT_DIR, f))
        os.rmdir(TEST_OUTPUT_DIR)

def test_clean_text_for_speech():
    assert clean_text_for_speech("*Hej* #världen#") == "Hej världen"
    assert clean_text_for_speech("  extra   mellanslag  ") == "extra mellanslag"

@pytest.mark.asyncio
async def test_generate_endpoint_invalid_input():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/generate", json={})
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_generate_endpoint_valid():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/generate", json={"prompt": "Hej, vem är du?"})
        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert len(data["text"]) > 0

@pytest.mark.asyncio
async def test_process_endpoint_valid():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/process", json={"prompt": "Berätta något kort."})
        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert "audio_info" in data

@pytest.mark.asyncio
async def test_invalid_method():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/generate")
        assert response.status_code == 405
