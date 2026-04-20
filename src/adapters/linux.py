import os
import torch
import logging
from .base import BaseAdapter

logger = logging.getLogger(__name__)

class LinuxAdapter(BaseAdapter):
    def setup_env(self) -> None:
        # RX 6700 XT ROCm requirement
        logger.info("Setting HSA_OVERRIDE_GFX_VERSION=10.3.0 for AMD Radeon RX 6700 XT")
        os.environ["HSA_OVERRIDE_GFX_VERSION"] = "10.3.0"

    def check_gpu_available(self) -> bool:
        return torch.cuda.is_available()

    def get_gpu_info(self) -> dict:
        return {
            "platform": "Linux",
            "backend": "ROCm/CUDA", 
            "available": self.check_gpu_available()
        }

    @property
    def device(self) -> str:
        return "cuda" if self.check_gpu_available() else "cpu"
