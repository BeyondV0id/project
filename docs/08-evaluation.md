# 08 — Evaluation Plan

> Without this document the project is a demo. With it, it is a research contribution. Every claim in the final report must map to a row in this plan.

---

## 1. Research questions

| RQ | Question | Where it is answered |
|---|---|---|
| **RQ1** | Does component decomposition improve calorie estimation over whole-dish recognition? | §6.1 baseline A vs. full |
| **RQ2** | Does retrieval grounding reduce error and variance compared to asking the VLM directly? | §6.1 baseline B vs. full |
| **RQ3** | Is the fused confidence score calibrated, and does it identify its own errors? | §5 calibration + selective accuracy |
| **RQ4** | Does selective clarification improve accuracy per question asked? | §6.4 clarification study |
| **RQ5** | Is the adaptive routing worth its complexity in latency and cost? | §6.5 tier ablation |

---

## 2. Metric definitions

### 2.1 Component recognition

| Metric | Definition | Target |
|---|---|---|
| Component precision / recall / F1 | Hungarian matching between predicted and GT components at IoU ≥ 0.5, then label match (exact alias or within the same canonical food group) | F1 ≥ 0.80 |
| Identity top-1 accuracy | matched component's food id equals GT (or an accepted synonym) | ≥ 0.72 |
| Identity top-3 accuracy | GT food in the three displayed candidates | ≥ 0.90 |
| Box quality | mean IoU of matched pairs | ≥ 0.62 |

### 2.2 Portion estimation

| Metric | Definition | Target |
|---|---|---|
| Mass MAE | mean abs error in grams over matched components | ≤ 35 g |
| Mass MAPE | median relative error | ≤ 22 % |
| Mass within ±30 % | % of components | ≥ 70 % |
| Interval coverage | % of GT masses inside the reported 80 % CI | 75–85 % (calibration of the error bar itself) |
| Anchor sensitivity | MAE with anchor vs. without | report both |

### 2.3 Nutrition

| Metric | Definition | Target |
|---|---|---|
| kcal MAE | per meal, vs. weighed ground truth | ≤ 90 kcal |
| kcal MAPE | per meal | ≤ 18 % |
| Macro MAE | protein / carb / fat in g | ≤ 6 g each |
| Within ±20 % | % of meals | ≥ 65 % |
| Rank correlation | Spearman between predicted and true kcal across meals | ≥ 0.85 |

### 2.4 Confidence and calibration

| Metric | Definition | Target |
|---|---|---|
| ECE | 10-bin expected calibration error on test split | ≤ 0.10 |
| Brier score | mean squared error of probability | report |
| Selective accuracy | accuracy on the subset where `confidence ≥ 0.8` | ≥ 0.88 |
| Risk–coverage curve | accuracy vs. fraction of components retained above a confidence threshold | plotted |
| AUROC | raw confidence vs. correctness | ≥ 0.75 |

**Selective accuracy is the headline metric** — "when the system says it is confident, it is right 88 % of the time" is a far stronger claim than raw accuracy.

### 2.5 Interaction and system

| Metric | Definition | Target |
|---|---|---|
| Questions per analysis | mean | ≤ 1.2 |
| Error reduction per question | `(MAE_before − MAE_after) / questions_asked` | report in kcal/question |
| Clarification acceptance | % of users who answer at least one question | report (usability signal) |
| Latency | p50 / p95 end-to-end | ≤ 8 s / ≤ 20 s |
| Cost | USD per analysis, from `llm_call` rows | ≤ $0.01 |
| Crash rate | failed analyses / total | < 2 % |

---

## 3. Dataset construction

**This is the part most teams skip. Do not skip it — it is the main source of marks.**

### 3.1 `gold_v1` — team-collected (primary)

| Property | Plan |
|---|---|
| Size | **150 images / 60 distinct meals**, 3–4 shots per meal (top-down, 45°, slightly further) |
| Dishes | 25 single-item + 35 mixed plates, heavy Indian coverage (thali, biryani, sambar-rice, upma, idli-sambar, chapati-dal-sabzi, poha, curd rice, chicken curry + rice, paneer dishes) |
| Capture | phone camera, indoor daylight + indoor artificial light + one dim restaurant set, to exercise the quality gate |
| **Ground truth masses** | every component weighed on a kitchen scale (±1 g) before plating; recorded in a spreadsheet; plate diameter recorded; a spoon/fork included in 50 % of shots as an anchor |
| Ground truth nutrition | computed by the team from IFCT values × weighed mass (not from any app) |
| Annotation | JSON per image: `[{label, canonical_food, mass_g, bbox, state}]` |
| Splits | 60 / 20 / 20 by **meal**, not by image — otherwise the same plate leaks across splits |
| Storage | `data/gold_v1/images/…`, `data/gold_v1/labels.json` |

The weighing session is also the calibration data for `portion_model` densities and heap factors — one afternoon of work that powers both M5 and the evaluation.

### 3.2 External datasets (secondary, for breadth and for RQ1 comparisons)

| Dataset | Use | Caveat |
|---|---|---|
| **Nutrition5k** (5 006 dishes, RGB-D, kcal + macros + total mass) | portion/nutrition MAE comparison | overhead camera, cafeteria food, no Indian dishes — domain gap must be stated |
| **FoodSeg103** (7 119 images, 103 ingredient classes, segmentation masks) | component segmentation sanity check | masks, not masses |
| **Food-101** | identity only, 101 classes | classification task, no portions; use only to show identity accuracy is not overfit |
| **Indian food image sets on Kaggle** | identity breadth for Indian dishes | licensing must be checked and cited |

We do **not** claim SOTA on these. We use them to show the pipeline generalises and to compare against published numbers where the task matches.

### 3.3 Annotation protocol

1. Two annotators label 20 % overlap; Cohen's κ reported (target ≥ 0.80 on component identity).
2. Disagreements resolved by the third member.
3. Masses come from the scale, never from annotator estimation — this is what makes the ground truth defensible.
4. Any image where the dish is unidentifiable even to a human is **excluded** and the exclusion is reported (no silent filtering).

---

## 4. Baselines

| ID | System | Purpose |
|---|---|---|
| **A** | Whole-dish VLM: "what is this meal and how many calories" (single prompt, no decomposition, no RAG) | the status quo this project critiques |
| **B** | Decomposition + VLM-stated nutrition (no RAG, model guesses numbers from memory) | isolates the value of grounding |
| **C** | Decomposition + RAG + fixed household priors (no scale anchoring) | isolates the value of geometric portion estimation |
| **D** | **Full system** | proposed |
| **E** | Full system + oracle identity (GT labels injected) | upper bound on portion+nurtrition error given perfect recognition |
| **F** | Full system − clarification | isolates RQ4 |

All baselines run on the same `gold_v1` test split, same images, same provider, same prompt budget. Report mean ± 95 % CI (bootstrap, 1 000 resamples).

---

## 5. Ablations

| Ablation | Variant | Expected effect |
|---|---|---|
| Retrieval mode | dense-only / BM25-only / hybrid / hybrid+rerank | hybrid+rerank best; dense-only collapses on regional names |
| State filter | on / off | off returns raw rice (345 kcal/100 g) for cooked rice — large systematic overestimate |
| Reranker | on / off | small accuracy gain, measurable latency cost |
| Consistency sampling | k=1 / k=3 | k=3 improves calibration more than raw accuracy |
| Critic | on / off | improves identity precision, may hurt recall (over-flagging) |
| Composite handling | single-record / recipe decomposition | recipe preserves ingredient transparency |
| Tier routing | always T2 / adaptive | adaptive cuts latency and cost with no accuracy loss on simple plates |

Every ablation row is a table in the report's Results chapter.

---

## 6. Experiments

### 6.1 RQ1 & RQ2 — does the pipeline help?

Run A, B, C, D on the test split. Table: kcal MAE, MAPE, macro MAE, % within ±20 %. Paired bootstrap significance test. Expected narrative: A is cheap but biased on mixed plates; B removes the bias only when the model happens to know the dish; D wins on both accuracy and variance.

### 6.2 RQ3 — calibration

- Reliability diagram (10 bins) for raw vs. calibrated score.
- ECE before/after isotonic regression.
- Risk–coverage curve.
- Scatter: confidence vs. absolute kcal error, with Spearman ρ.

### 6.3 Portion study

- MAE by anchor type (reference object / plate / none).
- MAE by food class (rice vs. gravy vs. bread) — expect gravy worst.
- Interval coverage — if 80 % CI contains the truth only 50 % of the time, the uncertainty model is wrong and must be fixed.

### 6.4 RQ4 — clarification value

Simulated-user protocol: for each low-confidence component, sample the answer from the ground truth with probability `p` (0.9) and a distractor otherwise, 20 repetitions. Measure MAE before/after, questions asked, error reduction per question. Compare against a "ask everything" policy and a "never ask" policy — three points on the accuracy/friction curve.

### 6.5 RQ5 — routing

Per-tier: latency, cost, accuracy, % of test images routed to each tier. Show that T0 images are answered at a fraction of T2 cost with no accuracy loss.

### 6.6 Qualitative / human study (small but valuable)

5–8 volunteers (students, one dietician if available) use the app on 5 meals each. SUS-style questionnaire + one open question. Report: perceived trust, whether the confidence badge changed their behaviour, whether they would use it. Even n=8 with quotes makes a strong Discussion section.

---

## 7. Acceptance criteria (what "done" means)

The project is demo-ready when **all** hold on `gold_v1` test:

- [ ] Component F1 ≥ 0.80
- [ ] kcal MAPE ≤ 18 %
- [ ] kcal MAE ≤ 90 kcal
- [ ] ECE ≤ 0.10
- [ ] Selective accuracy at `conf ≥ 0.8` ≥ 0.88
- [ ] p95 latency ≤ 20 s
- [ ] Cost ≤ $0.01/analysis
- [ ] Zero-crash run over the full test split
- [ ] Full pipeline works with `MOCK_MODE=1` (offline demo)
- [ ] Reproduction script: one command rebuilds index, runs eval, prints the tables

If a target is missed, the report states the achieved number and an error analysis — an honest miss with analysis scores better than a hidden one.

---

## 8. Error taxonomy (code every failure, count them)

| Code | Meaning | Example |
|---|---|---|
| `E-ID-WRONG` | wrong food identity | paneer called tofu |
| `E-ID-MISS` | component missed entirely | hidden chicken under rice |
| `E-ID-SPLIT` | one food split into two entries | dal reported twice |
| `E-PORT-LARGE` | mass overestimated > 50 % | 300 g rice that was 140 g |
| `E-PORT-SMALL` | mass underestimated > 50 % | |
| `E-STATE` | raw/cooked mismatch | raw rice record used |
| `E-COMPOSITE` | composite dish mis-handled | biryani treated as plain rice |
| `E-KB-MISS` | food absent from KB | regional dish |
| `E-RETR-WRONG` | retrieval returned the wrong record | "koora" → "korma" |
| `E-UNIT` | unit/energy conversion bug | kJ read as kcal |
| `E-VLM-SCHEMA` | provider returned invalid JSON | |
| `E-HALLUC` | model invented an item | |

Report a stacked bar of error codes by tier. This table is usually the most-discussed slide in a viva because it shows the team knows exactly *how* the system fails.

---

## 9. Reproducibility

```
python -m app.rag.build_index --kb data/kb/2026.11.1
python -m app.eval.run --dataset gold_v1 --config full --out results/runs/full_$(date +%F)
python -m app.eval.report --runs results/runs/* --format markdown > results/REPORT_TABLES.md
```

Each run records `git_sha`, `kb_version`, `prompt_version`, provider, model, seed, and hardware. Two runs with the same config must produce identical numbers in mock mode and within-variance numbers in live mode (seeds set, temperature pinned where possible).
