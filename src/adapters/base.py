from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseAdapter(ABC):
    @abstractmethod
    def setup_env(self) -> None:
        """Initialize platform-specific environment variables and checks."""
        pass

    @abstractmethod
    def check_gpu_available(self) -> bool:
        """Verify if the targeted hardware accelerator is available."""
        pass

    @abstractmethod
    def get_gpu_info(self) -> dict:
        """Return platform-specific hardware information."""
        pass

    @property
    @abstractmethod
    def device(self) -> str:
        """Return the torch-compatible device string (e.g., 'cuda', 'dml', 'cpu')."""
        pass
