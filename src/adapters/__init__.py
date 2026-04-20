from .base import BaseAdapter
from .linux import LinuxAdapter
from .windows import WindowsAdapter
import sys

def get_adapter() -> BaseAdapter:
    if sys.platform == "win32":
        return WindowsAdapter()
    return LinuxAdapter()
