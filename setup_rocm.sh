#!/bin/bash
set -e

echo "--- AMD AI Voice Setup (Piper High-Quality) ---"

# 1. Fresh Start
mkdir -p audio_out .tmp models/piper
rm -rf .venv

# 2. Create venv
uv venv --python 3.10
source .venv/bin/activate

# 3. Core ROCm Installation (Direct to index)
echo "Installing PyTorch with ROCm 6.0 support..."
uv pip install torch==2.4.1+rocm6.0 --index-url https://download.pytorch.org/whl/rocm6.0

# 4. Install Project Dependencies (From default PyPI)
echo "Installing project dependencies..."
# By not using --index-url here, uv will use the standard PyPI
uv pip install piper-tts fastapi uvicorn pydantic python-multipart httpx

# 5. Download High-Quality Swedish Model
echo "Checking high-quality Swedish Piper model..."
if [ ! -f "models/piper/sv_SE-tbatch-medium.onnx" ]; then
    wget -O models/piper/sv_SE-tbatch-medium.onnx https://github.com/rhasspy/piper-voices/releases/download/v1.0.0/sv_SE-tbatch-medium.onnx
    wget -O models/piper/sv_SE-tbatch-medium.onnx.json https://github.com/rhasspy/piper-voices/releases/download/v1.0.0/sv_SE-tbatch-medium.onnx.json
fi

# 6. Verification Check
echo "--- Verifying Installation ---"
python3 -c "import torch; print(f'Torch: {torch.__version__}'); print(f'GPU Available: {torch.cuda.is_available()}')"
python3 -c "import piper; print('Piper Engine: READY')"

echo "--- Setup Complete! ---"
echo "To start: source .venv/bin/activate && python -m uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload"
