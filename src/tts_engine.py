import torch
from transformers import VitsModel, VitsTokenizer

class MMSLoader:
    def __init__(self, model_id="facebook/mms-tts-swe"):
        # KISS: Använd GPU om tillgänglig, annars CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"QA: MMSLoader körs på enhet: {self.device}")
        
        self.model_id = model_id
        self.tokenizer = VitsTokenizer.from_pretrained(model_id)
        self.model = VitsModel.from_pretrained(model_id).to(self.device)

    def load(self):
        return self.model is not None and self.tokenizer is not None
