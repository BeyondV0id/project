# 11 — Software Requirements Specification

**System:** Adaptive Food Recognition and Nutritional Estimation Using Multimodal AI  
**Version:** 1.0  
**Status:** Baseline for Phase 2 implementation  
**Date:** 2026-11-08

## 1. Purpose and scope

This specification defines what the system shall deliver and how its success will be judged. It consolidates the binding architecture, API, data, confidence, evaluation, and engineering documents into a Chapter 3-ready requirements baseline.

The system accepts **one photograph of a meal** and returns a component-level nutritional estimate. It identifies visible food components, estimates their portions, retrieves nutrient values from an Indian-first knowledge base, calculates nutrition deterministically, and communicates uncertainty through calibrated confidence and targeted clarification.

The product is an informational estimation tool. It is not a medical device, diet prescription system, meal-tracking platform, or general-purpose image-recognition service.

## 2. Requirement conventions

The words **shall**, **must**, and **must not** are mandatory. Priorities use MoSCoW:

| Priority | Meaning |
|---|---|
| Must | Required for the planned demo and the project's central research claim. |
| Should | Required for a robust, usable implementation; may be staged after the walking skeleton. |
| Could | Useful but deferrable without invalidating the project claim. |

Each requirement has a verification method: **Test** (automated test), **Inspection** (code/API/document review), **Demonstration** (observed end-to-end behaviour), or **Analysis** (measured evaluation result).

## 3. Stakeholders and users

| Stakeholder | Need from the system |
|---|---|
| End user | A transparent estimate of a photographed meal, including component masses, nutrients, uncertainty, and limitations. |
| Project team | An offline-capable system with separable modules, repeatable experiments, and diagnosable failures. |
| Project evaluator | Evidence that nutrition is grounded in an auditable source rather than invented by a model. |
| Guide / institution | A safe, privacy-conscious educational prototype that does not make clinical claims. |

## 4. Functional requirements

| ID | Requirement | Priority | Acceptance criterion / verification |
|---|---|---|---|
| FR-01 | The system shall accept one meal image in JPEG, PNG, or WebP format, plus optional textual context. It shall reject unreadable, unsupported, oversized (>10 MB), or undersized (<256 px shortest side) inputs with a structured error. | Must | Invalid-input API tests return the specified `application/problem+json` error; valid upload creates an analysis. **Test** |
| FR-02 | The system shall assess image quality and decompose the visible meal into discrete components. For every component it shall produce a label, normalised bounding region, physical state, and relative-size information. | Must | A valid `AnalysisResponse` includes image-quality information and component results for a fixture meal. **Test / Demonstration** |
| FR-03 | The perception provider shall never generate calories, grams, or nutrient values. The system shall route work through T0, T1, or T2 according to image/scene complexity so simple images do not incur unnecessary model calls. | Must | Prompt-schema inspection contains no numeric nutrition or mass fields; routing unit tests cover the three tiers. **Inspection / Test** |
| FR-04 | The system shall match every component against the local IFCT 2017 + USDA knowledge base using aliases and hybrid retrieval. Retrieval shall filter candidates by `physical_state`; a match scoring below 0.55 shall not be accepted and shall proceed to USDA fallback or remain unmatched. | Must | Retrieval tests prove cooked food does not select an incompatible raw record; a <0.55 fixture produces `matched=False` when fallback fails. **Test** |
| FR-05 | The system shall estimate a mass in grams and a mass interval for each matched component using the best available evidence: scale-anchor geometry and density first, then a documented household-measure fallback. | Must | Portion fixtures return a positive mass and ordered gram interval; the response identifies the method and active limitations. **Test** |
| FR-06 | The system shall compute per-component and meal-level energy and nutrients in pure Python from retrieved per-100 g values and estimated mass. It shall convert IFCT energy in kJ to kcal by dividing by 4.184 and shall preserve an unreported nutrient as `null`, never as zero. | Must | Hand-worked nutrition tests, including kJ conversion and all-null aggregation, pass without an LLM dependency. **Test** |
| FR-07 | The system shall calculate calibrated component and meal confidence from measurable pipeline signals and show a confidence band with every reported component. | Must | A response contains confidence values/bands; calibration is evaluated against the ECE target in NFR-02. **Test / Analysis** |
| FR-08 | When a significant uncertainty is likely to change the result, the system shall ask at most two high-value clarification questions per round and no more than two rounds. Skipping questions shall still return a report with disclosed limitations. | Must | Clarification integration tests reprocess only affected components, enforce the two-round limit, and return a complete report after skip. **Test / Demonstration** |
| FR-09 | The system shall return a validated, complete `AnalysisResponse` containing component results, meal totals and intervals, confidence, provenance, limitations, and a fixed non-medical disclaimer. The user interface shall display only values supplied by this response. | Must | Contract tests validate every successful response against `AnalysisResponse`; UI inspection finds no client-side nutrient calculation. **Test / Inspection** |
| FR-10 | The system shall let a user correct a component's food identity and/or mass, recompute the affected nutrition deterministically, record feedback, and allow knowledge-base search to support the correction. | Should | `PATCH /v1/analyses/{id}/components/{ord}` recomputes the response and marks the override; food search returns state-labelled candidates. **Test / Demonstration** |
| FR-11 | The system shall persist reproducibility metadata (`provider`, `model`, `prompt_version`, `kb_version`, and `compute_version`) and a frozen report for each analysis. It shall replay stored reports without rerunning a provider and shall delete an analysis and its artifacts on request. | Must | Replay returns the stored report; deletion test confirms database/artifact removal; stored record inspection verifies all version fields. **Test** |
| FR-12 | The system shall expose health and configuration metadata for diagnostics and evaluation, and shall return failures exclusively as RFC 9457-style `application/problem+json`, never partial successful JSON. | Should | `/healthz` and `/v1/meta` return their contract fields; provider/schema failure tests return a problem response. **Test** |

## 5. Non-functional requirements

| ID | Requirement | Priority | Measure / acceptance criterion | Verification |
|---|---|---|---|---|
| NFR-01 | **Safety and scope.** The system shall present estimates for informational purposes only, with no diagnosis, prescription, target-calorie gamification, or moralising food labels. | Must | Every report and UI footer show the fixed disclaimer; scope review finds no medical advice flow. | Inspection / Demonstration |
| NFR-02 | **Accuracy and calibration.** On the held-out `gold_v1` test set, the system shall achieve component F1 >= 0.80, kcal MAPE <= 18%, kcal MAE <= 90 kcal, ECE <= 0.10, and selective accuracy at confidence >= 0.8 of >= 0.88. | Must | Evaluation report states every metric, sample size, and confidence interval. | Analysis |
| NFR-03 | **Performance and cost.** For T1 analyses, the system shall target p50 latency <= 8 s and p95 <= 20 s. Cost shall not exceed $0.01 per analysis (and target <= $0.005 for T0/T1). | Must | Per-analysis latency and provider-cost telemetry; full evaluation summary. | Analysis |
| NFR-04 | **Offline availability.** `MOCK_MODE=1` shall be the default and shall execute the complete pipeline without network access or a VLM API key. The same image bytes shall produce the same mock response. | Must | Offline smoke/integration test passes; repeated hash-keyed fixture result is byte-for-byte identical. | Test |
| NFR-05 | **Grounding and integrity.** Every non-null displayed nutrient shall be traceable to its food record and source reference. Nutrition arithmetic shall have no LLM in its execution path. | Must | `provenance[]` is complete for displayed values; dependency/code inspection and unit tests prove pure arithmetic. | Test / Inspection |
| NFR-06 | **Privacy.** Images and raw provider outputs shall remain in local storage by default, have a 30-day default retention period, be clearly disclosed when sent to a configured provider, and be removable by the user. | Must | Retention and deletion tests; UI/setting inspection. | Test / Inspection |
| NFR-07 | **Reliability.** The full `gold_v1` test run shall complete with zero crashes. External dependency failures shall degrade safely to mock/local paths or return an actionable problem response. | Must | Zero-crash evaluation run and fault-injection integration tests. | Analysis / Test |
| NFR-08 | **Usability and accessibility.** The report shall communicate uncertainty as ranges and confidence labels, expose provenance and limitations, and provide usable text labels and keyboard-operable controls without relying on colour alone. | Should | Five representative report/clarification flows are manually checked using keyboard navigation and non-colour cues. | Demonstration |
| NFR-09 | **Maintainability and reproducibility.** Domain logic shall remain independent of FastAPI, Streamlit, and LangGraph; thresholds shall have one named source; prompts shall be versioned with evaluation snapshots; and a documented command sequence shall rebuild the index and evaluation tables. | Must | Architecture/code inspection and the quality gate (`ruff`, `mypy`, unit and integration tests, KB validation) pass. | Inspection / Test |
| NFR-10 | **Deployment constraints.** The prototype shall run CPU-only on a Windows-compatible laptop with 8 GB RAM, using local SQLite and Chroma storage rather than requiring cloud infrastructure. Cold start shall target <= 60 s. | Must | Fresh-machine local-demo check and startup-log measurement. | Demonstration / Analysis |

## 6. External interface requirements

The FastAPI `/v1` contract is the sole application boundary for both Streamlit and the evaluation harness. The following endpoints are required by the functional requirements:

| Interface | Purpose | Related requirements |
|---|---|---|
| `POST /v1/analyses` | Validate one image and start analysis. | FR-01 to FR-09 |
| `GET /v1/analyses/{id}` | Retrieve a frozen, replayable report. | FR-09, FR-11 |
| `POST /v1/analyses/{id}/clarify` | Submit clarification answers and resume affected work. | FR-08 |
| `PATCH /v1/analyses/{id}/components/{ord}` | Correct identity/mass and recompute. | FR-10 |
| `POST /v1/analyses/{id}/components` | Add a component missed by perception. | FR-10 |
| `DELETE /v1/analyses/{id}` | Remove stored analysis and artifacts. | FR-11, NFR-06 |
| `GET /v1/foods/search` | Find state-labelled knowledge-base candidates. | FR-04, FR-10 |
| `GET /v1/meta`, `GET /healthz` | Expose diagnostic metadata and dependency status. | FR-12 |

## 7. Business rules and immutable constraints

These rules protect the project's research claim and take precedence over implementation convenience.

| ID | Rule |
|---|---|
| BR-01 | A VLM may propose labels, regions, physical state, and relative size only; it must not supply calories, grams, or nutrients. |
| BR-02 | Nutrition is calculated in Python from database values. IFCT kJ values are divided by 4.184 for kcal. |
| BR-03 | `null` means “not reported”; it must not be coerced to zero during calculations or aggregation. |
| BR-04 | Retrieval filters on physical state before acceptance. Raw-to-cooked conversion is permitted only with a documented yield factor and `state_converted` limitation. |
| BR-05 | A retrieval score below 0.55 is not accepted. The component is unresolved rather than presented as a plausible-but-wrong food. |
| BR-06 | The UI formats `AnalysisResponse` fields only; it must not compute nutrition, confidence, or other metrics itself. |
| BR-07 | All response data validate against `AnalysisResponse`; failures use `application/problem+json`. |
| BR-08 | Changes to a prompt require a version increment and matching `*.meta.json` evaluation snapshot. |

## 8. Acceptance and traceability

Project readiness is determined by the evaluation targets in NFR-02 through NFR-04 and the following completion evidence:

- all core unit tests and mock-mode integration tests pass;
- the knowledge-base validation passes;
- every successful API response validates against `AnalysisResponse`;
- the offline demo works end-to-end on a fresh clone; and
- the report records any missed target honestly, alongside its error analysis.

| SRS area | Authoritative source documents |
|---|---|
| Scope, routing, budgets, architecture | [01 — System Architecture](01-architecture.md) |
| Module behaviour and core-calculation constraints | [02 — Module Design](02-modules.md) |
| Retrieval, physical-state filtering, and acceptance threshold | [03 — Knowledge Base and RAG](03-knowledge-base-and-rag.md) |
| Stored data, reproducibility, retention, and deletion | [04 — Data Model](04-data-model.md) |
| Endpoint and response contracts | [05 — API Contracts](05-api-contracts.md) |
| Confidence, clarification, and thresholds | [06 — Confidence and Clarification](06-confidence-and-clarification.md) |
| Prompt restrictions and versioning | [07 — Prompt Specifications](07-prompts.md) |
| Metrics and demo-readiness targets | [08 — Evaluation Plan](08-evaluation.md) |
| Hardware, offline mode, quality gate, ethics, and delivery plan | [09 — Engineering Plan](09-engineering-plan.md) |

## 9. Out of scope

The following are deliberately excluded from this phase:

- clinical nutrition advice, diagnosis, or personalised diet prescriptions;
- video, multi-frame tracking, barcode scanning, and restaurant-menu OCR;
- multi-tenant accounts, payments, and production-scale cloud deployment;
- universal cuisine coverage or complete micronutrient coverage; and
- ungrounded calorie, gram, or nutrient generation by a language model.

