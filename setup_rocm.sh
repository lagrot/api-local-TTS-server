#!/bin/bash
set -e

echo "--- AMD GPU (ROCm) Setup for Ubuntu 24.04 ---"

# 1. Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
fi

source .venv/bin/activate

# 2. Install ROCm-specific PyTorch
echo "Installing PyTorch with ROCm 6.0 support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.0

# 3. Install llama-cpp-python with HIPBLAS support
echo "Compiling llama-cpp-python with HIPBLAS (AMD GPU) support..."
export CMAKE_ARGS="-DLLAMA_HIPBLAS=on"
pip install llama-cpp-python --force-reinstall --upgrade --no-cache-dir

# 4. Sync other dependencies from pyproject.toml
echo "Syncing other dependencies..."
uv sync

echo "--- Setup Complete! ---"
echo "To activate the environment: source .venv/bin/activate"
echo "To start the server: uv run uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload"
