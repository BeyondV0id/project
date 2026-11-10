"""Pydantic models â€” the API's only source of numbers."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class AnalysisStatus(str, Enum):
    received = "received"
    running = "running"
    needs_clarification = "needs_clarification"
    complete = "complete"
    partial = "partial"
    failed = "failed"
    rejected = "rejected"


class Tier(str, Enum):
    T0 = "T0"
    T1 = "T1"
    T2 = "T2"


class ImageInfo(BaseModel):
    width: int
    height: int
    quality: float = Field(ge=0, le=1)
    quality_flags: list[Literal["blurry", "dark", "overexposed", "low_resolution"]] = []


class Nutrients(BaseModel):
    kcal: float | None = None
    protein_g: float | None = None
    carb_g: float | None = None
    fat_g: float | None = None
    fibre_g: float | None = None


class FoodRef(BaseModel):
    food_id: int
    name: str
    source: Literal["IFCT2017", "USDA_FDC", "CUSTOM"]
    source_ref: str
    physical_state: str
    is_composite: bool = False


class MassRange(BaseModel):
    low: float
    high: float
    unit: Literal["g"] = "g"


class PortionDetail(BaseModel):
    method: Literal["anchor_area_volume", "household_prior", "composite_recipe", "user_override"]
    anchor: str | None = None
    volume_ml: float | None = None
    density_g_ml: float | None = None
    features: dict[str, float] = {}


class ComponentResult(BaseModel):
    ord: int
    label: str
    display_label: str
    bbox_norm: tuple[float, float, float, float]
    food: FoodRef | None = None
    mass_g: float | None = None
    mass_range: MassRange | None = None
    portion: PortionDetail | None = None
    nutrients: Nutrients
    nutrition_per_100g: Nutrients | None = None
    confidence: float = Field(ge=0, le=1)
    confidence_band: Literal["high", "medium", "low"]
    flags: list[str] = []
    match_type: Literal["alias", "fuzzy", "semantic", "api", "composite", "none"] = "none"

    @field_validator("bbox_norm")
    @classmethod
    def _bbox(cls, v):
        x0, y0, x1, y1 = v
        assert 0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1
        return v


class MacroSplit(BaseModel):
    protein_pct: float
    carb_pct: float
    fat_pct: float


class MealSummary(BaseModel):
    n_components: int
    n_matched: int
    matched_mass_pct: float
    kcal_p10: float | None = None
    kcal_p50: float | None = None
    kcal_p90: float | None = None
    totals: Nutrients
    macro_split: MacroSplit | None = None
    confidence: float = Field(ge=0, le=1)


class QuestionOption(BaseModel):
    value: str
    label: str
    delta_kcal: float | None = None


class Question(BaseModel):
    id: str
    component_ord: int | None = None
    kind: Literal["confirm_identity", "choose_between", "portion_scale", "composite_confirm", "free_text"]
    prompt: str
    options: list[QuestionOption] = []
    allow_free_text: bool = False
    info_gain: float = 0.0


class ProvenanceRecord(BaseModel):
    component_ord: int
    nutrient: str
    value: float | None = None
    source: str
    source_ref: str
    note: str | None = None


class AnalysisResponse(BaseModel):
    analysis_id: str
    status: AnalysisStatus
    created_at: datetime
    tier: Tier
    image: ImageInfo
    meal: MealSummary
    components: list[ComponentResult]
    questions: list[Question] = []
    provenance: list[ProvenanceRecord] = []
    limitations: list[str] = []
    disclaimer: str
    kb_version: str
    model: str
    latency_ms: int | None = None
