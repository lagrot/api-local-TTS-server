#!/bin/bash
# Script för att starta servern med rätt miljövariabler för ROCm/AMD
export AMD_SERIALIZE_KERNEL=3
export HSA_OVERRIDE_GFX_VERSION=10.3.0
export PYTHONPATH=.
exec .venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
