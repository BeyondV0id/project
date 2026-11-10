"""Report assembler: builds AnalysisResponse from validated state. No LLM."""

from __future__ import annotations

from datetime import datetime, timezone

from src.constants import DISCLAIMER
from src.core.schemas import AnalysisResponse, AnalysisStatus, MealSummary, Nutrients


def assemble(analysis_id: str, tier: str, image_info, components, kb_version, model, latency_ms=None) -> AnalysisResponse:
    parts = [c.nutrients.model_dump() for c in components]
    # sum
    totals = {k: None for k in ("kcal", "protein_g", "carb_g", "fat_g", "fibre_g")}
    for k in totals:
        vals = [p.get(k) for p in parts if p.get(k) is not None]
        if vals:
            totals[k] = sum(vals)
    n_matched = sum(1 for c in components if c.food is not None)
    mass_total = sum(c.mass_g or 0 for c in components) or 1.0
    matched_mass = sum((c.mass_g or 0) for c in components if c.food is not None)
    meal = MealSummary(
        n_components=len(components),
        n_matched=n_matched,
        matched_mass_pct=round(matched_mass / mass_total, 3),
        totals=Nutrients(**totals),
        confidence=round(sum(c.confidence for c in components) / max(len(components), 1), 3),
    )
    return AnalysisResponse(
        analysis_id=analysis_id,
        status=AnalysisStatus.complete,
        created_at=datetime.now(timezone.utc),
        tier=tier,
        image=image_info,
        meal=meal,
        components=components,
        disclaimer=DISCLAIMER,
        kb_version=kb_version,
        model=model,
        latency_ms=latency_ms,
    )
