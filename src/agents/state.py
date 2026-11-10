"""LangGraph state definition."""

from __future__ import annotations

from typing import Any, TypedDict


class AnalysisState(TypedDict, total=False):
    analysis_id: str
    image_path: str
    context: str | None
    tier: str
    quality: float
    components: list[dict[str, Any]]
    matches: dict[str, dict[str, Any]]
    portions: dict[str, dict[str, Any]]
    nutrients: dict[str, dict[str, float | None]]
    issues: list[dict[str, Any]]
    confidence: float
    questions: list[dict[str, Any]]
    answers: dict[str, str]
    status: str
    round: int
