# src/td_mion_orbitrap/__init__.py
"""
Top‑level package for TD‑MION Orbitrap tools.
"""

# ------------------------------------------------------------------
# Back‑compat imports for old scripts / tests that use bare names
# ------------------------------------------------------------------
import importlib, sys as _sys

for _mod in (
    "thermo",
    "spectrum",
    "blank",
    "blank_utils",
    "integration",
    "kmd",
    "norm",
):
    _sys.modules[_mod] = importlib.import_module(f"td_mion_orbitrap.{_mod}")
