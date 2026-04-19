# Hardware Inventory & System Layout

## Compute Resources
- **CPU:** AMD Ryzen 5 5600X (6-Core)
- **RAM:** 31 GiB
- **GPU:** AMD Radeon RX 6700 XT (12 GB VRAM)
  - **Driver/Framework:** Navi 22 (ROCm-stöd tillgängligt för framtida optimering)

## Storage
- **Primary:** 2x 1TB NVMe SSD (High-performance storage for model weights)

## Optimization Strategy
- **Phase 1 (Current):** CPU-based inference (Stability & Reliability).
- **Phase 2 (Future):** Enable ROCm acceleration via `setup_rocm.sh` to utilize 12GB VRAM.

## System Dependencies
- **System Libraries:**
  -  (för MP3-transcoding)
  -  (för audio-stream-hantering via PyAudio/FishSpeech)
- **Frameworks:**
  -  (Kräver AMD GPU-stöd i OS)

## GPU Specific Configuration
- **Architecture:** gfx1031 (RX 6700 XT)
- **ROCm Compatibility:** Requires `export HSA_OVERRIDE_GFX_VERSION=10.3.0` to function with PyTorch/ROCm.
