# AMD AI Voice API (S2 Pro Edition)

Lokal AI-server för högkvalitativ TTS med Fish Speech (S2 Pro).

## Arkitektur
- **TTS**: Fish Speech S2 Pro (Qwen-baserad) via ROCm-accelererad PyTorch.
- **Konvertering**: FFmpeg (asynkron streaming).
- **API**: FastAPI.

## Drift
1. **Miljökrav**: AMD RX 6700 XT, ROCm 7.2.1, `HSA_OVERRIDE_GFX_VERSION=10.3.0`.
2. **Setup**: `uv sync`
3. **Start**: `./run_server.sh`
4. **Test**: `curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"prompt": "Hej Fanny"}'`

## Viktigt: GPU-support
Detta projekt körs enbart på AMD GPU. Servern kör en `pre-flight` kontroll vid start som validerar GPU-tillgänglighet.
