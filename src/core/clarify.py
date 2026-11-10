"""Clarification question ranking by expected error reduction."""

from __future__ import annotations


def rank_questions(candidates: list[dict], k: int = 2) -> list[dict]:
    """Sort by info_gain desc, then by component ord; take top-k."""
    ordered = sorted(candidates, key=lambda q: (-q.get("info_gain", 0.0), q.get("component_ord") or 0))
    return ordered[:k]
