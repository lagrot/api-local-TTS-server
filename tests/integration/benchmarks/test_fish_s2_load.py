import torch
import logging
import os
from fish_speech.models.text2semantic.inference import init_model
from fish_speech.models.dac.inference import load_model

logging.basicConfig(level=logging.INFO)
device = "cuda" if torch.cuda.is_available() else "cpu"
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "10.3.0"

# Models path
model_dir = "models/fish-speech-s2-pro"

print(f"QA: Testing Fish Speech S2 Pro load on {device}...")

try:
    # 1. Load T2S
    print("QA: Loading Text-to-Semantic model...")
    # S2 Pro has config.json and .safetensors
    # We might need to point to the directory
    t2s_precision = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16
    
    # DualARTransformer.from_pretrained(checkpoint_path)
    # Let's see if it works
    from fish_speech.models.text2semantic.llama import DualARTransformer
    t2s_model = DualARTransformer.from_pretrained(model_dir, load_weights=True)
    t2s_model.to(device=device, dtype=t2s_precision)
    print("QA: T2S loaded.")

    # 2. Load DAC
    print("QA: Loading DAC model...")
    # load_model(config_name, checkpoint_path, device="cuda")
    # S2 Pro uses modded_dac_vq.yaml probably
    codec_path = os.path.join(model_dir, "codec.pth")
    # For S2 Pro, we need to know the config name.
    # Looking at the file list: config.json exists.
    # But load_model looks in configs/ directory of the package.
    # Standard config for S2 Pro is likely "modded_dac_vq"
    dac_model = load_model("modded_dac_vq", codec_path, device=device)
    print("QA: DAC loaded.")

    print("QA: SUCCESS! Both models loaded.")

except Exception as e:
    print(f"QA: FAILED to load: {e}")
    import traceback
    traceback.print_exc()
