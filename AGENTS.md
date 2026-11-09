# AGENTS.md

## Repository state — read this first

This repo is **documentation only** (Phase 1 of a final-year project). There is no `pyproject.toml`, no `requirements.txt`, no package manifest, no tests, no CI, and **no git repository** (`git status` will fail — do not run git commands unless the user asks to initialise one).

Do not go looking for a build or test command: none exists yet. The intended layout, stack and commands are specified in `docs/09-engineering-plan.md` — if you are asked to implement, follow that plan rather than inventing a different structure.

## What the project is

A Streamlit + FastAPI app that takes one meal photo and returns **per-component** nutrition: decompose the plate → estimate each component's mass → retrieve per-100 g values from a local IFCT 2017 + USDA knowledge base → compute totals in Python → report calibrated confidence and ask the user targeted questions when uncertain.

`ARCHITECTURE.md` is the one-page system overview. `docs/` holds the binding specification:

| File | Contract it defines |
|---|---|
| `docs/01-architecture.md` | Layers, adaptive routing tiers T0/T1/T2, budgets, ADRs |
| `docs/02-modules.md` | Module M0–M12 responsibilities and interfaces |
| `docs/03-knowledge-base-and-rag.md` | Dual-index RAG (`foods` + `dishes`), thresholds, yield factors |
| `docs/04-data-model.md` | SQL DDL — implement exactly this schema |
| `docs/05-api-contracts.md` | Pydantic models + endpoints — these are the UI's only source of numbers |
| `docs/06-confidence-and-clarification.md` | Confidence fusion, isotonic calibration, question ranking |
| `docs/07-prompts.md` | Versioned prompts and JSON schemas |
| `docs/08-evaluation.md` | Datasets, metrics, baselines, acceptance targets |
| `docs/09-engineering-plan.md` | Target directory tree, stack, 12-week milestones |

Report deliverables have their own folder: `docs/report/00-report-skeleton.md` (chapter outline), `docs/report/04-methodology-slides.md` (methodology slide content), and `docs/report/05-presentation-spec.md` (department-mandated deck: mandatory slides, bullets-only rule, slide-to-source map).

## Invariants — violating any of these breaks the project's central claim

1. **The VLM never outputs calories, grams, or nutrients.** The decomposition JSON schema has no such field, deliberately. All numbers come from `food_nutrient` rows via `app/core/nutrition.py`. If a prompt edit or a new field would let a model state a kcal value, it is wrong.
2. **Nutrition arithmetic is pure Python and unit-tested.** No LLM in the calculation path, ever. Energy from IFCT is in kJ → divide by 4.184.
3. **`NULL` means "not reported", never `0`.** Do not coerce missing nutrient values to zero when aggregating.
4. **Streamlit renders only fields from `AnalysisResponse`.** No metric may be computed client-side; if the UI needs something, add it to the API response.
5. **Retrieval must filter by `physical_state`.** Without it, cooked rice matches raw rice at 345 kcal/100 g instead of ~130 — the single largest systematic error in the system.
6. **`MOCK_MODE=1` is the default and must keep working offline.** The team has no VLM API key. A real key must never be required for tests, CI, or the demo.
7. **Thresholds live in `app/core/constants.py`** (`TAU_ACCEPT`, `TAU_IG_MIN`, `MAX_ROUNDS`, …) and are imported everywhere. No magic numbers in agents, UI or tests.
8. **Changing a prompt requires a version bump plus a `*.meta.json` eval snapshot.** Never edit a prompt in place.
9. **API responses always validate against `AnalysisResponse`.** Failures return `problem+json`; never partial JSON.
10. **A match below `0.55` is not accepted.** Mark `matched=False` and let clarification handle it — wrong-but-plausible is worse than unknown.

## Environment facts

- Windows + PowerShell (`win32`). Paths in docs use forward slashes; the shell needs quoting for spaces.
- Target Python 3.11/3.12, **CPU-only** (8 GB RAM laptop). Do not introduce GPU-only dependencies.
- Local state is file-based: `data/app.db` (SQLite), `data/chroma/` (Chroma), `data/artifacts/{analysis_id}/`. These are generated, not source — never hand-edit them into a commit.
- If scaffolding does not yet exist, the intended quality gate is `make check` → `ruff check` → `ruff format --check` → `mypy app/core app/api` → `pytest tests/unit` → `pytest tests/integration` → `python -m app.rag.validate_kb`.
- Entrypoints to create/keep: `app/api/main.py` (FastAPI), `app/ui/streamlit_app.py` (Streamlit), `app/agents/graph.py` (LangGraph), `app/core/*` (pure domain logic).

## Conventions that differ from defaults

- Domain logic in `app/core/` must not import FastAPI, Streamlit or LangGraph — that is what keeps it unit-testable. Agents in `app/agents/` are thin adapters.
- Providers return **validated Pydantic objects or raise**; never dicts, never half-parsed JSON.
- Every stored analysis records `provider`, `model`, `prompt_version`, `kb_version`, `compute_version` — reports must be reproducible, so do not drop these fields.
- Deterministic mock responses are keyed by SHA-256 of the image bytes; keep that contract when adding fixtures.
- Team ownership (useful when deciding whose file to touch): Harsha — API/providers/UI/infra; Abhigna — KB/ingestion/retrieval; Sranay — portion/nutrition; Prasanna — orchestration/confidence/evaluation.

## Working agreement

Before implementing a module, read its entry in `docs/02-modules.md` and the matching schema/contract doc. After implementing, update the doc if reality diverges — the docs are the project's specification and are marked for the final report, so silent divergence is worse than a visible correction.
