"""Confidence fusion + isotonic calibration (pure Python)."""

from __future__ import annotations

WEIGHTS = {
    "s_ident": 0.28,
    "s_retr": 0.20,
    "s_port": 0.18,
    "s_crit": 0.14,
    "s_img": 0.08,
    "s_state": 0.07,
    "s_cover": 0.05,
}


def fuse(signals: dict[str, float]) -> float:
    raw = 0.0
    for k, w in WEIGHTS.items():
        raw += w * float(signals.get(k, 0.0))
    # hard caps
    if not signals.get("matched", True):
        raw = min(raw, 0.25)
    if signals.get("critic_veto"):
        raw = min(raw, 0.40)
    if signals.get("severe_blur"):
        raw = min(raw, 0.55)
    return max(0.0, min(1.0, raw))


def calibrate(raw: float, isotonic_points: list[tuple[float, float]] | None = None) -> float:
    """Piecewise-linear isotonic calibration. Identity if no model fitted."""
    if not isotonic_points:
        return raw
    pts = sorted(isotonic_points)
    if raw <= pts[0][0]:
        return pts[0][1]
    if raw >= pts[-1][0]:
        return pts[-1][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= raw <= x1:
            t = (raw - x0) / (x1 - x0) if x1 != x0 else 0.0
            return y0 + t * (y1 - y0)
    return raw


def band(confidence: float) -> str:
    if confidence >= 0.8:
        return "high"
    if confidence >= 0.5:
        return "medium"
    return "low"
