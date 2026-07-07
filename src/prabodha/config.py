"""Config loader — config over constants (CLAUDE.md).
Concept: āgama-śāsana — the written rule governs the run.
Primitive: YAML -> dict with required-key validation.
"""
from __future__ import annotations
from pathlib import Path
import yaml

def load(path: str | Path, required: tuple[str, ...] = ()) -> dict:
    with open(path) as f:
        cfg = yaml.safe_load(f)
    missing = [k for k in required if k not in cfg]
    if missing:
        raise KeyError(f"config {path} missing required keys: {missing}")
    return cfg
