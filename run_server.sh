#!/bin/bash
# Startup script with GPU override for RX 6700 XT
export HSA_OVERRIDE_GFX_VERSION=10.3.0
source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.
fastapi run src/main.py
