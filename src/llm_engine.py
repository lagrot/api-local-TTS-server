import httpx


class OllamaClient:
    def __init__(self, host="http://localhost:11434"):
        self.host = host
        # Använd modellen vi verifierade finns: ai-sweden-llama3:latest
        self.model = "ai-sweden-llama3:latest"

    async def generate_text(self, prompt: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.host}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()["response"]
