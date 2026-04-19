import logging
import os
import scipy.io.wavfile as wavfile
from src.tts_engine import FishSpeechLoader

logging.basicConfig(level=logging.INFO)
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "10.3.0"

print("QA: Testing Fish Speech S2 Pro generation...")

try:
    loader = FishSpeechLoader()
    text = "Hej, detta är ett röstprov i studiokvalitet genererat med Fish Speech S2 Pro. Vi utnyttjar full GPU-kraft."
    
    import time
    start = time.time()
    audio = loader.generate(text)
    duration = time.time() - start
    
    print(f"QA: Generation complete in {duration:.2f} seconds.")
    print(f"QA: Audio shape: {audio.shape}, Type: {audio.dtype}")
    
    # Save to file to check quality
    output_path = "audio_out/fish_s2_test.wav"
    os.makedirs("audio_out", exist_ok=True)
    
    # Normalize to int16
    if audio.dtype == 'float32':
        audio_int = (audio * 32767).astype('int16')
    else:
        audio_int = audio
        
    wavfile.write(output_path, loader.sampling_rate, audio_int)
    print(f"QA: Saved test audio to {output_path}")

except Exception as e:
    print(f"QA: FAILED: {e}")
    import traceback
    traceback.print_exc()
