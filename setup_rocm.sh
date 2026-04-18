#!/bin/bash
set -e

echo "--- AMD GPU (ROCm) Setup for Ubuntu 24.04 ---"

# 1. Environment and VENV
mkdir -p .tmp models audio_out
export TMPDIR=$(pwd)/.tmp

# Find ROCm libraries (e.g. from Ollama or system)
ROCM_PATH=$(find /usr/local/lib/ollama/rocm -name "libamdhip64.so*" -exec dirname {} \; | head -n 1)
if [ -z "$ROCM_PATH" ]; then
    ROCM_PATH=$(find /opt/rocm -name "libamdhip64.so*" -exec dirname {} \; | head -n 1)
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
    uv venv
fi

# 2. Install PyTorch ROCm 6.1 (Latest stable compatible with Ubuntu 24.04)
echo "Installing PyTorch with ROCm support using uv..."
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.1 --force-reinstall

# 3. Install build tools needed for llama-cpp-python
echo "Checking for build tools..."
if ! command -v cmake &> /dev/null; then
    uv pip install cmake
fi

# 4. Compile llama-cpp-python with ROCm (HIPBLAS) support
echo "Compiling llama-cpp-python with HIPBLAS support..."
export CMAKE_ARGS="-DLLAMA_HIPBLAS=on"
uv pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir

# 5. Sync dependencies
echo "Syncing other dependencies..."
uv sync

# 6. Final Model Check
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
