"""Run the FastAPI server with project-local web dependencies."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
VENDOR_DIR = PROJECT_ROOT / "backend" / "vendor"
for path in (PROJECT_ROOT, VENDOR_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import uvicorn


if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=False)
