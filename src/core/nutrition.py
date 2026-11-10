"""Pure nutrition arithmetic. No LLM, no I/O. Unit-tested."""

from __future__ import annotations

from src.constants import KJ_PER_KCAL, NUTRIENT_CODES


def scale_nutrients(per_100g: dict[str, float | None], mass_g: float) -> dict[str, float | None]:
    """Scale per-100g values by mass. NULL stays NULL (never 0)."""
    factor = mass_g / 100.0
    out: dict[str, float | None] = {}
    for code in NUTRIENT_CODES:
        v = per_100g.get(code)
        out[code] = (v * factor) if v is not None else None
    return out


def kj_to_kcal(kj: float | None) -> float | None:
    if kj is None:
        return None
    return kj / KJ_PER_KCAL


def sum_nutrients(parts: list[dict[str, float | None]]) -> dict[str, float | None]:
    """Sum nutrient dicts; a code is NULL unless at least one part reports it."""
    totals: dict[str, float | None] = {c: None for c in NUTRIENT_CODES}
    for code in NUTRIENT_CODES:
        vals = [p.get(code) for p in parts if p.get(code) is not None]
        if vals:
            totals[code] = sum(vals)
    return totals


def macro_split(totals: dict[str, float | None]) -> dict[str, float] | None:
    kcal = totals.get("kcal")
    if not kcal or kcal <= 0:
        return None
    p = (totals.get("protein_g") or 0) * 4
    c = (totals.get("carb_g") or 0) * 4
    f = (totals.get("fat_g") or 0) * 9
    return {
        "protein_pct": round(100 * p / kcal, 1),
        "carb_pct": round(100 * c / kcal, 1),
        "fat_pct": round(100 * f / kcal, 1),
    }
