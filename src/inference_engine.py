import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging

logger = logging.getLogger(__name__)

class QwenInferenceEngine:
    def __init__(self, model_dir):
        logger.info(f"Loading Qwen-based model from {model_dir} using native transformers...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_dir, 
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.model.eval()

    def generate(self, text):
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            output = self.model.generate(**inputs, max_new_tokens=200)
        return self.tokenizer.decode(output[0], skip_special_tokens=True)
