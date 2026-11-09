# 05 — API Contracts

The API is the **only** boundary the UI and the evaluation harness are allowed to use. If Streamlit computes a number that the API did not return, that is a bug.

Base URL: `http://localhost:8000` · Content type: `application/json` (except uploads, `multipart/form-data`) · Versioning: path prefix `/v1`.

---

## 1. Endpoint summary

| Method | Path | Purpose | Typical latency |
|---|---|---|---|
| `POST` | `/v1/analyses` | Upload a meal photo and run the pipeline | 3–25 s |
| `GET` | `/v1/analyses/{id}` | Fetch a stored report (replay, refresh-safe) | < 100 ms |
| `POST` | `/v1/analyses/{id}/clarify` | Submit answers, resume the graph | 2–10 s |
| `PATCH` | `/v1/analyses/{id}/components/{ord}` | Correct identity or mass, recompute | < 500 ms |
| `POST` | `/v1/analyses/{id}/components` | Add a missed component | < 500 ms |
| `DELETE` | `/v1/analyses/{id}` | Delete analysis + artifacts (privacy) | < 200 ms |
| `GET` | `/v1/foods/search` | Search the KB directly (typeahead, corrections) | < 150 ms |
| `GET` | `/v1/meta` | Provider, kb_version, model, mock flag, limits | < 50 ms |
| `GET` | `/healthz` | Liveness + dependency checks | < 50 ms |

---

## 2. Core models (Pydantic v2)

```python
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
    T0 = "T0"; T1 = "T1"; T2 = "T2"

class ImageInfo(BaseModel):
    width: int
    height: int
    quality: float = Field(ge=0, le=1)
    quality_flags: list[Literal["blurry","dark","overexposed","low_resolution"]] = []

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
    method: Literal["anchor_area_volume","household_prior","composite_recipe","user_override"]
    anchor: str | None = None              # "dinner_plate_26cm" | "spoon" | "none"
    volume_ml: float | None = None
    density_g_ml: float | None = None
    features: dict[str, float] = {}        # area_cm2, heap_k, px_per_cm, ...

class ComponentResult(BaseModel):
    ord: int
    label: str                              # raw label from perception
    display_label: str                      # human-facing, tidied
    bbox_norm: tuple[float, float, float, float]
    food: FoodRef | None = None
    mass_g: float | None = None
    mass_range: MassRange | None = None
    portion: PortionDetail | None = None
    nutrients: Nutrients
    nutrition_per_100g: Nutrients | None = None
    confidence: float = Field(ge=0, le=1)
    confidence_band: Literal["high","medium","low"]
    flags: list[str] = []
    match_type: Literal["alias","fuzzy","semantic","api","composite","none"] = "none"

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
    kcal_p10: float | None
    kcal_p50: float | None
    kcal_p90: float | None
    totals: Nutrients
    macro_split: MacroSplit | None
    confidence: float = Field(ge=0, le=1)

class QuestionOption(BaseModel):
    value: str
    label: str
    delta_kcal: float | None = None      # effect on meal total if chosen

class Question(BaseModel):
    id: str
    component_ord: int | None
    kind: Literal["confirm_identity","choose_between","portion_scale","composite_confirm","free_text"]
    prompt: str
    options: list[QuestionOption] = []
    allow_free_text: bool = False
    info_gain: float = 0.0               # expected kcal error reduction / total kcal

class ProvenanceRecord(BaseModel):
    component_ord: int
    nutrient: str
    value: float | None
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
```

**`disclaimer`** is a constant string, never model-generated:

> Estimated nutritional values for informational purposes only. Not medical or dietary advice. Portions are approximated from a photograph and may differ from actual serving sizes.

---

## 3. `POST /v1/analyses`

**Request** — `multipart/form-data`

| Field | Type | Required | Rules |
|---|---|---|---|
| `image` | file | yes | `image/jpeg`, `image/png`, `image/webp`; ≤ 10 MB; min 256 px shortest side |
| `context` | string | no | ≤ 200 chars, e.g. `"home lunch, medium steel plate"` |
| `tier_override` | string | no | `T0|T1|T2` — for evaluation only, ignored in production UI |

**Response** `201 Created`, body `AnalysisResponse`. When `status="needs_clarification"`, `questions` is non-empty and the client must POST answers.

**Example — mixed plate, one low-confidence component**

```json
{
  "analysis_id": "9f2c1b7e4a6d4c1e8b3a2f5d7c9e1a04",
  "status": "needs_clarification",
  "created_at": "2026-11-06T12:41:03.221Z",
  "tier": "T1",
  "image": { "width": 1024, "height": 768, "quality": 0.81, "quality_flags": [] },
  "meal": {
    "n_components": 4,
    "n_matched": 4,
    "matched_mass_pct": 1.0,
    "kcal_p10": 512.0,
    "kcal_p50": 604.0,
    "kcal_p90": 711.5,
    "totals": { "kcal": 604.0, "protein_g": 22.4, "carb_g": 74.1, "fat_g": 24.8, "fibre_g": 7.2 },
    "macro_split": { "protein_pct": 14.8, "carb_pct": 49.1, "fat_pct": 36.1 },
    "confidence": 0.71
  },
  "components": [
    {
      "ord": 0,
      "label": "white rice",
      "display_label": "Steamed rice",
      "bbox_norm": [0.08, 0.22, 0.46, 0.78],
      "food": { "food_id": 12, "name": "Rice, cooked (white, milled)", "source": "IFCT2017", "source_ref": "13-026", "physical_state": "cooked", "is_composite": false },
      "mass_g": 165.0,
      "mass_range": { "low": 138.0, "high": 197.0, "unit": "g" },
      "portion": { "method": "anchor_area_volume", "anchor": "dinner_plate_26cm", "volume_ml": 194.0, "density_g_ml": 0.85, "features": { "area_cm2": 96.2, "heap_k": 0.28, "px_per_cm": 31.4 } },
      "nutrients": { "kcal": 214.5, "protein_g": 4.5, "carb_g": 46.5, "fat_g": 0.5, "fibre_g": 0.7 },
      "nutrition_per_100g": { "kcal": 130.0, "protein_g": 2.7, "carb_g": 28.2, "fat_g": 0.3, "fibre_g": 0.4 },
      "confidence": 0.86,
      "confidence_band": "high",
      "flags": [],
      "match_type": "alias"
    },
    {
      "ord": 3,
      "label": "some curry",
      "display_label": "Curry (unconfirmed)",
      "bbox_norm": [0.62, 0.62, 0.93, 0.90],
      "food": { "food_id": 34, "name": "Mixed vegetable curry", "source": "IFCT2017", "source_ref": "16-112", "physical_state": "gravy", "is_composite": false },
      "mass_g": 92.0,
      "mass_range": { "low": 61.0, "high": 139.0, "unit": "g" },
      "portion": { "method": "anchor_area_volume", "anchor": "dinner_plate_26cm", "volume_ml": 97.0, "density_g_ml": 0.95, "features": { "area_cm2": 41.0, "heap_k": 0.28, "px_per_cm": 31.4 } },
      "nutrients": { "kcal": 101.2, "protein_g": 2.3, "carb_g": 8.1, "fat_g": 6.7, "fibre_g": 2.4 },
      "confidence": 0.48,
      "confidence_band": "low",
      "flags": ["state_converted"],
      "match_type": "semantic"
    }
  ],
  "questions": [
    {
      "id": "q_1",
      "component_ord": 3,
      "kind": "choose_between",
      "prompt": "The side dish is unclear. Which is closest?",
      "options": [
        { "value": "mixed_vegetable_curry", "label": "Mixed vegetable curry", "delta_kcal": 0 },
        { "value": "paneer_curry", "label": "Paneer curry", "delta_kcal": 96 },
        { "value": "dal_fry", "label": "Dal fry", "delta_kcal": -33 }
      ],
      "allow_free_text": true,
      "info_gain": 0.16
    }
  ],
  "limitations": [
    "Portions estimated from a plate-size anchor, not measured on a scale.",
    "One component was matched after converting a raw-state record to cooked."
  ],
  "disclaimer": "Estimated nutritional values for informational purposes only. Not medical or dietary advice. Portions are approximated from a photograph and may differ from actual serving sizes.",
  "kb_version": "2026.11.1",
  "model": "gemini-2.5-flash",
  "latency_ms": 7340
}
```

---

## 4. `POST /v1/analyses/{id}/clarify`

**Request**

```json
{
  "answers": [
    { "question_id": "q_1", "value": "paneer_curry" },
    { "question_id": "q_2", "value": "medium" }
  ],
  "skip_remaining": false
}
```

**Behaviour:** only the affected components are recomputed (graph re-enters at `portion`). Returns a full `AnalysisResponse` with `status` `complete` or `needs_clarification` if a second round is warranted. **Maximum two rounds** — after that the report is emitted with remaining low confidence and `limitations` explaining why.

**Errors:** `409` if the analysis is not in `needs_clarification`; `422` if a `question_id` is unknown or a value is not in the options and the question does not allow free text.

---

## 5. `PATCH /v1/analyses/{id}/components/{ord}`

Manual correction. Any subset of fields:

```json
{ "food_id": 41, "mass_g": 120, "label": "paneer curry" }
```

**Behaviour:** applies the override (`method="user_override"`), recomputes nutrients from the new food/mass, **sets that component's confidence to 1.0**, appends a `feedback` row, and re-emits the response. Corrections are how the system learns: alias additions and calibration data come from this table.

`409` if the component does not exist. `422` if `mass_g` is outside `(0, 3000]`.

---

## 6. Other endpoints

**`GET /v1/foods/search?q=paneer&state=cooked&limit=8`**

```json
{
  "query": "paneer",
  "results": [
    { "food_id": 41, "name": "Paneer, full fat", "category": "dairy", "physical_state": "raw",
      "kcal_per_100g": 296.0, "source": "IFCT2017", "source_ref": "09-014", "score": 0.97 }
  ]
}
```

**`GET /v1/meta`**

```json
{
  "app_version": "0.3.0",
  "provider": "mock",
  "model": "mock-thali-v1",
  "mock_mode": true,
  "kb_version": "2026.11.1",
  "n_foods": 1024,
  "n_dishes": 42,
  "prompt_version": "p1.2.0",
  "features": { "clarification": true, "usda_live": false, "consistency_sampling": true }
}
```

**`GET /healthz`** — `200` with `{ "ok": true, "checks": { "db": "ok", "chroma": "ok", "provider": "mock", "usda_key": "absent" } }`; `503` if `db` or `chroma` fails.

---

## 7. Error format

RFC 9457-style `application/problem+json`:

```json
{
  "type": "https://errors.local/schema-violation",
  "title": "Model response did not match the decomposition schema",
  "status": 502,
  "code": "SCHEMA_VIOLATION",
  "detail": "missing required field 'components[0].bbox_norm' after 2 attempts",
  "analysis_id": "9f2c...",
  "retryable": true
}
```

| Code | HTTP | Retryable | Meaning |
|---|---|---|---|
| `IMAGE_UNREADABLE` | 422 | no | decode failure |
| `IMAGE_TOO_SMALL` | 422 | no | shortest side < 256 px |
| `IMAGE_TOO_LARGE` | 413 | no | > 10 MB |
| `UNSUPPORTED_MEDIA_TYPE` | 415 | no | not jpeg/png/webp |
| `PROVIDER_TIMEOUT` | 504 | yes | VLM did not answer |
| `SCHEMA_VIOLATION` | 502 | yes | model output unparseable after retry |
| `PROVIDER_EXHAUSTED` | 503 | yes | quota/billing |
| `KB_UNAVAILABLE` | 503 | yes | index missing |
| `RATE_LIMITED` | 429 | yes | per-session limit (see §9) |
| `NOT_FOUND` | 404 | no | unknown analysis id |
| `STATE_CONFLICT` | 409 | no | e.g. clarify on a completed analysis |

---

## 8. Behavioural guarantees

| Guarantee | Implementation |
|---|---|
| Idempotent upload by content | identical image bytes within 60 s returns the cached analysis unless `?fresh=1` |
| Deterministic mock mode | same image hash → identical response, byte-for-byte, with `MOCK_MODE=1` |
| No partial JSON | responses always validate against `AnalysisResponse`; failures become `problem+json` |
| Every component number is traceable | `provenance[]` contains a record for each non-null nutrient |
| Nothing is recomputed client-side | UI only formats values from the response |
| Replayable | `GET /v1/analyses/{id}` returns the frozen `report.json` content, not a re-run |

---

## 9. Limits and configuration

| Limit | Default | Env var |
|---|---|---|
| Max upload | 10 MB | `MAX_UPLOAD_MB` |
| Max image pixels after normalisation | 1024 long side | `MAX_IMAGE_SIDE` |
| Analyses per session per hour | 60 | `RATE_LIMIT_HOURLY` |
| Clarification rounds | 2 | `MAX_CLARIFY_ROUNDS` |
| Per-analysis compute budget | tier-driven | — |
| Concurrency | 4 workers | `UVICORN_WORKERS` |

---

## 10. Streamlit ↔ API mapping (so the UI has no logic)

| UI element | Source field |
|---|---|
| Hero thumbnail + quality chip | `image`, `image.quality_flags` |
| Component cards (sorted by mass share) | `components` sorted by `mass_g` desc |
| Confidence badge colour | `confidence_band` |
| Calorie headline + error bar | `meal.kcal_p50` with `kcal_p10/p90` |
| Macro donut | `meal.macro_split` |
| "How do you know?" expander | `provenance`, `limitations` |
| Clarification form | `questions` |
| "Edit" dialogs | `PATCH /components/{ord}` |
| Methodology footer | `GET /v1/meta` |

If a UI requirement cannot be served from these fields, **add a field to the response** — do not compute it in Streamlit.
