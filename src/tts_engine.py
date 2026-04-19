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


class FishSpeechLoader(BaseTTSLoader):
    def __init__(self, model_dir="models/fish-speech-s2-pro"):
        super().__init__()
        # S2 Pro initialization with split device strategy to fit in 12GB VRAM
        self.model_dir = model_dir
        self.sampling_rate = 44100  # Default for S2 Pro
        
        # 1. Load Text-to-Semantic (Llama) on GPU
        logger.info("Initializing Fish Speech S2 Pro T2S on GPU...")
        from fish_speech.models.text2semantic.llama import DualARTransformer
        
        t2s_precision = torch.bfloat16 if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else torch.float16
        self.t2s_model = DualARTransformer.from_pretrained(model_dir, load_weights=True)
        # Limit context window to save VRAM and increase speed (KV Cache is huge)
        # 4096 is enough for short snippets and fits in 12GB
        self.t2s_model.config.max_seq_len = 4096
        self.t2s_model.to(device=self.device, dtype=t2s_precision)
        self.t2s_model.eval()
        
        # 2. Load DAC (Codec) on CPU to save VRAM
        logger.info("Initializing Fish Speech S2 Pro DAC on CPU...")
        from fish_speech.models.dac.inference import load_model
        codec_path = os.path.join(model_dir, "codec.pth")
        self.dac_model = load_model("modded_dac_vq", codec_path, device="cpu")
        self.dac_model.eval()
        
        # 3. Setup internal state
        from fish_speech.models.text2semantic.inference import decode_one_token_ar
        self.decode_one_token = decode_one_token_ar
        
        logger.info(f" {self.__class__.__name__} initialized (T2S: {self.device}, DAC: CPU)")

    def get_reference_tokens(self, audio_path):
        import soundfile as sf
        from torchaudio.functional import resample
        logger.info(f"Encoding reference audio via soundfile: {audio_path}")
        
        # 1. Läs in ljudet (Robust backend: soundfile)
        wav, sr = sf.read(audio_path)
        # Flytta till CPU eftersom dac_model är på CPU
        wav = torch.from_numpy(wav).float().to("cpu")
        
        # Hantera stereo -> mono om det behövs
        if wav.ndim > 1:
            wav = wav.mean(dim=-1)
            
        # 2. Resample till modellens samplingrate (44.1kHz för S2 Pro)
        wav = resample(wav, sr, self.dac_model.sample_rate)
        
        # 3. Koda till tokens med DAC-modellen (Samma logik som Fish Speech encode_audio)
        model_dtype = next(self.dac_model.parameters()).dtype
        audios = wav[None, None].to(dtype=model_dtype) # (1, 1, T)
        audio_lengths = torch.tensor([len(wav)], device="cpu", dtype=torch.long)
        
        with torch.no_grad():
            indices, feature_lengths = self.dac_model.encode(audios, audio_lengths)
            
        return indices[0, :, : feature_lengths[0]] # (num_codebooks, T)

    def generate(self, text, reference_audio=None, reference_text=None, **kwargs):
        from fish_speech.models.text2semantic.inference import generate_long
        
        logger.info(f"FishSpeech generating: {text[:50]}...")
        
        # Setup conditioning if reference audio is provided
        prompt_tokens = None
        if reference_audio and os.path.exists(reference_audio):
            prompt_tokens = self.get_reference_tokens(reference_audio)
        
        # Ensure model is in eval mode
        self.t2s_model.eval()
        
        with torch.no_grad():
            responses = generate_long(
                model=self.t2s_model,
                device=self.device,
                decode_one_token=self.decode_one_token,
                text=text,
                prompt_text=reference_text, # Add transcription of reference
                prompt_tokens=prompt_tokens,
                num_samples=1,
                max_new_tokens=512,
                top_p=0.7,
                temperature=0.7,
                compile=True,
            )
            
            all_codes = []
            for resp in responses:
                if resp.action == "sample":
                    all_codes.append(resp.codes)
            
            if not all_codes:
                logger.error("FishSpeech generated no codes")
                return np.zeros((1,), dtype="float32")
                
            # Concatenate all codes along the sequence dimension
            first_code = all_codes[0]
            cat_dim = 2 if first_code.ndim == 3 else 1
            full_codes = torch.cat(all_codes, dim=cat_dim)
            
            # If 2D, add batch dim (1, num_codebooks, T)
            if full_codes.ndim == 2:
                full_codes = full_codes[None]
                
            # Convert indices to latent z and decode to audio
            with torch.no_grad():
                # Correct way for DAC in Fish Speech: from_indices already handles decode
                audio_waveform = self.dac_model.from_indices(full_codes.cpu())
                audio_np = audio_waveform.squeeze().cpu().numpy()
            
        return audio_np


class TTSLoaderFactory:
    @staticmethod
    def get_loader(model_type="mms"):
        if model_type == "mms":
            return MMSLoader()
        elif model_type == "fish":
            return FishSpeechLoader()
        else:
            raise ValueError(f"Unknown model type: {model_type}")
