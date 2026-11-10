"""Retrieval node: match components to KB (state-filtered)."""

from __future__ import annotations

# Minimal in-memory KB for offline demo.
KB = {
    "rice": {"food_id": 1, "name": "Rice, cooked", "source": "IFCT2017", "source_ref": "13-026",
             "physical_state": "cooked", "per_100g": {"kcal": 130.0, "protein_g": 2.7, "carb_g": 28.2, "fat_g": 0.3, "fibre_g": 0.4}},
    "dal": {"food_id": 2, "name": "Dal, cooked", "source": "IFCT2017", "source_ref": "04-010",
            "physical_state": "cooked", "per_100g": {"kcal": 116.0, "protein_g": 7.0, "carb_g": 17.0, "fat_g": 3.0, "fibre_g": 4.0}},
}


def retrieve(state):
    matches = {}
    for c in state.get("components", []):
        rec = KB.get(c["label"])
        if rec:
            matches[str(c["ord"])] = rec
    return {"matches": matches}
