import torch
import os
from src.tts_engine import TTSLoaderFactory

def generate_fanny_profile():
    # 1. Initiera loader
    loader = TTSLoaderFactory.get_loader("fish")
    
    # 2. Definiera filer
    wav_path = "audio_in/fanny_reference.wav"
    profile_path = "audio_in/fanny.pt"
    
    if not os.path.exists(wav_path):
        print(f"Fel: {wav_path} saknas!")
        return

    print("Kodrar Fanny-referens...")
    
    # 3. Kör encoder
    # get_reference_tokens returnerar (num_codebooks, T)
    tokens = loader.get_reference_tokens(wav_path)
    
    # 4. Spara som PT
    torch.save(tokens, profile_path)
    print(f"Fanny-profil sparad till {profile_path}")

if __name__ == "__main__":
    generate_fanny_profile()
