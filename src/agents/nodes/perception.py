"""Perception node: VLM decomposes image into components (no calories)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def perceive(state, provider="mock"):
    # Mock provider: deterministic decomposition keyed by image hash.
    path = state.get("image_path")
    data = b""
    if path and Path(path).exists():
        data = Path(path).read_bytes()
    h = hashlib.sha256(data).hexdigest()[:8]
    components = [
        {"ord": 0, "label": "rice", "display_label": "Steamed rice",
         "bbox_norm": (0.08, 0.22, 0.46, 0.78), "mass_g": None},
        {"ord": 1, "label": "dal", "display_label": "Dal",
         "bbox_norm": (0.5, 0.3, 0.85, 0.7), "mass_g": None},
    ]
    return {"components": components, "quality": 0.81}
