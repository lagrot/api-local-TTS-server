import pytest
import asyncio
from src.llm_engine import OllamaClient

@pytest.mark.asyncio
async def test_llm_client():
    client = OllamaClient()
    print("QA: Testar Ollama-anslutning...")
    response = await client.generate_text("Hej, svara bara med ordet 'test'.")
    assert "test" in response.lower()
    print(f"QA: Ollama svarade: {response}")
