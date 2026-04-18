# AMD AI Voice API - Ollama & XTTS-v2 (ROCm)

Lokal AI-server optimerad för **AMD GPU (RX 6700 XT)** på native Linux (Ubuntu 24.04). Använder **Ollama** som hjärna (LLM) och **XTTS-v2** som röst (TTS).

## 🚀 Egenskaper

- **AMD GPU (ROCm) Acceleration**: Fullt stöd för XTTS-v2 på Radeon-kort.
- **Ollama Integration**: Använder din befintliga Ollama-instans för LLM-svar (t.ex. DeepSeek-R1).
- **RAM-Disk Processing**: Alla ljudfiler genereras i `/dev/shm` (RAM) för extrem hastighet och noll disk-slitage.
- **Högkvalitativ MP3**: Automatisk konvertering från WAV till **320kbps MP3** via FFmpeg.
- **DeepSeek-R1 Optimerad**: Rensar automatiskt bort `<think>` block innan uppläsning för naturligt tal.

## 🛠️ Installation

1. **Installera Systemberoenden**:
   ```bash
   sudo apt update && sudo apt install -y ffmpeg
   ```

2. **Förbered miljön (ROCm)**:
   Kör vårt automatiserade setup-script som fixar AMD-drivrutiner och PyTorch:
   ```bash
   chmod +x setup_rocm.sh
   ./setup_rocm.sh
   ```

3. **Ollama**:
   Se till att Ollama körs lokalt på port 11434. Vi rekommenderar en svensk-optimerad modell:
   ```bash
   ollama run deepseek-r1:7b
   # Eller för bättre svenska:
   # ollama run llama3-swedish-instruct
   ```

## 🏃 Körning

Starta servern med GPU-stöd:
```bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/ollama/rocm
export HSA_OVERRIDE_GFX_VERSION=10.3.0
source .venv/bin/activate
python -m uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

## 📡 API Endpoints

### `POST /process`
Kombinerad endpoint: Fråga -> LLM -> Tal -> MP3.
- **Payload**:
  ```json
  {
    "prompt": "Berätta en kort saga om en riddare.",
    "model": "deepseek-r1:7b",
    "speaker": "Daisy",
    "bitrate": "320k"
  }
  ```
- **Retur**: En högkvalitativ `.mp3` fil. Den genererade texten finns i HTTP-headern `X-Generated-Text`.

### `GET /health`
Kontrollera status för GPU, TTS-modellen och RAM-disken.

### `GET /speakers`
Lista alla tillgängliga röster i XTTS-v2 modellt (t.ex. Daisy, Viktor, Ana).

## 📁 Struktur
```text
.
├── setup_rocm.sh       # Automatiserad miljö-setup för AMD
├── src/
│   └── app.py          # FastAPI-applikation (Ollama + TTS + MP3)
├── audio_out/          # (Används ej längre, allt körs i /dev/shm)
└── pyproject.toml      # Projektberoenden (uv)
```

## ⚖️ Licens
Koden är MIT. XTTS-v2 använder [Coqui CPML](https://coqui.ai/cpml). Genom att använda detta API godkänner du deras villkor.
