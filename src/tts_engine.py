import torch
from transformers import VitsModel, VitsTokenizer

class MMSLoader:
    def __init__(self, model_id="facebook/mms-tts-swe"):
        self.model_id = model_id
        self.tokenizer = VitsTokenizer.from_pretrained(model_id)
        self.model = VitsModel.from_pretrained(model_id)

    def load(self):
        # Enkel verifiering att modellen laddats
        return self.model is not None and self.tokenizer is not None
