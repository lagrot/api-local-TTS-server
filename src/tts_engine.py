import os
import torch
from piper import PiperVoice


class BaseTTSLoader:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"QA: {self.__class__.__name__} körs på enhet: {self.device}")


class MMSLoader(BaseTTSLoader):
    def __init__(self, model_id="facebook/mms-tts-swe"):
        super().__init__()
        # Force CPU for MMS as ROCm/HIP is unstable for this model in our environment
        self.device = "cpu"
        print(f"QA: {self.__class__.__name__} tvingas till enhet: {self.device}")
        from transformers import VitsModel, VitsTokenizer

        self.tokenizer = VitsTokenizer.from_pretrained(model_id)
        self.model = VitsModel.from_pretrained(model_id).to(self.device)

    def generate(self, text, **kwargs):
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            output = self.model(**inputs)
        return output.waveform[0].cpu().numpy()


class PiperTTSLoader(BaseTTSLoader):
    def __init__(self, model_path="sv_SE-nst-medium.onnx"):
        super().__init__()
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
        # Detta är en förenklad implementation för att verifiera att vi kan ladda motorn.
        # En fullständig implementation kräver en Llama-queue.
        print(f"QA: {self.__class__.__name__} initierad på {self.device}")

    def generate(self, text, **kwargs):
        import numpy as np

        # Placeholder för FishSpeech-generering (kräver konfigurerad LLAMA-motor)
        # Vi kommer att bygga ut denna i nästa steg när vi vet att arkitekturen är stabil.
        print(f"QA: FishSpeech genererar ljud för text: {text}")
        return np.zeros((22050,), dtype="float32")


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
