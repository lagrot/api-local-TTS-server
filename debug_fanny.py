import torch
import os
from src.tts_engine import TTSLoaderFactory

# Initiera loader
loader = TTSLoaderFactory.get_loader("fish")

# Kolla Fanny-profil
profile_path = "audio_in/fanny.pt"
if os.path.exists(profile_path):
    tokens = torch.load(profile_path, map_location="cpu")
    print(f"Fanny-profil laddad. Tokens form: {tokens.shape}")
    print(f"Tokens innehåll (snittvärde): {tokens.float().mean().item()}")
else:
    print("Fanny-profil saknas!")
