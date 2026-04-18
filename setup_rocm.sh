#!/bin/bash
set -e

echo "--- AMD GPU (ROCm) Setup for Ubuntu 24.04 ---"

# 1. Environment and VENV
mkdir -p .tmp models audio_out
export TMPDIR=$(pwd)/.tmp

# Find ROCm libraries (e.g. from Ollama or system)
ROCM_PATH=$(find /usr/local/lib/ollama/rocm -name "libamdhip64.so*" -exec dirname {} 2>/dev/null \; | head -n 1)
if [ -z "$ROCM_PATH" ]; then
    ROCM_PATH=$(find /opt/rocm -name "libamdhip64.so*" -exec dirname {} 2>/dev/null \; | head -n 1)
fi

if [ ! -z "$ROCM_PATH" ]; then
    echo "Found ROCm libraries at: $ROCM_PATH"
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ROCM_PATH
    export HSA_OVERRIDE_GFX_VERSION=10.3.0
else
    echo "Warning: No ROCm libraries found. GPU acceleration might fail."
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv --python 3.10
fi

# 2. Sync dependencies with forced ROCm index
echo "Syncing dependencies with ROCm 6.1 index..."
uv sync --index rocm --no-cache

# 3. Explicitly ensure llama-cpp-python is using HIPBLAS
# Re-install with CMAKE_ARGS to make sure it links correctly
echo "Re-compiling llama-cpp-python with HIPBLAS support..."
export CMAKE_ARGS="-DLLAMA_HIPBLAS=on"
uv pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir

# 4. Final Verification Check
echo "--- Verifying Installation ---"
source .venv/bin/activate
# Pass variables again to ensure python script sees them
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ROCM_PATH
export HSA_OVERRIDE_GFX_VERSION=10.3.0
python3 -c "import torch; print(f'Torch: {torch.__version__}'); print(f'HIP Backend: {getattr(torch.version, \"hip\", \"MISSING\")}'); print(f'GPU Available: {torch.cuda.is_available()}')"

if [ ! -f "models/Meta-Llama-3-8B-Instruct.Q5_K_M.gguf" ]; then
    echo "Warning: Llama-3 model file not found in models/."
else
    echo "Success: Model file verified."
fi

echo "--- Setup Complete! ---"
echo "To start with GPU support:"
echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:$ROCM_PATH"
echo "export HSA_OVERRIDE_GFX_VERSION=10.3.0"
echo "source .venv/bin/activate && uv run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload"
