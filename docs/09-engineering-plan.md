# 09 — Engineering Plan

---

## 1. Stack

| Layer | Choice | Version pinning | Why |
|---|---|---|---|
| Language | Python | 3.11 or 3.12 | best ecosystem support; avoid 3.13 until torch is stable |
| UI | Streamlit | `>=1.36,<2` | fastest credible demo, no frontend work |
| API | FastAPI + Uvicorn | `>=0.111` | typed contracts, auto OpenAPI docs |
| Validation | Pydantic v2 | `>=2.7` | schema enforcement + JSON schema for VLM |
| Orchestration | LangGraph | `>=0.2` | explicit state machine, checkpointing |
| VLM | `google-genai` (reference), `groq`, `ollama` | latest | provider abstraction makes this swappable |
| Embeddings | sentence-transformers `BAAI/bge-small-en-v1.5` | `>=3.0` | CPU-friendly |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` | same | CPU, ~20 ms/pair |
| Vector DB | chromadb | `>=0.5` | persistent, metadata filters |
| BM25 | bm25s | `>=0.2` | fast, pure Python |
| SQL | SQLite + `sqlite3`/SQLAlchemy Core | stdlib | zero ops |
| Images | Pillow, OpenCV (`opencv-python-headless`) | latest | EXIF, resize, Laplacian |
| Matching | rapidfuzz | `>=3.9` | fast fuzzy matching |
| Numerics | numpy, pandas, scikit-learn | latest | isotonic, metrics |
| Testing | pytest, pytest-cov, ruff, mypy | latest | quality gate |
| Packaging | `uv` or `pip` + `requirements.txt` | — | `uv` is much faster if available |

**Hardware assumption:** any laptop with 8 GB RAM and no GPU. Everything above runs on CPU. If a GPU is available, only the embedding model gets faster.

---

## 2. Repository layout

```
final_year_project/
├── README.md
├── docs/                          ← this design set
├── pyproject.toml
├── requirements.txt
├── .env.example
├── Makefile
│
├── app/
│   ├── __init__.py
│   ├── config.py                 # env, paths, feature flags, thresholds import
│   ├── constants.py              # TAU_*, nutrient codes, disclaimers
│   │
│   ├── providers/
│   │   ├── base.py               # VisionProvider protocol + CallMeta
│   │   ├── mock.py               # deterministic fixtures provider
│   │   ├── gemini.py
│   │   ├── groq.py               # optional
│   │   └── __init__.py           # registry
│   │
│   ├── prompts/
│   │   ├── registry.py
│   │   ├── perception/v1.2.0.jinja + .meta.json
│   │   ├── verify/v1.0.1.jinja
│   │   ├── critic/v1.1.0.jinja
│   │   └── dish_recipe/v1.0.0.jinja
│   │
│   ├── core/
│   │   ├── intake.py             # M1
│   │   ├── router.py             # M2
│   │   ├── perception.py         # M3
│   │   ├── matching.py           # M4
│   │   ├── portion.py            # M5
│   │   ├── nutrition.py          # M7
│   │   ├── critic.py             # M8
│   │   ├── confidence.py         # M9
│   │   ├── clarify.py            # M9
│   │   ├── report.py             # M10
│   │   ├── store.py              # M11
│   │   └── schemas.py            # all Pydantic models
│   │
│   ├── rag/
│   │   ├── ingest.py             # source CSVs → parquet
│   │   ├── validate_kb.py
│   │   ├── build_index.py
│   │   ├── retriever.py          # hybrid search + rerank
│   │   ├── usda_client.py
│   │   └── render.py             # food card → document text
│   │
│   ├── agents/
│   │   ├── graph.py              # LangGraph wiring
│   │   ├── state.py
│   │   └── nodes/*.py            # router, perception, portion, retrieval, ...
│   │
│   ├── api/
│   │   ├── main.py
│   │   ├── routes.py
│   │   └── errors.py             # problem+json
│   │
│   ├── ui/
│   │   ├── streamlit_app.py
│   │   └── components/*.py       # cards, badges, clarifier form, macros
│   │
│   └── eval/
│       ├── run.py
│       ├── metrics.py
│       ├── report.py
│       └── datasets.py
│
├── data/
│   ├── kb/2026.11.1/{raw,processed,manifest.json}
│   ├── chroma/
│   ├── artifacts/                # gitignored
│   ├── fixtures/                 # mock-mode decompositions + sample images
│   ├── gold_v1/{images,labels.json}
│   └── app.db                    # gitignored
│
├── scripts/
│   ├── seed_db.py
│   ├── weigh_session.py          # helper for recording ground-truth masses
│   └── demo.sh
│
└── tests/
    ├── unit/                     # per module, no network
    ├── integration/              # mock-mode graph runs
    └── fixtures/
```

---

## 3. Configuration

`.env.example`

```bash
# ── mode ────────────────────────────────────────────────
MOCK_MODE=1                     # 1 = no network, deterministic
APP_ENV=dev                     # dev | demo | eval

# ── provider ────────────────────────────────────────────
VLM_PROVIDER=mock               # mock | gemini | groq | ollama
GEMINI_API_KEY=
GROQ_API_KEY=
OLLAMA_HOST=http://localhost:11434
VLM_MODEL=gemini-2.5-flash

# ── knowledge base ──────────────────────────────────────
KB_VERSION=2026.11.1
CHROMA_DIR=./data/chroma
SQLITE_PATH=./data/app.db

# ── nutrition api ───────────────────────────────────────
USDA_API_KEY=
USDA_ENABLED=0                  # keep 0 until a key exists
USDA_TIMEOUT_S=8
USDA_CACHE_TTL_DAYS=90

# ── limits ──────────────────────────────────────────────
MAX_UPLOAD_MB=10
MAX_IMAGE_SIDE=1024
MAX_CLARIFY_ROUNDS=2
RATE_LIMIT_HOURLY=60

# ── eval ────────────────────────────────────────────────
EVAL_SEED=7
```

`.env` is gitignored. `config.py` fails fast with a readable error listing missing required keys for the selected mode — never a stack trace at import time.

---

## 4. Milestones (12-week plan, 4 members)

| Week | Milestone | Deliverable | Owner focus |
|---|---|---|---|
| 1 | Freeze design, set up repo, CI, lint | `docs/` merged, `make check` green | Harsha (infra) |
| 2 | KB v0.1: 25 foods + 6 composites + aliases + densities | `data/kb/…/foods.parquet`, seeded DB | Abhigna (data) |
| 3 | Retrieval working end-to-end, retrieval eval table | `app/rag/*`, Recall@k numbers | Abhigna + Sranay |
| 4 | Mock provider + intake + perception + Streamlit upload loop | image in → component list out | Harsha |
| 5 | Portion estimator + nutrition calculator + unit tests | grams + kcal per component | Sranay |
| 6 | **Walking skeleton complete** (mock, T0 only) | full report rendered from mock data | all |
| 7 | LangGraph agents, critic, confidence fusion | graph + state + tests | Prasanna |
| 8 | Clarification loop + PATCH corrections + feedback table | two-round clarify UI | Prasanna |
| 9 | Live provider integration (Gemini), T1/T2, cost logging | real VLM path behind flag | Harsha |
| 10 | `gold_v1` capture + weighing session (150 images) | labels.json + scale sheet | all (one weekend) |
| 11 | Full evaluation, baselines, ablations, calibration | result tables, reliability diagram | Prasanna + Abhigna |
| 12 | Report, presentation, demo rehearsal, buffer | 60-page report, 15-min demo | all |

**Critical path:** the weighing session (week 10) must not slip — it is the only source of ground-truth mass and everything in the Results chapter depends on it. If it slips, move it to week 8.

**Suggested ownership** is a starting point; every module has one primary owner and one reviewer, and nobody owns more than two modules.

---

## 5. Quality gate

`make check` runs:

```
ruff check app tests          # lint
ruff format --check           # format
mypy app/core app/api         # types on the pure core
pytest tests/unit -q          # fast unit tests
pytest tests/integration -q   # mock-mode graph (no network)
python -m app.rag.validate_kb # KB invariants
```

CI: GitHub Actions, Python 3.11, `MOCK_MODE=1`, no secrets required. A run must pass in < 3 minutes. **A failing API key must never fail CI** — that is why mock mode is first-class.

---

## 6. Risk register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| No VLM API key / quota exhausted | **High** (current state) | High | Mock provider is the default path; the entire demo runs offline. Gemini free tier is a bonus, not a dependency |
| Portion estimation unacceptably inaccurate | Medium | High | Calibrate on the weighing session early (week 5), widen CIs honestly, lean on clarification; report real MAE rather than hiding it |
| IFCT transcription errors | Medium | Medium | Dual transcription + diff + page-number provenance; start with 25 foods, not 528 |
| Indian dish coverage gaps | High | Medium | Alias-heavy seeding + USDA fallback + `free_text` clarification |
| LangGraph complexity eats time | Medium | Medium | Walking skeleton in week 6 uses plain Python; LangGraph wraps it in week 7. If it slips, the plain orchestrator ships |
| Refactoring data schema late | Medium | High | This document set is the contract; changes require a written ADR |
| Team member unavailable | Medium | High | Modules are decoupled behind interfaces; each has a named backup |
| Demo network failure | Medium | High | `MOCK_MODE=1` + pre-recorded `report.json` replay + local index. Never demo on venue Wi-Fi |
| Scope creep (barcode, wearable, meal history) | High | Medium | Non-goals list in [01](01-architecture.md#2-goals-and-non-goals) is binding until week 12 |

---

## 7. Team split (suggested)

| Member | Primary | Secondary |
|---|---|---|
| Harsha | API, providers, Streamlit, infra/CI | intake, deployment, demo |
| Abhigna | Knowledge base, ingestion, retrieval, aliases | evaluation data |
| Sranay | Portion estimator, nutrition calculator, unit tests | critic |
| Prasanna | Orchestration, confidence, clarification, evaluation | report writing lead |

Everyone: annotation, weighing session, report, presentation.

---

## 8. Ethics, privacy and disclaimers

| Concern | Stance |
|---|---|
| Medical advice | The app reports estimates, never diagnoses, never prescribes. Fixed disclaimer string on every report and in the UI footer. |
| Eating-disorder risk | No moralising language, no "good/bad food" labels, no target-calorie gamification. Calories are shown with ranges, not as a score to minimise. |
| Privacy | Images are the most sensitive artefact. Stored locally only, 30-day default retention, one-click delete, no third-party upload beyond the configured VLM provider — and the UI states which provider receives the image. |
| Consent for the user study | Written consent, anonymised images, right to withdraw and delete. |
| Dataset licensing | Food-101 (research use), FoodSeg103 (check licence), Nutrition5k (research use), Kaggle sets (per-dataset). Cite each in the report's references. |
| IFCT usage | Values are published scientific facts; the transcription is the team's own work. Cite NIN Hyderabad, IFCT 2017 prominently. |
| Bias | Indian meals are the focus because that is the project's context — state this as a scope decision, not a universal claim. USDA coverage mitigates but does not eliminate Western bias. |
| Hallucination | Structurally prevented for nutrients (schema has no such field + arithmetic layer). Disclosed for LLM-generated composite recipes (`basis="llm_generated_v1"`). |

---

## 9. Demo script (12 minutes)

| Min | Beat | What to show |
|---|---|---|
| 0–1 | Problem | One app screenshot: "biryani, 550 kcal" vs. the actual plate. State the two error sources. |
| 1–3 | Architecture | The 2-tier diagram + the three axes of adaptivity. Do not read the diagram; point at it. |
| 3–5 | Live demo, mixed plate | Upload a thali. Show components, masses, kcal, confidence badges. **Highlight a low-confidence item.** |
| 5–6 | Clarification | Answer the one question. Show the total and the interval tighten. This is the moment that sells the project. |
| 6–8 | Grounding | Open "How do you know?" — show IFCT row + page/code. Contrast with baseline A's unauditable number. |
| 8–10 | Results | Three tables: decomposition F1, kcal MAE across baselines, reliability diagram. One sentence per table. |
| 10–11 | Honest failure | Show the error taxonomy and the accepted limitations. Judges reward this. |
| 11–12 | Roadmap + close | Wearables, barcode, meal history, regional expansion. End on the disclaimer and privacy stance. |

**Rehearsal rules:** run the demo 5 times end-to-end, twice with the network off, once on a fresh machine. Keep a `demo_replay/` folder of three `report.json` files to load instantly if anything stalls.

---

## 10. Viva questions to prepare (with the answer that scores)

1. **"Why not just ask GPT/Gemini for calories?"** → Because numbers must be auditable (P1/P2), and VLM nutrition recall is inconsistent. We measure baseline B to prove it.
2. **"How do you know a portion is 165 g?"** → Plate-anchor geometry → volume → density, with a calibrated CI; and we validate MAE on 150 weighed plates.
3. **"Isn't your confidence just made up?"** → It is fused from 7 measurable features, isotonic-calibrated on dev data, and reported with ECE and a reliability diagram on test data.
4. **"What happens with a dish you've never seen?"** → Retrieval refuses below 0.55, falls back to USDA, then asks the user via `free_text`. Never guesses silently.
5. **"Why LangGraph and not one prompt?"** → Per-stage metrics, per-stage retries, resumable clarification, and a diagram that maps to the methodology chapter.
6. **"What is novel here?"** → Dual-index retrieval (ingredient + composite recipe), calibrated selective clarification ranked by expected error reduction, and a scale-anchored portion model validated against weighed food. Not "we used a VLM".
7. **"What would you do with six more months?"** → Depth estimation for heap height, 3D reconstruction, longitudinal diet tracking, dietician-in-the-loop validation, Hindi/Telugu voice input.

---

## 11. Definition of done (project level)

- [ ] `MOCK_MODE=1` demo works end-to-end on a fresh clone in under 5 minutes
- [ ] All acceptance criteria in [08 §7](08-evaluation.md#7-acceptance-criteria-what-done-means) met or honestly reported
- [ ] 100 % of unit tests pass; core modules ≥ 80 % coverage
- [ ] Report contains real tables from `results/`, not placeholders
- [ ] Every number in the report is reproducible from a committed script
- [ ] Repo README lets a stranger run it
- [ ] Privacy/delete path demonstrated
- [ ] Demo rehearsed offline
