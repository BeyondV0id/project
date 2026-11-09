# Methodology — Slide Content

## Slide: Methodology (overview)

**From one meal photo to a nutrition report**

1. **Input** — Meal photo + optional user context (meal type, plate size)
2. **Image Preparation** — Validate, resize, assess quality; reject unusable images early
3. **Perception Agent** — Detect food components and their regions (no calories, no grams)
4. **Food Analysis** — Match each component, retrieve IFCT/USDA per-100 g values, estimate portion
5. **Nutrition Calculation** — Pure Python arithmetic; no AI in the calculation path
6. **Critic Agent** — Check food identity, portion size, and nutritional plausibility
7. **Confidence Calculation** — Weighted reliability score from image quality, match certainty, portion uncertainty, and critic checks
8. **Decision** — Accept → report. Low confidence → ask one targeted question and re-run Food Analysis
9. **Report Generation** — Nutrition values, ranges, sources, and limitations
10. **Diet Recommendation Agent** — General suggestions from validated results and user goals
11. **Persistence** — Store result, provenance, artifacts, and feedback

**Callout:** Confidence is **not a separate AI model**. It is a calculated score that combines four pieces of evidence and is calibrated on data.

---

## Slide: What each stage does and why

| Stage | What it does | Why it matters |
|---|---|---|
| Image Preparation | Checks blur, lighting, resolution | Bad photo → bad result; fail fast |
| Perception Agent | Finds components and regions | A mixed plate is several foods, not one |
| Food Analysis | Matches food, fetches IFCT/USDA, estimates grams | Every number must be traceable to a database row |
| Nutrition Calculation | Scales per-100 g values by mass and sums | Deterministic, unit-tested, reproducible |
| Critic Agent | Checks identity, portion, plausibility | Catches obvious mistakes before the user sees them |
| Confidence Calculation | Combines image, match, portion, critic evidence | Tells the user when to trust the result |
| Clarification | Asks the single most useful question | Cheap fix for the biggest uncertainty |
| Report | Values, ranges, sources, limitations | Honest output, not false precision |
| Recommendation | General dietary suggestions | Uses validated output only, not raw guesses |

---

## One-line flow (for a diagram caption)

Photo → Quality check → Detect components → Match + retrieve + estimate portion → Compute nutrition → Critic check → Confidence score → Clarify if uncertain → Report → Recommend → Store

---

## Speaker notes (30 seconds)

"The system takes one meal photo. It first checks the image, then an AI perception agent lists the food components — but it never gives calories or grams. Each component is matched to IFCT or USDA data and its portion is estimated. Nutrition is then computed in plain Python, checked by a critic agent, and given a confidence score built from image quality, match certainty, portion uncertainty, and critic checks. If confidence is low, the system asks the user one targeted question instead of guessing. Finally it produces the report and stores everything for reproducibility."

---

## Key points to say aloud

- The VLM describes food; it never produces nutrition numbers.
- All numbers come from the knowledge base via deterministic Python.
- Low confidence triggers a question, not a silent guess.
- Every report stores its sources and versions, so it can be reproduced.
