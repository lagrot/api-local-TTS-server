# AMD AI Voice API (MMS Edition)

Lokal AI-server för TTS (Text-to-Speech) med Meta MMS.

## Arkitektur
- **TTS**: Meta MMS via PyTorch.
- **Konvertering**: FFmpeg (för MP3-streaming).
- **API**: FastAPI.

## Drift
1. Installera beroenden: `uv sync`
2. Starta servern: `fastapi run src/main.py`
3. Testa: `curl -X POST http://localhost:8000/tts -H "Content-Type: application/json" -d '{"text": "Hej"}' -o output.mp3`

## ⚠️ Viktigt: Beroenden & ROCm
Detta projekt använder **AMD ROCm 7.2.1**. 
Standard-PyTorch från PyPI kommer inte att fungera med GPU-acceleration. 
Innan `uv sync`, måste de officiella AMD .whl-filerna installeras manuellt:
1. Ladda ner hjulen från AMD:s repo.
2. Kör `uv pip install *.whl`.
3. Kör därefter `uv sync`.
Se `HARDWARE.md` för detaljerade instruktioner.
