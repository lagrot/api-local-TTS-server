#!/bin/bash
set -e

echo "--- AMD AI Voice Setup (Ollama-Integrated) ---"

# 1. Fresh Start
echo "Clearing old environment for a clean state..."
rm -rf .venv
mkdir -p audio_out .tmp

# 2. Create new venv
echo "Creating new virtual environment (Python 3.10)..."
uv venv --python 3.10
source .venv/bin/activate

# 3. Core ROCm Installation (Manual to bypass uv sync issues)
echo "Installing PyTorch with ROCm 6.0 support..."
uv pip install torch==2.4.1+rocm6.0 torchvision==0.19.1+rocm6.0 torchaudio==2.4.1+rocm6.0 --index-url https://download.pytorch.org/whl/rocm6.0

# 4. Install Project Dependencies
echo "Installing remaining project dependencies..."
# We install TTS and other requirements manually to ensure no version conflicts
# Explicitly pin transformers to 4.33.0 for Coqui TTS 0.22.0 compatibility
uv pip install TTS==0.22.0 fastapi uvicorn pydantic python-multipart numpy==1.22.0 httpx transformers==4.33.0 tokenizers setuptools "setuptools<70.0.0"


# 5. Final Verification Check
echo "--- Verifying Installation ---"
# Redefining paths for the check script
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/ollama/rocm
export HSA_OVERRIDE_GFX_VERSION=10.3.0

python3 -c "import torch; print(f'Torch: {torch.__version__}'); print(f'HIP Backend: {getattr(torch.version, \"hip\", \"MISSING\")}'); print(f'GPU Available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"

echo "--- Setup Complete! ---"
echo "To start the server with GPU support:"
echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:/usr/local/lib/ollama/rocm"
echo "export HSA_OVERRIDE_GFX_VERSION=10.3.0"
echo "source .venv/bin/activate && uv run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload"
