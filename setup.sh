#!/bin/bash
set -e

echo "--- AMD AI Voice Setup (Simplified & Stable) ---"

# 1. Fresh Start
mkdir -p .tmp models/piper
rm -rf .venv

# 2. Create venv
echo "Creating virtual environment (Python 3.10)..."
uv venv --python 3.10
source .venv/bin/activate

# 3. Install Essential Dependencies
echo "Installing project dependencies (Piper + FastAPI)..."
uv pip install fastapi uvicorn piper-tts httpx

# 4. Download High-Quality Swedish Piper Model (NST)
# We use the 'nst' model which you shared - it's the Swedish standard
echo "Downloading Swedish Piper model (NST Medium)..."
MODEL_DIR="models/piper"
BASE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/sv/sv_SE/nst/medium"

if [ ! -f "$MODEL_DIR/sv_SE-nst-medium.onnx" ]; then
    wget -O "$MODEL_DIR/sv_SE-nst-medium.onnx" "$BASE_URL/sv_SE-nst-medium.onnx"
    wget -O "$MODEL_DIR/sv_SE-nst-medium.onnx.json" "$BASE_URL/sv_SE-nst-medium.onnx.json"
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
