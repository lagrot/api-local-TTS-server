# api-local-TTS-server
Lokal AI-server med Llama-3 och XTTS-v2 för AMD GPU (Vulkan/ROCm) på WSL2.

## Struktur
```text
.
├── pyproject.toml      # Beroenden (uv) och ruff-inställningar
├── models/             # Lägg din .gguf-modell här
├── src/
│   └── app.py          # FastAPI-applikation (LLM + TTS)
├── tests/
│   └── test_api.py     # API-tester
└── audio_out/          # Temporär lagring för ljudfiler
```

## Installation

1. **Installera uv** (om du inte har det):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Förbered miljön**:
   ```bash
   uv sync
   ```

3. **Installera llama-cpp-python med Vulkan-stöd**:
   ```bash
   # I WSL2/Linux terminal
   export CMAKE_ARGS="-DLLAMA_VULKAN=on"
   uv pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir
   ```

4. **Modeller**:
   - Skapa mappen `models/`: `mkdir models`
   - Flytta din Llama-3 modell dit: `mv Meta-Llama-3-8B-Instruct.Q5_K_M.gguf models/`
   - XTTS-v2 modellen laddas ner automatiskt vid första körningen (~2GB).

## Körning

Starta servern:
```bash
uv run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

- `POST /generate`: Tar en prompt och returnerar text.
- `POST /speak`: Tar text och returnerar en `.wav`-fil (XTTS-v2).
- `POST /process`: Kombinerad endpoint (Fråga -> Text -> Ljud).

## Tester

Kör rök-tester för att se att allt fungerar:
```bash
uv run pytest tests/
```

## Linting
```bash
uv run ruff check . --fix
```
