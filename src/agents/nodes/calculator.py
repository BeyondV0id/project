"""Calculator node: pure Python nutrition arithmetic."""

from __future__ import annotations

from src.core.nutrition import scale_nutrients, sum_nutrients


def calculate(state):
    nutrients = {}
    comps = state.get("components", [])
    for c in comps:
        ord_ = str(c["ord"])
        match = (state.get("matches") or {}).get(ord_, {})
        per100 = match.get("per_100g", {}) if match else {}
        mass = (state.get("portions") or {}).get(ord_, {}).get("mass_g", 100.0)
        scaled = scale_nutrients(per100, mass or 100.0)
        c["nutrients"] = scaled
        c["kcal"] = scaled.get("kcal")
        c["protein_g"] = scaled.get("protein_g")
        c["carb_g"] = scaled.get("carb_g")
        c["fat_g"] = scaled.get("fat_g")
        c["fibre_g"] = scaled.get("fibre_g")
        nutrients[ord_] = scaled
    # meal totals
    meal = sum_nutrients([c.get("nutrients", {}) for c in comps])
    state["nutrients"] = nutrients
    state["meal_totals"] = meal
    return {"nutrients": nutrients, "components": comps}
