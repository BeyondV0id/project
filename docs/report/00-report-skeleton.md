# 10 — Project Report Skeleton

Standard B.Tech project report structure (GVPCE / JNTU-style). Page counts assume a **60–70 page** report excluding appendices; adjust to your department's template. Each section lists what must go in it and which artefact from this repo supplies the content.

> Rule for the whole report: **every claim ends in a number, a figure, or a citation.** "The system is accurate" is not a sentence. "The system achieves 13.8 % MAPE on 30 held-out mixed plates (Table 6.4)" is.

> The final PowerPoint deck is governed separately by the department mandate recorded in [05 — Presentation Specification](05-presentation-spec.md). That file lists the mandatory slides, the bullets-only rule, and which section here supplies each slide.

---

## Front matter

| Item | Content |
|---|---|
| Title page | Project title, team names + roll numbers, guide, department, college, academic year |
| Certificate | Guide + HOD signature block |
| Declaration | Standard, signed by all four members |
| Acknowledgement | Guide, Centre for Innovation, department |
| Abstract | 250–300 words: problem, approach, key result numbers, contribution. **Write this last.** |
| Table of contents | Auto-generated |
| List of figures / tables | Auto-generated |
| Abbreviations | VLM, RAG, RRF, IFCT, FDC, ECE, MAPE, MAE, IoU, CI |

---

## Chapter 1 — Introduction (5–6 pages)

1.1 Background — dietary self-tracking, why portion accuracy matters, the "one dish, one calorie number" failure.
1.2 Motivation — Indian mixed meals; the error is multiplicative (identity × mass).
1.3 Problem statement — verbatim from the project brief; then **operationalise** it into the four error sources from [01 §1](01-architecture.md#1-problem-framing).
1.4 Objectives — the five objectives, each rewritten as a measurable goal (map to RQ1–RQ5).
1.5 Scope and limitations of scope — the non-goals list; be explicit that this is not a medical device.
1.6 Organisation of the report.

**Figure 1.1** — the motivating example: one app's single-dish 550 kcal vs. the decomposed reality (rice 215 + dal 140 + chapati 210 + curry 100).
**Table 1.1** — objectives → deliverables → evaluation metric.

---

## Chapter 2 — Literature Survey (6–8 pages)

Group by theme, not chronologically. End each subsection with *what is missing*, so the gap analysis writes itself.

2.1 Food recognition — Food-101 (Bossard et al., 2014), UEC Food-256, FoodSeg103 (Wu et al., 2021), deep CNN → ViT progression.
2.2 Nutritional estimation from images — Nutrition5k (Thames et al., 2021), Im2Calories (Meyers et al., 2015), portion estimation literature, why depth/RGB-D helps and why phones lack it.
2.3 Multimodal LLMs for food — GPT-4V/Gemini/LLaVA-based dietary assessment studies; documented overconfidence; hallucinated nutrient values.
2.4 Retrieval-augmented generation — Lewis et al. 2020; RAG in the biomedical/culinary domain; hybrid retrieval (BM25 + dense, RRF — Cormack et al. 2009).
2.5 Confidence calibration — Guo et al. 2017 (on calibration), isotonic regression, selective prediction (Geifman & El-Yaniv 2017), active learning / value-of-information for question selection.
2.6 Indian food composition resources — IFCT 2017 (Longvah et al., NIN Hyderabad), Indian food datasets.
2.7 **Gap analysis** — Table 2.1 comparing 6–8 prior systems against: component-level output, portion estimation, grounded nutrition, calibrated confidence, clarification, Indian coverage. The last row is this project, all ✓. This table is the justification for the entire project.

**Table 2.1** is the single most important table in the report. Take a full page on it if needed.

---

## Chapter 3 — System Requirements and Design (8–10 pages)

3.1 Functional requirements — FR1…FR12, each with a priority (Must/Should/Could). Use the [Software Requirements Specification](../11-software-requirements-specification.md#4-functional-requirements) as the source table.
3.2 Non-functional requirements — latency, cost, offline capability, privacy, accessibility. Use the [SRS NFR table](../11-software-requirements-specification.md#5-non-functional-requirements) and update only the measured results at submission time.
3.3 Use-case diagram + 3 use-case descriptions (analyse meal, answer clarification, correct a component).
3.4 Architecture — reproduce the C4 diagrams from [01](01-architecture.md), explain the layers and the *reason* for each boundary.
3.5 The three axes of adaptivity — the table from [01 §4](01-architecture.md#4-what-adaptive-means-here). This is where the title is justified.
3.6 Data model — ER diagram + key tables from [04](04-data-model.md).
3.7 API contract — endpoint table + one annotated request/response.
3.8 Design decisions — the ADR table from [01 §11](01-architecture.md#11-architecture-decision-records), with the rejected alternatives. **Include what you rejected and why** — it demonstrates engineering judgement.

**Figures:** context diagram, container diagram, sequence diagram, ER diagram, use-case diagram.
**Tables:** FR/NFR tables, ADR table.

---

## Chapter 4 — Methodology (10–12 pages) ← the core chapter

4.1 Pipeline overview — the numbered flow, with one paragraph per stage.
4.2 **Component decomposition** — prompt design, JSON schema, why the schema has no nutrient fields, post-processing rules, self-consistency.
4.3 **Food matching and the dual-index RAG** — the two collections, the query pipeline, RRF, reranking, thresholds, state filtering (with the raw-vs-cooked 345 vs 130 kcal example).
4.4 **Portion estimation** — the full geometric derivation: anchor → px/cm → area → heap volume → density → mass → log-normal CI. Include the equations, the density table, and the household-measure fallback. **This is the most technical and most examinable section — write it carefully.**
4.5 **Nutrition computation** — scaling, aggregation, Atwater fallback, None-propagation rules, unit-safety checklist.
4.6 **Confidence model** — the 7 features, the fusion equation, the overrides, isotonic calibration, meal-level aggregation, Monte-Carlo propagation.
4.7 **Clarification policy** — eligibility triggers, the `IG` equation, templates, round budget.
4.8 **Multi-agent orchestration** — the agent roster, the LangGraph state, the graph diagram, retry/degradation policy.
4.9 Algorithms — numbered pseudocode blocks for: `estimate_portion`, `hybrid_retrieve`, `fuse_confidence`, `rank_questions`.

**Figures:** pipeline diagram, RAG query flowchart, portion geometry diagram (labelled, with the plate anchor), LangGraph diagram, confidence fusion diagram.
**Tables:** density/heap constants, prompt-version table, thresholds table.

---

## Chapter 5 — Implementation (8–10 pages)

5.1 Technology stack — the table from [09 §1](09-engineering-plan.md#1-stack), with a one-line justification per row.
5.2 Repository structure — the tree, annotated.
5.3 Module walkthrough — 1 short subsection per module M1–M11, each with its public interface and a 10–20 line code excerpt. Show real code, not paraphrase.
5.4 The mock provider — why offline-first mattered, how determinism is achieved (hash-keyed fixtures).
5.5 Knowledge-base construction — the transcription protocol, the validation rules, the index build.
5.6 Streamlit UI — screenshots with callouts; the "no logic in the UI" rule.
5.7 Testing — the unit-test matrix from [02 §15](02-modules.md#15-unit-test-obligations-definition-of-done-per-module), coverage number, CI configuration.
5.8 Deployment / how to run — the commands from the README, verified on a fresh machine.

**Figures:** code screenshots or formatted listings, UI screenshots, CI badge.

---

## Chapter 6 — Results and Discussion (10–12 pages)

**This chapter decides the grade. Do not pad it with screenshots.**

6.1 Experimental setup — dataset composition, splits, hardware, provider/model, seeds, cost.
6.2 Dataset statistics — dish distribution, component count histogram, mass distribution, lighting conditions.
6.3 Component recognition results — Table: precision/recall/F1, identity top-1/top-3, box IoU; confusion pairs for the top 5 errors.
6.4 Portion estimation results — MAE/MAPE overall, **broken down by anchor type and food class**; interval-coverage plot.
6.5 Nutrition results — kcal MAE/MAPE, macro MAE, % within ±20 %, Spearman ρ; scatter predicted vs. true with the identity line.
6.6 **Baseline comparison (RQ1, RQ2)** — the A/B/C/D/E/F table with 95 % CIs and paired-test p-values. This is the money table.
6.7 **Calibration (RQ3)** — reliability diagram (raw vs. calibrated), ECE, Brier, risk–coverage curve, selective accuracy.
6.8 **Clarification study (RQ4)** — MAE before/after, questions asked, error reduction per question, three-policy comparison curve.
6.9 **Routing (RQ5)** — per-tier latency/cost/accuracy and tier distribution.
6.10 Ablation summary — one table, one sentence of interpretation per row.
6.11 Error analysis — the taxonomy table with counts and a stacked bar by tier; 3–4 annotated failure images with the actual cause and what would fix it.
6.12 Discussion — what worked, what did not, why, and how it compares to published numbers (with the domain-gap caveat for Nutrition5k).
6.13 Threats to validity — small n, single cuisine, single annotator pair, lighting, phone-only, no clinical validation.

**Every table must state n.** Every metric must have a CI. Every comparison must be paired on the same images.

---

## Chapter 7 — Conclusion and Future Scope (3–4 pages)

7.1 Summary of contributions — 4 bullets, each with its headline number.
7.2 Objectives vs. achievements — a table: objective, target, achieved, verdict. **Be honest about misses and explain them.**
7.3 Limitations — technical, data, and scope.
7.4 Future scope — depth sensing / monocular depth for heap height, 3D reconstruction, multi-image consistency, barcode + menu integration, longitudinal tracking, Hindi/Telugu voice input, dietician-in-the-loop validation, on-device deployment.
7.5 Closing statement — the one-paragraph "what this project proves".

---

## References

IEEE style, ≥ 30 entries. Must include: IFCT 2017, USDA FDC, Food-101, FoodSeg103, Nutrition5k, Im2Calories, RAG (Lewis), RRF (Cormack), calibration (Guo), selective prediction (Geifman), bge embeddings, sentence-transformers, LangGraph, FastAPI, Streamlit, ChromaDB, and 3–5 recent multimodal-LLM-for-diet papers.

Cite the **dataset licences** explicitly. Cite the IFCT page numbers for transcribed values.

---

## Appendices

| Appendix | Content |
|---|---|
| A | Full prompt texts + JSON schemas (from [07](07-prompts.md)) |
| B | Complete database DDL (from [04](04-data-model.md)) |
| C | IFCT transcription sheet with page references |
| D | Weighing-session log (dish, component, scale reading, photo id) |
| E | Density / heap-factor calibration table |
| F | API reference (OpenAPI export) |
| G | Extended results — every eval run, per-image predictions |
| H | User-study questionnaire and anonymised responses |
| I | Source code listing (or a repository link + commit SHA) |

---

## Figures and tables inventory (checklist)

**Figures (≈ 22)**
pipeline · C4 context · C4 container · sequence · ER · use-case · RAG flowchart · portion geometry · LangGraph graph · confidence fusion · reliability diagram · risk–coverage · predicted-vs-true scatter · interval coverage · error stacked bar · tier distribution · UI screenshots ×4 · example failure cases ×3

**Tables (≈ 20)**
objectives→metrics · literature comparison · FR · NFR · ADR · density constants · thresholds · prompt versions · unit-test matrix · dataset stats · recognition results · portion by anchor · portion by class · nutrition results · baseline comparison · calibration metrics · clarification study · tier ablation · ablation summary · error taxonomy · objectives vs. achievements

---

## Writing schedule

| Week | Draft |
|---|---|
| 9 | Chapters 1–3 (can be written before results) |
| 10 | Chapter 4 (methodology — write while implementing; it is easiest then) |
| 11 | Chapter 5 + 6 (results land here) |
| 12 | Chapter 7, abstract, front matter, appendices, proofread, format to template |

**Tip:** keep a `results/REPORT_TABLES.md` generated by `app.eval.report` and paste tables from it directly into Chapter 6. Never retype a number — transcription errors in a results chapter are the fastest way to lose credibility.
