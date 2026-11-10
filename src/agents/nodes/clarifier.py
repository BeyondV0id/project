"""Clarifier node: generate targeted questions."""

from __future__ import annotations

from src.core.clarify import rank_questions


def clarify(state):
    candidates = []
    for c in state.get("components", []):
        if (c.get("confidence") or 1.0) < 0.7:
            candidates.append({
                "id": f"q_{c['ord']}",
                "component_ord": c["ord"],
                "kind": "confirm_identity",
                "prompt": f"Is the {c['label']} correct?",
                "options": [],
                "allow_free_text": True,
                "info_gain": 0.1,
            })
    qs = rank_questions(candidates, k=2)
    return {"questions": qs}
