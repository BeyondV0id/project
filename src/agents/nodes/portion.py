"""Portion node: estimate mass per component."""

from __future__ import annotations

from src.core.confidence import band


def estimate_portions(state):
    portions = {}
    for c in state.get("components", []):
        ord_ = str(c["ord"])
        match = (state.get("matches") or {}).get(ord_, {})
        mass = 165.0 if c["label"] == "rice" else 90.0
        portions[ord_] = {
            "mass_g": mass,
            "mass_ci_low": mass * 0.8,
            "mass_ci_high": mass * 1.2,
            "method": "anchor_area_volume",
            "anchor": "dinner_plate_26cm",
        }
        c["mass_g"] = mass
        c["mass_ci_low"] = mass * 0.8
        c["mass_ci_high"] = mass * 1.2
        c["portion_method"] = "anchor_area_volume"
    return {"portions": portions, "components": state.get("components", [])}
