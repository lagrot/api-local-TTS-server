#!/bin/bash
set -e

echo "--- AMD AI Voice Setup (Ollama-Integrated) ---"

# 1. Environment and VENV
mkdir -p audio_out .tmp
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv --python 3.10
fi

source .venv/bin/activate

# 2. Install PyTorch with ROCm 6.0 (for XTTS-v2)
echo "Installing PyTorch with ROCm 6.0 support..."
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.0 --force-reinstall

# 3. Sync other dependencies from pyproject.toml
echo "Syncing other project dependencies..."
uv sync

# 4. Final Verification Check
echo "--- Verifying Installation ---"
python3 -c "import torch; print(f'Torch: {torch.__version__}'); print(f'HIP Backend: {getattr(torch.version, \"hip\", \"MISSING\")}'); print(f'GPU Available: {torch.cuda.is_available()}')"

echo "--- Setup Complete! ---"
echo "To start the server:"
echo "source .venv/bin/activate && uv run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload"
