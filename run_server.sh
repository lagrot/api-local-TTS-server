#!/bin/bash
# Startup script with GPU override for RX 6700 XT
export HSA_OVERRIDE_GFX_VERSION=10.3.0

echo "--- Pre-flight environment check ---"

# 1. Kontrollera miljövariabel
if [ "$HSA_OVERRIDE_GFX_VERSION" != "10.3.0" ]; then
    echo "ERROR: HSA_OVERRIDE_GFX_VERSION is not 10.3.0. Check hardware config."
    exit 1
fi

# 2. Kontrollera GPU via Python/Torch
source .venv/bin/activate
python3 -c "import torch; assert torch.cuda.is_available(), 'GPU not available (Torch)'; print('GPU check passed')" || { echo "GPU check failed: Torch could not find GPU."; exit 1; }

echo "--- Environment check passed. Starting server ---"

export PYTHONPATH=$PYTHONPATH:.
fastapi run src/main.py
