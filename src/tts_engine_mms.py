import torch
from transformers import VitsModel, AutoTokenizer
import scipy.io.wavfile
import numpy as np
import os

# Ladda modell
model_name = "facebook/mms-tts-swe"
model = VitsModel.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

def generate_audio(text: str, output_path: str):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        output = model(**inputs).waveform
    
    # Spara som wav (MMS ger raw wave)
    scipy.io.wavfile.write(output_path.replace(".mp3", ".wav"), 
                           rate=model.config.sampling_rate, 
                           data=output.squeeze().numpy())
    
    # Konvertera till MP3 med ffmpeg
    import subprocess
    subprocess.run(["ffmpeg", "-y", "-i", output_path.replace(".mp3", ".wav"), 
                    "-codec:a", "libmp3lame", "-b:a", "128k", output_path], check=True)
    os.remove(output_path.replace(".mp3", ".wav"))
    return output_path
