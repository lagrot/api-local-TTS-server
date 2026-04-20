# AMD AI Voice API (S2 Pro Edition)

Lokal AI-server för högkvalitativ TTS med Fish Speech (S2 Pro).

## Arkitektur
- **TTS**: Fish Speech S2 Pro (Qwen-baserad) via ROCm-accelererad PyTorch.
- **Konvertering**: FFmpeg (asynkron streaming).
- **API**: FastAPI.

## Drift

### Linux (ROCm / AMD GPU)
1. **Miljökrav**: AMD RX 6700 XT, ROCm 7.2.1.
2. **Setup**: `uv sync` eller `pip install -r requirements.txt`.
3. **Start**: `./run_server.sh`.

### Windows (DirectML / AMD GPU)
1. **Miljökrav**: AMD Radeon GPU, Adrenaline drivrutiner.
2. **Setup**: `powershell -ExecutionPolicy Bypass -File .\scripts\setup-windows.ps1`.
3. **Start**: `.\.venv\Scripts\fastapi run src\main.py`.
4. **Test**: `curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"prompt": "Hej Fanny"}'`

## Viktigt: GPU-support
Detta projekt är optimerat för AMD GPU (Linux/ROCm och Windows/DirectML). Servern kör en `pre-flight` kontroll vid start som validerar GPU-tillgänglighet via den plattformsspecifika adaptern.
