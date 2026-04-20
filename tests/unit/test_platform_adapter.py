import sys
import pytest
from unittest.mock import MagicMock, patch
from src.adapters import get_adapter
from src.adapters.linux import LinuxAdapter
from src.adapters.windows import WindowsAdapter

def test_get_adapter_detection():
    with patch("sys.platform", "win32"):
        adapter = get_adapter()
        assert isinstance(adapter, WindowsAdapter)
    
    with patch("sys.platform", "linux"):
        adapter = get_adapter()
        assert isinstance(adapter, LinuxAdapter)

def test_linux_adapter_setup():
    adapter = LinuxAdapter()
    with patch("os.environ", {}) as mock_env:
        adapter.setup_env()
        assert mock_env["HSA_OVERRIDE_GFX_VERSION"] == "10.3.0"

def test_windows_adapter_device_fallback():
    adapter = WindowsAdapter()
    # Mock torch and torch_directml to test fallback to cpu
    with patch("torch.cuda.is_available", return_value=False):
        with patch.dict("sys.modules", {"torch_directml": None}):
            assert adapter.device == "cpu"

@pytest.mark.skipif(sys.platform != "win32", reason="Requires Windows")
def test_windows_adapter_directml_detection():
    # This only runs on Windows if torch_directml is installed
    try:
        import torch_directml
        adapter = WindowsAdapter()
        if torch_directml.is_available():
            assert adapter.device == torch_directml.device()
    except ImportError:
        pytest.skip("torch_directml not installed")
