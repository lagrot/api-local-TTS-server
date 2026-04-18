#!/bin/bash
set -e

echo "--- AMD AI Voice Setup (Piper High-Quality) ---"

# 1. Fresh Start
mkdir -p audio_out .tmp models/piper
rm -rf .venv

# 2. Create venv
uv venv --python 3.10
source .venv/bin/activate

# 3. Install core dependencies
# Piper is much lighter than Coqui TTS
uv pip install fastapi uvicorn pydantic python-multipart httpx torch==2.4.1+rocm6.0 --index-url https://download.pytorch.org/whl/rocm6.0
uv pip install piper-tts

# 4. Download High-Quality Swedish Model
echo "Downloading high-quality Swedish Piper model..."
if [ ! -f "models/piper/sv_SE-tbatch-medium.onnx" ]; then
    wget -O models/piper/sv_SE-tbatch-medium.onnx https://github.com/rhasspy/piper-voices/releases/download/v1.0.0/sv_SE-tbatch-medium.onnx
    wget -O models/piper/sv_SE-tbatch-medium.onnx.json https://github.com/rhasspy/piper-voices/releases/download/v1.0.0/sv_SE-tbatch-medium.onnx.json
fi

echo "--- Setup Complete! ---"
echo "To start: source .venv/bin/activate && python -m uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload"
