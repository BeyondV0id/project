# Adaptive Food Recognition and Nutritional Estimation Using Multimodal AI

**Team:** The Invincibles · **Department:** Computer Science and Engineering
**Institution:** GVP College of Engineering (Autonomous) — Centre for Innovation

| Role | Name | Roll No. | Email | Mobile |
|---|---|---|---|---|
| Member | Gottumukkala Sri Abhigna | 323103310081 | 323103310081@gvpce.ac.in | 7799125455 |
| Member | Jetti Lakshmi Prasanna | 323103310097 | 323103310097@gvpce.ac.in | 7416654959 |
| Member | Harsha Vardhan Gandepalli | 323103310092 | 323103310092@gvpce.ac.in | 7207644341 |
| Member | Jami Sranay | 323103310095 | 323103310095@gvpce.ac.in | 9440706190 |
| Guide | Dr. G. Vani | — | vanig@gvpce.ac.in | 9703031020 |

---

## Status

**Phase 1 — Architecture and design: complete.** Phase 2 — walking skeleton: started.

What is implemented so far (under `src/`, offline, `MOCK_MODE=1`):

- **Data architecture** — Pydantic v2 schemas for `AnalysisResponse`, components, nutrients, questions, provenance (`src/core/schemas.py`).
- **Database** — SQLite with the full DDL from `docs/04-data-model.md` (16+ tables: `food`, `food_nutrient`, `analysis`, `analysis_component`, `clarification`, `feedback`, `llm_call`, ...), WAL mode, foreign keys, plus a seed with 25 demo foods and 7 nutrients (`src/db/`).
- **Nutrition arithmetic** — pure Python, NULL-preserving, kJ → kcal conversion, unit-tested (`src/core/nutrition.py`).
- **Confidence + clarification** — feature fusion, hard caps, isotonic calibration hook, question ranking (`src/core/confidence.py`, `src/core/clarify.py`).
- **LangGraph management** — typed state, 7 agent nodes (router, perception, retrieval, portion, calculator, critic, clarifier) and a runnable pipeline with a plain-Python fallback when `langgraph` is unavailable (`src/agents/`).
- **Mock provider path** — deterministic decomposition keyed by image hash; the full pipeline runs end-to-end offline.

In progress / not yet wired: ChromaDB vector store (design complete, in-memory stub in place pending `chromadb` install), FastAPI routes, Streamlit UI, live VLM provider.

Everything the team needs to continue coding — module boundaries, database schema, API contracts, prompts, retrieval strategy, evaluation protocol and report outline — is specified in `docs/`.

## One-paragraph summary

A photo of a mixed Indian meal is not one food. Existing calorie apps force you to pick "biryani" and guess a quantity, which is where most of the error comes from. This system **decomposes the plate into its individual components**, estimates each component's mass using scale references in the image, retrieves per-100 g nutrient values from a curated Indian + USDA knowledge base using hybrid RAG, and computes the meal totals with deterministic arithmetic rather than letting a language model invent numbers. Every component carries a **calibrated confidence score**; when a component is uncertain, the system asks the user exactly one targeted question instead of silently guessing. The output is an interpretable report: components, masses with ranges, calories, macronutrients, provenance for every number, and a confidence badge.

## Design decisions locked in this phase

| Decision | Choice | Rationale |
|---|---|---|
| Multimodal model | Pluggable provider; **Gemini 2.5 Flash** as the reference implementation | Strong vision + native JSON schema output; free tier is workable for a student project |
| Current provider | **Mock provider** (`MOCK_MODE=1`) | Team has no API key yet; the whole pipeline must run end-to-end offline |
| Nutrition knowledge base | **IFCT 2017 (Indian) primary + USDA FoodData Central fallback** | Demo meals are Indian; USDA covers everything the IFCT does not |
| Vector store | **ChromaDB** (persistent, local) | Zero-ops, file-based, easy to demo on a laptop |
| Embeddings | `BAAI/bge-small-en-v1.5` (384-d) | Good quality/size for a food corpus on CPU |
| Retrieval | **Hybrid BM25 + dense, RRF fusion, cross-encoder rerank** | Food names are proper nouns — pure dense retrieval misses exact names |
| Orchestration | **LangGraph** state machine, 7 agents | Satisfies the multi-agent requirement without hiding control flow |
| Backend | FastAPI + SQLite (Postgres-compatible schema) | Thin API layer so the Streamlit UI and the evaluation harness share one path |
| Frontend | Streamlit | Fastest route to a credible demo; team already has Python skills |
| Nutrition arithmetic | **Pure Python, no LLM** | Non-negotiable: numbers must be traceable to a database row |

## Document index

| # | Document | What it answers |
|---|---|---|
| 01 | [System Architecture](docs/01-architecture.md) | What are the layers, how does data flow, what is "adaptive" |
| 02 | [Module Design](docs/02-modules.md) | What does each module do, its interface, its failure modes |
| 03 | [Knowledge Base and RAG](docs/03-knowledge-base-and-rag.md) | Where nutrition data comes from and how it is retrieved |
| 04 | [Data Model](docs/04-data-model.md) | DDL for every table, vector collections, artifact storage |
| 05 | [API Contracts](docs/05-api-contracts.md) | Endpoints, Pydantic models, example payloads |
| 06 | [Confidence and Clarification](docs/06-confidence-and-clarification.md) | How confidence is computed, calibrated and acted upon |
| 07 | [Prompt Specifications](docs/07-prompts.md) | Verbatim prompts and JSON schemas for every agent |
| 08 | [Evaluation Plan](docs/08-evaluation.md) | Datasets, metrics, baselines, ablations, acceptance targets |
| 09 | [Engineering Plan](docs/09-engineering-plan.md) | Repo layout, stack, milestones, risks, ethics, demo script |
| 10 | [Project Report Skeleton](docs/report/00-report-skeleton.md) | Chapter-by-chapter outline of the final report |
| 11 | [Software Requirements Specification](docs/11-software-requirements-specification.md) | Functional and non-functional requirements, priorities, verification, and scope |
| 12 | [Presentation Specification](docs/report/05-presentation-spec.md) | Department-mandated slide list, formatting rules, and slide-to-source map for the final deck |

## Repository state

```
final_year_project/
├── README.md          ← you are here
└── docs/              ← architecture and design (this phase)
```

The target code layout is in [docs/09-engineering-plan.md](docs/09-engineering-plan.md#2-repository-layout).

## Next step

Implementation starts with **Phase 2 — walking skeleton**: mock provider + seeded IFCT subset + the six-node LangGraph + Streamlit single-image flow, so the pipeline is observable end-to-end before any model accuracy work begins.
# project
