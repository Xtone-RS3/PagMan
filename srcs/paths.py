from pathlib import Path
import sys
from typing import Any

if getattr(sys, "frozen", False):
    base = getattr(sys, "_MEIPASS", None)
    if base is None:
        raise RuntimeError("Frozen app missing _MEIPASS")
    ROOT = Path(base)
else:
    ROOT = Path(__file__).resolve().parent.parent


def asset(*parts: Any) -> Path:
    return ROOT.joinpath(*parts)
