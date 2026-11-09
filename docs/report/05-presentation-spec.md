# Presentation Specification (Department Mandate)

**Authority:** Project Coordinator and Head of the Department, Department of Computer Science and Engineering, GVP College of Engineering (Autonomous) — Centre for Innovation.
**Signed:** 7 November 2026.
**Applies to:** the final project PowerPoint deck for *Adaptive Food Recognition and Nutritional Estimation Using Multimodal AI*.
**Status:** binding. The deck is a separate deliverable from the report; both must agree on every number.

This file records the department's instructions verbatim and maps each mandatory slide to the material already in this repository, so the deck can be assembled without re-deriving content.

---

## 1. Formatting rules (mandatory)

- The presentation shall be **clear, concise, and in bullet points only**.
- **Lengthy paragraphs are not allowed.** A slide is a set of short bullets, not prose.
- Numbers, tables and diagrams carry the argument; sentences do not.
- Every claim on a slide must trace to a document in `docs/` or a measured result — same rule as the report ([00 §Rule](00-report-skeleton.md)).
- The fixed non-medical disclaimer (NFR-01) appears on the report/limitations slide and in the deck footer.

## 2. Mandatory slides (verbatim from the mandate)

| # | Slide | Required content |
|---|---|---|
| 1 | **Title Page** | Title of the project; name of the college; **college logo**; name of the department; guide name; names of the students |
| 2 | **Index** | Deck contents |
| 3 | **Abstract** | Problem, approach, headline result, contribution |
| 4 | **Introduction** | Background, domain context, why the problem matters |
| 5 | **Literature Survey** | Refer to **research papers from the last 3 years** |
| 5a | ↳ Challenges in domain area | What is hard about this problem today |
| 5b | ↳ Sub-domain (respective challenge) | The specific sub-area this project addresses |
| 5c | ↳ Motivation of work | Why this project is worth doing |
| 5d | ↳ Objectives | Measurable objectives |
| 5e | ↳ Problem statement | One precise statement of the problem |
| 6 | **System Workflow** | End-to-end flow from photo to report |
| 7 | **Methodology** | How each stage works |
| 8 | **Requirements** | Functional and non-functional requirements |
| 9 | **Dataset (if applicable)** | Datasets used, size, splits, licence |
| 10 | **Status of the project** | What is done, what is in progress, what remains |
| 11 | **Conclusion** | Findings, contribution, limitations, future scope |
| 12 | **References** | IEEE style, recent work included |

> Items 5a–5e are indented under Literature Survey in the mandate. Treat them as either five sub-slides or one survey flow — but all five headings must appear.

---

## 3. Slide-to-source map

Each mandatory slide already has an authoritative source in this repository. Do not write new claims; extract and compress.

| Slide | Source in repo | What to take |
|---|---|---|
| Title Page | [README](../../README.md#team) | Project title, team names + roll numbers, guide (Dr. G. Vani), department, institution |
| Index | This file §2 | The 12 mandatory slides |
| Abstract | [00 §Front matter](00-report-skeleton.md#front-matter) | 250–300 word abstract pattern; **write last**, after results |
| Introduction | [01 §1](../01-architecture.md#1-problem-framing), [00 Ch. 1](00-report-skeleton.md#chapter-1--introduction-56-pages) | The four error sources; the "one dish, one calorie number" failure; mixed Indian plate |
| Literature Survey | [00 Ch. 2](00-report-skeleton.md#chapter-2--literature-survey-68-pages) | Themed survey + **Table 2.1 gap analysis** — the justification slide |
| 5a Challenges | [00 Ch. 2](00-report-skeleton.md#chapter-2--literature-survey-68-pages) §2.1–2.6 "what is missing" endings | Identity error, portion error, ungrounded LLM numbers, overconfidence, Indian coverage |
| 5b Sub-domain | [01 §1](../01-architecture.md#1-problem-framing), [03](../03-knowledge-base-and-rag.md) | Component-level nutrition estimation with retrieval grounding + calibration |
| 5c Motivation | [00 §1.2](00-report-skeleton.md#chapter-1--introduction-56-pages), [README](../../README.md#one-paragraph-summary) | Multiplicative error (identity × mass); apps force one dish + guessed quantity |
| 5d Objectives | [00 §1.4](00-report-skeleton.md#chapter-1--introduction-56-pages) | Five objectives mapped to RQ1–RQ5, each with its metric |
| 5e Problem statement | [01 §1](../01-architecture.md#1-problem-framing) | Operationalised statement — not a paragraph |
| System Workflow | [04 — Methodology slides](04-methodology-slides.md) | The 11-stage flow and the one-line caption; [01](../01-architecture.md) C4/sequence diagrams |
| Methodology | [04 — Methodology slides](04-methodology-slides.md), [00 Ch. 4](00-report-skeleton.md#chapter-4--methodology-1012-pages-) | Stage table; decomposition → RAG match → portion → Python nutrition → confidence → clarification |
| Requirements | [11 — SRS](../11-software-requirements-specification.md) | FR-01…FR-12, NFR-01…NFR-10, the 8 business rules |
| Dataset | [08 — Evaluation](../08-evaluation.md), [10 — Dataset research](../10-dataset-research.md) | `gold_v1` composition, splits, annotation protocol, licences |
| Status | [README §Status](../../README.md#status), [09 — Engineering plan](../09-engineering-plan.md) | Phase 1 (design) complete; Phase 2 walking skeleton next; milestone table |
| Conclusion | [00 Ch. 7](00-report-skeleton.md#chapter-7--conclusion-and-future-scope-34-pages) | Objectives vs. achieved table; limitations; future scope |
| References | [00 §References](00-report-skeleton.md#references) | IEEE style, ≥ 30 entries |

---

## 4. Gaps to close before the deck is submission-ready

| Gap | Why it matters | Action |
|---|---|---|
| **College logo asset** | Mandated on the title slide; repo has no image assets | Obtain official GVPCE logo (high-resolution PNG/SVG) and store under `docs/report/assets/` |
| **Papers from the last 3 years (2023–2026)** | Mandate explicitly requires recent literature; the repo's citation base is dominated by classics (Food-101 2014, Nutrition5k 2021, RAG 2020, Guo 2017) | Add 5–8 recent multimodal-LLM-for-diet / food-recognition / calibration papers and mark them on the survey slide |
| **Measured results** | Abstract, Conclusion and Status slides currently have no numbers because Phase 2 has not run | Fill from `gold_v1` evaluation once it exists; until then the Status slide states design-phase status honestly |
| **Deck length** | Mandate says concise; 12 slides with 5 sub-items can sprawl | Target ~15–18 slides total, ≤ 6 bullets per slide |

## 5. Deck guardrails (non-negotiable)

These restate the project invariants that a slide could easily violate:

1. **No slide may claim the VLM produces calories, grams or nutrients.** The deck says the opposite, explicitly (BR-01).
2. **Any number shown on a slide must come from the repo or a measured run** — never estimated for the slide (BR-02, NFR-05).
3. **Physical-state filtering and the 0.55 threshold** are the two technical differentiators; both deserve a slide bullet (BR-04, BR-05).
4. **Uncertainty is shown as ranges and confidence bands**, never as a single false-precision figure (NFR-08).
5. **The disclaimer appears** wherever a nutrition value is displayed (NFR-01).
6. **Demo, if shown, runs in `MOCK_MODE=1`** — offline, no API key required (NFR-04).

## 6. Relationship to the report

- The report ([00](00-report-skeleton.md)) is the long-form evidence; this deck is the 15-minute argument.
- Slide numbers must match report numbers at submission time. If a result changes, update both.
- Chapter 3 of the report and the **Requirements** slide share one source: [11 — SRS](../11-software-requirements-specification.md).
- Chapter 4 and the **Methodology** slide share one source: [04 — Methodology slides](04-methodology-slides.md).
