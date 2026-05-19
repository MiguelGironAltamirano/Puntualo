"""Conftest local de tests (no commitear — AGENTS.md §4).

Asegura que `app/` es importable cuando se corre pytest desde el dir backend.
"""
import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))
