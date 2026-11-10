"""LangGraph wiring with a plain-Python fallback (no langgraph required)."""

from __future__ import annotations

try:
    import langgraph  # noqa: F401
    _HAS_LG = True
except Exception:  # pragma: no cover
    _HAS_LG = False


def run_pipeline(state: dict) -> dict:
    """Run the agent sequence. Plain-Python fallback of the LangGraph graph."""
    from src.agents.nodes.router import route
    from src.agents.nodes.perception import perceive
    from src.agents.nodes.retrieval import retrieve
    from src.agents.nodes.portion import estimate_portions
    from src.agents.nodes.calculator import calculate
    from src.agents.nodes.critic import critique
    from src.agents.nodes.clarifier import clarify

    state = {**state, **perceive(state)}
    state = {**state, **route(state)}
    state = {**state, **retrieve(state)}
    state = {**state, **estimate_portions(state)}
    state = {**state, **calculate(state)}
    state = {**state, **critique(state)}

    for c in state.get("components", []):
        m = (state.get("matches") or {}).get(str(c["ord"]))
        if m:
            c["food"] = {"food_id": m["food_id"], "name": m["name"], "source": m["source"],
                         "source_ref": m["source_ref"], "physical_state": m["physical_state"],
                         "is_composite": False}
            c["match_type"] = "alias"
            c["confidence"] = 0.86
        else:
            c["food"] = None
            c["match_type"] = "none"
            c["confidence"] = 0.3
        c["display_label"] = c.get("display_label", c["label"].title())
        c["confidence_band"] = "high" if c["confidence"] >= 0.8 else ("medium" if c["confidence"] >= 0.5 else "low")
        c.setdefault("flags", [])
        c.setdefault("bbox_norm", (0, 0, 1, 1))

    conf = (sum(c.get("confidence", 0) for c in state.get("components", [])) /
            max(len(state.get("components", [])), 1))
    state["confidence"] = conf
    if conf < 0.55 and state.get("round", 0) < 2:
        state = {**state, **clarify(state)}
        state["status"] = "needs_clarification"
    else:
        state["status"] = "complete"
    return state
