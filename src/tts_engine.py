import logging; logger = logging.getLogger(__name__)
import os
import torch
from piper import PiperVoice

class BaseTTSLoader:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f" {self.__class__.__name__} körs på enhet: {self.device}")

class MMSLoader(BaseTTSLoader):
    def __init__(self, model_id="facebook/mms-tts-swe"):
        super().__init__()
        self.device = "cpu"
        self.sampling_rate = 16000
        from transformers import VitsModel, VitsTokenizer
        self.tokenizer = VitsTokenizer.from_pretrained(model_id)
        self.model = VitsModel.from_pretrained(model_id).to(self.device)

    def generate(self, text, **kwargs):
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            output = self.model(**inputs)
        return output.waveform[0].cpu().numpy()

class PiperTTSLoader(BaseTTSLoader):
    def __init__(self, model_path="models/sv_SE-nst-medium.onnx"):
        super().__init__()
        self.sampling_rate = 22050
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"Piper modell saknas: {model_path}")
        self.voice = PiperVoice.load(model_path)

    def generate(self, text, **kwargs):
        import io
        import wave
        import scipy.io.wavfile as wavfile
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wav_file:
            self.voice.synthesize_wav(text, wav_file)
        wav_buffer.seek(0)
        sr, audio = wavfile.read(wav_buffer)
        return audio.astype("float32") / 32767.0

class FishSpeechLoader(BaseTTSLoader):
    def __init__(self):
        super().__init__()
        self.sampling_rate = 22050
        logger.info(f" {self.__class__.__name__} initierad på {self.device}")

    def generate(self, text, **kwargs):
        raise NotImplementedError("FishSpeech-motorn är under utveckling.")

class TTSLoaderFactory:
    @staticmethod
    def get_loader(model_type="mms"):
        if model_type == "mms":
            return MMSLoader()
        elif model_type == "piper":
            return PiperTTSLoader()
        elif model_type == "fish":
            return FishSpeechLoader()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
