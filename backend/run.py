#!/usr/bin/env python3
"""Run the PrivacyRadar API. From backend/: python run.py (with venv and pip install -e .)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import uvicorn
except ModuleNotFoundError:
    print("Install dependencies. In backend/:")
    print("  python3 -m venv .venv && source .venv/bin/activate")
    print("  pip install -e .")
    print("  python run.py")
    sys.exit(1)

if __name__ == "__main__":
    uvicorn.run(
        "app.interface.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
