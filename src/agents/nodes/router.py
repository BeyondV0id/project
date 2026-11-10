def route(state):
    q = state.get("quality", 0.8)
    n = len(state.get("components", [])) or 1
    if q >= 0.75 and n <= 1:
        tier = "T0"
    elif q < 0.45 or n > 8:
        tier = "T2"
    else:
        tier = "T1"
    return {"tier": tier}
