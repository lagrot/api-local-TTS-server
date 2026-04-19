import torch
import pytest

def test_gpu_availability():
    """Verifierar att GPU (ROCm) är tillgänglig och kan allokera tensorer."""
    if not torch.cuda.is_available():
        pytest.skip("CUDA/ROCm inte tillgänglig på denna maskin")
    
    device = torch.device("cuda")
    x = torch.tensor([1.0, 2.0, 3.0], device=device)
    assert x.device.type == "cuda"
    assert x.sum().item() == 6.0
