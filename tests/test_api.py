import pytest
from httpx import AsyncClient
from src.app import app
import os

TEST_OUTPUT_DIR = "test_audio_out"

@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    if not os.path.exists(TEST_OUTPUT_DIR):
        os.makedirs(TEST_OUTPUT_DIR)
    yield
    if os.path.exists(TEST_OUTPUT_DIR):
        for f in os.listdir(TEST_OUTPUT_DIR):
            os.remove(os.path.join(TEST_OUTPUT_DIR, f))
        os.rmdir(TEST_OUTPUT_DIR)

@pytest.mark.asyncio
async def test_generate_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/generate", json={"prompt": "Hej!"})
        assert response.status_code == 200
        assert "text" in response.json()

@pytest.mark.asyncio
async def test_speak_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/speak", json={"prompt": "Test."})
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"

@pytest.mark.asyncio
async def test_process_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/process", json={"prompt": "Kort historia."})
        assert response.status_code == 200
        assert "text" in response.json()