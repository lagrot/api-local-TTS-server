import torch
import logging
import os
import time
from fish_speech.models.text2semantic.llama import DualARTransformer
from fish_speech.models.dac.inference import load_model

logging.basicConfig(level=logging.INFO)
device = "cuda" if torch.cuda.is_available() else "cpu"
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "10.3.0"

model_dir = "models/fish-speech-s2-pro"

print(f"QA: Testing Optimized Fish Speech S2 Pro load...")

try:
    # 1. Load T2S on GPU (BF16)
    print("QA: Loading Text-to-Semantic model on GPU (BF16)...")
    t2s_precision = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16
    t2s_model = DualARTransformer.from_pretrained(model_dir, load_weights=True)
    t2s_model.to(device=device, dtype=t2s_precision)
    print("QA: T2S loaded on GPU.")

    # 2. Load DAC on CPU
    print("QA: Loading DAC model on CPU...")
    codec_path = os.path.join(model_dir, "codec.pth")
    # We load on CPU to save VRAM
    dac_model = load_model("modded_dac_vq", codec_path, device="cpu")
    print("QA: DAC loaded on CPU.")

    print("QA: SUCCESS! Both models loaded with split device strategy.")

except Exception as e:
    print(f"QA: FAILED: {e}")
    import traceback
    traceback.print_exc()
