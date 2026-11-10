def critique(state):
    issues = []
    for c in state.get("components", []):
        m = (state.get("portions") or {}).get(str(c["ord"]), {}).get("mass_g")
        if m is not None and (m <= 0 or m > 2000):
            issues.append({"component": c["ord"], "issue": "implausible_mass"})
    return {"issues": issues}
