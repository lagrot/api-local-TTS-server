import torch
import os
import io
import torch.package

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

class SileroTTSLoader(BaseTTSLoader):
    def __init__(self, model_path='model.pt'):
        # Force CPU for Silero as ROCm/HIP is unstable for this model in our environment
        self.device = "cpu"
        print(f"QA: {self.__class__.__name__} tvingas till enhet: {self.device}")
        
        if not os.path.isfile(model_path):
            torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v5_ru.pt', model_path)
        self.model = torch.package.PackageImporter(model_path).load_pickle("tts_models", "model")
        self.model.to(self.device)

    def generate(self, text, speaker='xenia', sample_rate=48000, **kwargs):
        return self.model.apply_tts(text=text, speaker=speaker, sample_rate=sample_rate).numpy()

class TTSLoaderFactory:
    @staticmethod
    def get_loader(model_type="mms"):
        if model_type == "mms":
            return MMSLoader()
        elif model_type == "silero":
            return SileroTTSLoader()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
