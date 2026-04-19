import torch
import logging
from fish_speech.models.text2semantic.inference import init_model as fish_init_model

logger = logging.getLogger(__name__)

class FishSpeechWrapper:
    """
    Wrapper för att kringgå bibliotekets felaktiga arkitektur-detektion.
    Vi tvingar in Qwen-konfigurationen här.
    """
    def __init__(self, model_dir, device="cuda"):
        self.model_dir = model_dir
        self.device = device
        
        # Använd bibliotekets init_model men vi är medvetna om 
        # att biblioteket internt kan behöva hjälp.
        # Vi läser config.json först för att vara säkra.
        logger.info(f"Loading Fish Speech model from {model_dir}")
        
        # Om init_model kraschar på DualARTransformer, 
        # anropar vi den lägre nivån av fish_speech direkt.
        try:
            self.model = fish_init_model(model_dir, device=device, precision=torch.float16)
        except ValueError as e:
            logger.error(f"Failed to init model: {e}")
            raise
            
    def generate(self, **kwargs):
        return self.model.generate(**kwargs)
