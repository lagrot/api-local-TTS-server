import logging
import os
import torch
import numpy as np

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

from src.inference_engine import QwenInferenceEngine

class FishSpeechLoader(BaseTTSLoader):
    def __init__(self, model_dir="models/fish-speech-s2-pro"):
        super().__init__()
        self.model_dir = model_dir
        self.sampling_rate = 44100
        
        logger.info(f"Initializing Fish Speech S2 Pro using native QwenInferenceEngine...")
        self.engine = QwenInferenceEngine(model_dir)
        
        from fish_speech.models.dac.inference import load_model
        codec_path = os.path.join(model_dir, "codec.pth")
        self.dac_model = load_model("modded_dac_vq", codec_path, device="cpu")
        self.dac_model.eval()
        
        logger.info(f" {self.__class__.__name__} initialized on {self.device}")

    def get_reference_tokens(self, audio_path):
        import soundfile as sf
        from torchaudio.functional import resample
        wav, sr = sf.read(audio_path)
        wav = torch.from_numpy(wav).float().to("cpu")
        if wav.ndim > 1:
            wav = wav.mean(dim=-1)
        wav = resample(wav, sr, self.dac_model.sample_rate)
        
        model_dtype = next(self.dac_model.parameters()).dtype
        audios = wav[None, None].to(dtype=model_dtype)
        audio_lengths = torch.tensor([len(wav)], device="cpu", dtype=torch.long)
        
        with torch.no_grad():
            indices, feature_lengths = self.dac_model.encode(audios, audio_lengths)
        return indices[0, :, : feature_lengths[0]]

    @time_it
    def generate(self, text, reference_audio=None, reference_text=None, **kwargs):
        # I den här versionen genererar vi semantik via vår Qwen-motor 
        # och avkodar sedan med DAC.
        # För enkelhetens skull, använd self.engine.generate(text) här
        # (vi bygger vidare på att koppla tokens till DAC sen)
        
        tokens = self.engine.generate(text)
        # Här behöver vi mappa token-output från Qwen till DAC-indices
        # Men för att verifiera laddningen kör vi detta först:
        logger.info(f"Inference complete: {text[:20]}...")
        return np.zeros((1,), dtype="float32") # Placeholder för att verifiera modell-laddningen

class TTSLoaderFactory:
    @staticmethod
    def get_loader(model_type="mms"):
        if model_type == "mms":
            return MMSLoader()
        elif model_type == "fish":
            return FishSpeechLoader()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
