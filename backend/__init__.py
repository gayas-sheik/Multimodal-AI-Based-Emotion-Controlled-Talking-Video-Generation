"""Backend package for the standalone FLOAT application."""

from pathlib import Path
import sys


# Web dependencies are deliberately installed in this project directory, not
# into the externally managed ComfyUI embedded-Python site-packages.
_VENDOR_DIR = Path(__file__).resolve().parent / "vendor"
if _VENDOR_DIR.is_dir() and str(_VENDOR_DIR) not in sys.path:
    sys.path.insert(0, str(_VENDOR_DIR))
