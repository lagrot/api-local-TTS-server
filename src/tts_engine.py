import logging
import os
import torch

logger = logging.getLogger(__name__)


class BaseTTSLoader:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f" {self.__class__.__name__} körs på enhet: {self.device}")


class MMSLoader(BaseTTSLoader):
    def __init__(self, model_id="facebook/mms-tts-swe"):
        super().__init__()
        self.sampling_rate = 16000
        from transformers import VitsModel, VitsTokenizer

        self.tokenizer = VitsTokenizer.from_pretrained(model_id)
        self.model = VitsModel.from_pretrained(model_id).to(self.device)

    def generate(self, text, **kwargs):
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            output = self.model(**inputs)
        return output.waveform[0].cpu().numpy()


from src.utils import time_it

class FishSpeechLoader(BaseTTSLoader):
    # ... (behåll befintlig kod för __init__ och get_reference_tokens)

    @time_it
    def generate(self, text, reference_audio=None, reference_text=None, **kwargs):
        prompt_tokens = None
        
        # Ny logik för Fanny-profil
        if reference_audio == "fanny":
            profile_path = "audio_in/fanny.pt"
            if os.path.exists(profile_path):
                logger.info("Loading pre-computed Fanny profile...")
                prompt_tokens = torch.load(profile_path, map_location="cpu")
            else:
                logger.warning(f"Fanny profile not found at {profile_path}, falling back to default voice.")
        elif reference_audio and os.path.exists(reference_audio):
            prompt_tokens = self.get_reference_tokens(reference_audio)
        
        with torch.no_grad():
            tokens = self.wrapper.generate(
                text=text,
                prompt_text=reference_text,
                prompt_tokens=prompt_tokens,
                top_p=0.7,
                temperature=0.7,
            )
            audio_waveform = self.dac_model.from_indices(tokens.cpu())
            return audio_waveform.squeeze().cpu().numpy()


class TTSLoaderFactory:
    @staticmethod
    def get_loader(model_type="mms"):
        if model_type == "mms":
            return MMSLoader()
        elif model_type == "fish":
            return FishSpeechLoader()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
