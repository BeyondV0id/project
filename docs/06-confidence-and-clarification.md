# 06 — Confidence, Calibration and Clarification

This document is the academic core of the project. Most food-AI demos output a number with no error bar; the contribution here is a **measured**, **calibrated** confidence that drives a **selective** interaction policy.

---

## 1. Why not just ask the model

VLMs are systematically overconfident on fine-grained food labels, and their self-reported confidence is weakly correlated with correctness (well documented in the calibration literature). If we display `0.9` because the model said so, we are manufacturing trust we have not earned. So:

> **Principle P3.** Confidence is a *fused, calibrated* function of observable evidence, validated on a held-out set, reported with ECE.

---

## 2. Features

Per component `i`:

| Symbol | Feature | Source | Range | Available at |
|---|---|---|---|---|
| `s_ident` | Identity agreement | self-consistency across k samples (T2) / crop verifier agreement (T1) / 0.72 prior (T0) | 0–1 | always |
| `s_retr` | Retrieval margin | reranked top-1 minus top-2, normalised | 0–1 | always |
| `s_port` | Portion plausibility | how close the estimate sits to class prior & anchor expectation | 0–1 | always |
| `s_crit` | Critic verdict | 1.0 pass / 0.5 warning / 0.0 veto, averaged over applicable checks | 0–1 | always |
| `s_img` | Image quality | M1 `quality` | 0–1 | always |
| `s_state` | State/record penalty | 1.0 exact state match, 0.7 conversion applied, 0.5 composite recipe | 0–1 | always |
| `s_cover` | Component visibility | `1 − occlusion` × bbox-area share sanity | 0–1 | T1/T2 |

**`s_port` definition** (the one that matters most):

```
s_port = exp( -|ln(m_hat / m_prior)| / 1.2 )     when a class prior exists
       = 0.5                                     when no anchor at all
```

with `m_prior` = class-typical mass (rice 150 g, chapati 45 g, dal 120 g, gravy 100 g). A 2× deviation costs ~0.44, a 4× deviation ~0.16. This is the term that catches "the model said 12 g of rice".

---

## 3. Fusion

Raw score (linear in log-odds space is overkill for 7 features; a weighted sum is transparent and easy to defend in a viva, and we validate that it beats the alternatives):

```
raw_i = 0.28·s_ident + 0.20·s_retr + 0.18·s_port
      + 0.14·s_crit  + 0.08·s_img  + 0.07·s_state + 0.05·s_cover
```

Weights are **fit**, not guessed: logistic regression on the dev split (features → "component identity *and* mass within ±25 %" as the binary target), then rounded to two decimals for the report table, then isotonic-calibrated. The report shows both the fitted weights and the hand-set prior weights — that's an honest ablation.

**Hard overrides** (applied before calibration, because some failures must never be shown as confident):

| Condition | Cap on `raw` |
|---|---|
| `matched=False` | 0.25 |
| bbox area < 0.3 % of image | 0.45 |
| `flags` contains `composite_recipe` and mass > 400 g | 0.60 |
| critic veto on identity | 0.40 |
| image quality < 0.35 | 0.55 |

---

## 4. Calibration

1. Build the dev set: ≥ 120 components with ground-truth identity and weighed mass (see [08](08-evaluation.md)).
2. Label each prediction `y = 1` if (identity correct) **and** (|mass error| ≤ 25 %), else `0`.
3. Fit **isotonic regression** (`sklearn.isotonic.IsotonicRegression`, `out_of_bounds="clip"`) on `(raw_i, y_i)`.
4. Persist to `calibration_model` with `ece` and the sample count; `is_active=1` for the newest accepted model.
5. Report a **reliability diagram** and **ECE** on the *test* split (never the dev split used for fitting).

```
ECE = Σ_b (n_b / N) · | acc(b) − conf(b) |
```

Target: **ECE ≤ 0.10**. Also report Brier score and AUC of the raw score as a sanity check that the features carry signal at all.

**Closing the loop:** every user correction (PATCH endpoint) produces a new `(raw, y=0)` sample. Recalibration is a documented, versioned job (`python -m app.confidence.recalibrate`), not silent learning.

---

## 5. Meal-level confidence

Mass-weighted, discounted by coverage:

```
coverage = Σ_{i matched} m_i / Σ_i m_i
w_i      = m_i / Σ_{i matched} m_i
conf_meal = coverage^0.5 · Σ_i w_i · c_i
```

Rationale: a meal that is 80 % matched but has one unmatched 20 % component should not read "0.9". The `coverage^0.5` term is a soft, concave penalty — it hurts, but does not zero out a mostly-correct plate.

Bands for the UI:

| Band | Range | Wording |
|---|---|---|
| high | ≥ 0.80 | "Confident estimate" |
| medium | 0.55 – 0.80 | "Approximate — check the parts marked amber" |
| low | < 0.55 | "Rough estimate — please confirm the highlighted items" |

---

## 6. Uncertainty propagation (the error bar)

Portion error is multiplicative and roughly log-normal, so propagate by Monte Carlo rather than Gaussian error bars:

```python
def propagate(components, n=2000, rng=default_rng(7)):
    totals = []
    for _ in range(n):
        kcal = 0.0
        for c in components:
            if c.mass_g is None or c.nutrients.kcal is None:
                continue
            m = c.mass_g * rng.lognormal(mean=0.0, sigma=c.sigma_log)   # sigma_log from M5
            kcal += c.nutrients.kcal * (m / c.mass_g)
        totals.append(kcal)
    p10, p50, p90 = np.percentile(totals, [10, 50, 90])
    return p10, p50, p90
```

- `p50` is displayed as **the** number; `p10/p90` as the whisker.
- Fixed seed → reproducible reports (important for a live demo).
- Unmatched components contribute their *prior* kcal with a wide σ (0.6) so they are visible as uncertainty, not silently dropped. Alternative: exclude and show "up to +N kcal unaccounted". Prefer the latter for honesty — the UI shows a distinct "unaccounted mass" row.

---

## 7. When to ask a question

Asking everything destroys the experience; asking nothing hides error. The policy is an explicit expected-value rule.

### 7.1 Trigger conditions

A question is *eligible* if any holds:

| Trigger | Eligibility rule |
|---|---|
| Ambiguous identity | top-2 rerank scores within 0.05 **and** their kcal differ by > 8 % of meal total |
| Low identity confidence | `c_i < 0.60` **and** mass share > 8 % |
| Wide portion interval | `(ci_high − ci_low)/mass > 0.9` **and** mass share > 10 % |
| Unmatched component | `matched=False` **and** mass share > 5 % |
| Composite ambiguity | `is_composite` dish with no separable components detected |
| Structural inconsistency | component count mismatch by > 2, or mass balance fails |

### 7.2 Ranking by expected error reduction

For candidate question `q` with option set `O`:

```
IG(q) = Σ_{o ∈ O} p(o) · |Δkcal(o)| / max(total_kcal, 1)
```

- `p(o)` — option probability: from the softmax of the retrieval scores for `choose_between`; from a fixed prior (0.5/0.5) for `confirm_identity`; from the CI mass distribution for `portion_scale`.
- `Δkcal(o)` — change in meal total if the user picks `o` instead of the current best guess. For identity questions this is `|kcal(alt) − kcal(current)|` at the same mass. For portion questions it is the mass delta × per-gram kcal.

Ask the **top 2 by `IG`**, never more, and never a question with `IG < 0.02` (it would change nothing). Store `info_gain` on the `clarification` row so the report can plot "questions asked vs. error reduced" — that is the evaluation hook that proves the policy is worth its friction.

### 7.3 Question templates

| Kind | Template | Options |
|---|---|---|
| `confirm_identity` | "Is this **{top1}** or **{top2}**?" | two foods + "neither" (free text) |
| `choose_between` | "The **{position}** item looks like one of these. Which is closest?" | top-3 by score, each with `delta_kcal` |
| `portion_scale` | "How much {food} is on the plate?" | quarter / half / full katori, plus "bigger than shown" |
| `composite_confirm` | "Is this one dish (**{dish}**) or separate items?" | one dish / separate |
| `free_text` | "What is this item? (e.g. *pappu*, *koora*, *paneer*)" | free text, matched live via `/v1/foods/search` |

Every option shows its calorie consequence (`delta_kcal`) — a small detail that turns a survey into a transparent decision, and demos very well.

### 7.4 Round budget

- Max **2 rounds**.
- Round 2 is allowed only if the best remaining `IG > 0.05`; otherwise stop.
- On skip: emit the report with `status="complete"` (never block the user), append to `limitations` — "You skipped 1 of 2 clarifications; the dish at bottom-right may be off by ±40 kcal."

---

## 8. Thresholds (single source of truth)

```python
# app/core/confidence.py
TAU_ACCEPT        = 0.60   # below → eligible for clarification
TAU_ASK           = 0.60
TAU_HIGH_BAND     = 0.80
TAU_MEDIUM_BAND   = 0.55
TAU_IG_MIN        = 0.02   # never ask a question below this
TAU_IG_ROUND2     = 0.05
MASS_SHARE_MIN    = 0.08
PORTION_REL_WIDTH = 0.90   # (hi-lo)/mass
MAX_ROUNDS        = 2
```

These constants live in one file and are imported everywhere — no magic numbers in the graph, the UI or the tests.

---

## 9. What the user sees

```
┌───────────────────────────────────────────────────────────┐
│  ~604 kcal          likely range 512 – 712               │
│  Confidence: MEDIUM (0.71)        ⓘ how this is computed │
├───────────────────────────────────────────────────────────┤
│  Steamed rice          165 g   215 kcal   ●●● high       │
│  Toor dal               120 g   140 kcal  ●●● high       │
│  Chapati (2)             90 g   210 kcal  ●●● high       │
│  Curry — unconfirmed     92 g   101 kcal  ●○○ low  [fix] │
├───────────────────────────────────────────────────────────┤
│  Protein 22 g · Carbs 74 g · Fat 25 g · Fibre 7 g        │
│  Sources: IFCT 2017 (3), USDA FDC (1)                    │
│  ⚠ Portions estimated from plate size, not weighed.      │
└───────────────────────────────────────────────────────────┘
```

Design rules:

1. The point estimate is never shown without its range.
2. Low-confidence components are visually *and* textually marked — never colour alone (accessibility).
3. The provenance affordance is one click away, always.
4. The disclaimer is always visible, not buried.
5. No green "healthy/unhealthy" verdict. The system reports numbers; it does not moralise about food.

---

## 10. Failure modes we explicitly accept and disclose

| Failure | Why it happens | Disclosure |
|---|---|---|
| Hidden layer under visible food (biryani chicken) | 2D image, no depth | `occlusion` feature → confidence cap; `limitations` entry |
| Oil/ghee quantity | visually invisible | default 5 g per fried item, flagged `assumed_oil` |
| Very small items (pickle, chutney) | area below anchor precision | `tiny` prior, capped confidence |
| Unfamiliar regional dish | not in KB, retrieval fail | `free_text` question → user supplies name |
| Plate size unknown | no reference object | `household_prior` method, wider interval, explicit anchor=`none` |

Writing these down is not weakness — it is what separates an engineering project from a demo.
