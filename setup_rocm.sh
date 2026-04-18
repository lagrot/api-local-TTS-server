#!/bin/bash
set -e

echo "--- AMD AI Voice Setup (Ollama-Integrated) ---"

# 1. Start Fresh
echo "Clearing old environment for a clean state..."
rm -rf .venv
mkdir -p audio_out .tmp

# 2. Create new venv and Sync
echo "Creating new virtual environment and syncing with ROCm index..."
uv venv --python 3.10
source .venv/bin/activate
uv sync --index rocm

# 3. Final Verification Check
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
