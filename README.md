# AMD AI Voice API (MMS Edition)
Lokal AI-server med Ollama (GPU) och Meta MMS TTS (Högkvalitativ, underhållen 2025-standard).

## Arkitektur
- **LLM**: Ollama (`ai-sweden-llama3`).
- **TTS**: Meta MMS (Massively Multilingual Speech) via PyTorch.
- **API**: FastAPI (Standardiserad).

## Drift
1. Installera beroenden: `uv sync`
2. Starta servern: `python src/api_server.py`
3. Testa: `curl -X POST http://localhost:8000/process -d '{"prompt": "..."}'`
