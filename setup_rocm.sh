#!/bin/bash
set -e

echo "--- AMD GPU (ROCm) Setup for Ubuntu 24.04 ---"

# 1. Environment and VENV
mkdir -p .tmp models audio_out
export TMPDIR=$(pwd)/.tmp

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

# 2. Install PyTorch ROCm
echo "Installing PyTorch with ROCm 6.0 support..."
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.0

# 3. Install build tools needed for llama-cpp-python
echo "Checking for build tools..."
if ! command -v cmake &> /dev/null; then
    echo "Warning: cmake not found. Attempting to install via uv pip..."
    uv pip install cmake
fi

# 4. Compile llama-cpp-python with ROCm (HIPBLAS) support
echo "Compiling llama-cpp-python with HIPBLAS support..."
# Using --no-cache-dir and a local TMPDIR to avoid disk space issues
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
echo "To start: source .venv/bin/activate && uv run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload"
