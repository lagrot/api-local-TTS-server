import torch
import logging
from .base import BaseAdapter

logger = logging.getLogger(__name__)

class WindowsAdapter(BaseAdapter):
    def setup_env(self) -> None:
        # Windows-specific environment tuning could go here
        logger.info("Initializing Windows environment")

    def check_gpu_available(self) -> bool:
        try:
            import torch_directml
            return torch_directml.is_available()
        except ImportError:
            return torch.cuda.is_available()

    def get_gpu_info(self) -> dict:
        return {
            "platform": "Windows",
            "backend": "DirectML/CUDA", 
            "available": self.check_gpu_available()
        }

    @property
    def device(self) -> str:
        if self.check_gpu_available():
            try:
                import torch_directml
                return torch_directml.device()
            except ImportError:
                return "cuda"
        return "cpu"
