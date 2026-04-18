#!/bin/bash
set -e

echo "--- AMD AI Voice Setup (Simplified & Stable) ---"

# 1. Start Fresh
mkdir -p .tmp models/piper
rm -rf .venv

# 2. Create venv
echo "Creating virtual environment (Python 3.10)..."
uv venv --python 3.10
source .venv/bin/activate

# 3. Install Essential Dependencies
echo "Installing project dependencies (Piper + FastAPI)..."
uv pip install fastapi uvicorn piper-tts httpx

# 4. Download High-Quality Swedish Piper Model
# We use the 'alby' model which is one of the highest quality Swedish voices
echo "Downloading high-quality Swedish Piper model (Alby)..."
MODEL_DIR="models/piper"
if [ ! -f "$MODEL_DIR/sv_SE-alby-medium.onnx" ]; then
    wget -O "$MODEL_DIR/sv_SE-alby-medium.onnx" https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/sv/sv_SE/alby/medium/sv_SE-alby-medium.onnx
    wget -O "$MODEL_DIR/sv_SE-alby-medium.onnx.json" https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/sv/sv_SE/alby/medium/sv_SE-alby-medium.onnx.json
fi

# 5. Final Verification
echo "--- Verifying Installation ---"
python3 -c "import piper; print('Piper TTS Engine: READY')"
echo "Checking Ollama connectivity..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "Ollama Backend: READY (GPU)"
else
    echo "Warning: Ollama not found on localhost:11434. Make sure it is running."
fi

echo "--- Setup Complete! ---"
echo "To start the server:"
echo "source .venv/bin/activate"
echo "python -m uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload"
