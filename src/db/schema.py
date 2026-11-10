"""DDL from docs/04-data-model.md."""

from __future__ import annotations

DDL = r"""
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS source (
    id            INTEGER PRIMARY KEY,
    code          TEXT NOT NULL UNIQUE,
    name          TEXT NOT NULL,
    version       TEXT,
    url           TEXT,
    license       TEXT,
    priority      INTEGER NOT NULL DEFAULT 100,
    retrieved_at  TEXT
);

CREATE TABLE IF NOT EXISTS food (
    id                INTEGER PRIMARY KEY,
    source_id         INTEGER NOT NULL REFERENCES source(id),
    source_ref        TEXT NOT NULL,
    canonical_name    TEXT NOT NULL,
    display_name      TEXT NOT NULL,
    category          TEXT NOT NULL,
    physical_state    TEXT NOT NULL,
    is_composite      INTEGER NOT NULL DEFAULT 0,
    is_preferred      INTEGER NOT NULL DEFAULT 0,
    edible_portion_pct REAL NOT NULL DEFAULT 100,
    default_portion_g REAL,
    density_g_ml      REAL,
    notes             TEXT,
    UNIQUE (source_id, source_ref)
);
CREATE INDEX IF NOT EXISTS idx_food_canonical ON food(canonical_name);
CREATE INDEX IF NOT EXISTS idx_food_category  ON food(category, physical_state);

CREATE TABLE IF NOT EXISTS food_alias (
    id        INTEGER PRIMARY KEY,
    food_id   INTEGER NOT NULL REFERENCES food(id) ON DELETE CASCADE,
    alias     TEXT NOT NULL,
    lang      TEXT NOT NULL DEFAULT 'en',
    weight    REAL NOT NULL DEFAULT 1.0,
    UNIQUE (food_id, alias)
);
CREATE INDEX IF NOT EXISTS idx_alias_lookup ON food_alias(alias);

CREATE TABLE IF NOT EXISTS nutrient (
    id    INTEGER PRIMARY KEY,
    code  TEXT NOT NULL UNIQUE,
    name  TEXT NOT NULL,
    unit  TEXT NOT NULL,
    kind  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS food_nutrient (
    food_id         INTEGER NOT NULL REFERENCES food(id) ON DELETE CASCADE,
    nutrient_id     INTEGER NOT NULL REFERENCES nutrient(id),
    amount_per_100g REAL,
    min_value       REAL,
    max_value       REAL,
    data_points     INTEGER,
    note            TEXT,
    PRIMARY KEY (food_id, nutrient_id)
);

CREATE TABLE IF NOT EXISTS household_measure (
    id        INTEGER PRIMARY KEY,
    food_id   INTEGER NOT NULL REFERENCES food(id) ON DELETE CASCADE,
    label     TEXT NOT NULL,
    volume_ml REAL,
    weight_g  REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS dish_recipe (
    id                INTEGER PRIMARY KEY,
    dish_food_id      INTEGER NOT NULL REFERENCES food(id) ON DELETE CASCADE,
    component_food_id INTEGER NOT NULL REFERENCES food(id),
    fraction          REAL NOT NULL CHECK (fraction > 0 AND fraction <= 1),
    fraction_min      REAL,
    fraction_max      REAL,
    basis             TEXT,
    UNIQUE (dish_food_id, component_food_id)
);

CREATE TABLE IF NOT EXISTS portion_model (
    id           INTEGER PRIMARY KEY,
    food_class   TEXT NOT NULL UNIQUE,
    density_g_ml REAL NOT NULL,
    heap_k       REAL NOT NULL,
    shape_factor REAL NOT NULL DEFAULT 1.0,
    fill_factor  REAL NOT NULL DEFAULT 0.70,
    mass_min_g   REAL,
    mass_max_g   REAL,
    source_note  TEXT,
    measured_at  TEXT
);

CREATE TABLE IF NOT EXISTS analysis (
    id                TEXT PRIMARY KEY,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL,
    status            TEXT NOT NULL,
    tier              TEXT,
    image_path        TEXT,
    image_phash       TEXT,
    image_quality     REAL,
    context_text      TEXT,
    provider          TEXT,
    model             TEXT,
    prompt_version    TEXT,
    kb_version        TEXT,
    compute_version   TEXT,
    total_kcal_p50    REAL,
    total_kcal_p10    REAL,
    total_kcal_p90    REAL,
    meal_confidence   REAL,
    latency_ms        INTEGER,
    cost_usd          REAL,
    error_json        TEXT
);
CREATE INDEX IF NOT EXISTS idx_analysis_created ON analysis(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_status  ON analysis(status);

CREATE TABLE IF NOT EXISTS analysis_component (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id       TEXT NOT NULL REFERENCES analysis(id) ON DELETE CASCADE,
    ord               INTEGER NOT NULL,
    label_raw         TEXT NOT NULL,
    label_display     TEXT NOT NULL,
    bbox_norm         TEXT NOT NULL,
    crop_path         TEXT,
    food_id           INTEGER REFERENCES food(id),
    match_type        TEXT,
    match_score       REAL,
    matched_state     TEXT,
    mass_g            REAL,
    mass_ci_low       REAL,
    mass_ci_high      REAL,
    portion_method    TEXT,
    portion_features  TEXT,
    kcal              REAL,
    protein_g         REAL,
    carb_g            REAL,
    fat_g             REAL,
    fibre_g           REAL,
    nutrients_json    TEXT,
    confidence        REAL,
    confidence_raw    REAL,
    flags_json        TEXT,
    UNIQUE (analysis_id, ord)
);
CREATE INDEX IF NOT EXISTS idx_component_analysis ON analysis_component(analysis_id);

CREATE TABLE IF NOT EXISTS clarification (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id   TEXT NOT NULL REFERENCES analysis(id) ON DELETE CASCADE,
    component_ord INTEGER,
    kind          TEXT NOT NULL,
    question      TEXT NOT NULL,
    options_json  TEXT,
    answer        TEXT,
    answered_at   TEXT,
    info_gain     REAL
);
CREATE INDEX IF NOT EXISTS idx_clarification_analysis ON clarification(analysis_id);

CREATE TABLE IF NOT EXISTS feedback (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id   TEXT NOT NULL REFERENCES analysis(id) ON DELETE CASCADE,
    component_ord INTEGER,
    field         TEXT NOT NULL,
    predicted     TEXT,
    corrected     TEXT,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS llm_call (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id TEXT REFERENCES analysis(id) ON DELETE CASCADE,
    agent       TEXT NOT NULL,
    provider    TEXT NOT NULL,
    model       TEXT NOT NULL,
    in_tokens   INTEGER,
    out_tokens  INTEGER,
    latency_ms  INTEGER,
    cost_usd    REAL,
    ok          INTEGER NOT NULL DEFAULT 1,
    error       TEXT,
    created_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_llm_call_analysis ON llm_call(analysis_id);

CREATE TABLE IF NOT EXISTS usda_cache (
    query_hash   TEXT PRIMARY KEY,
    query        TEXT NOT NULL,
    fdc_id       TEXT,
    payload_json TEXT NOT NULL,
    fetched_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS calibration_model (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    kind        TEXT NOT NULL,
    params_json TEXT NOT NULL,
    n_samples   INTEGER,
    ece         REAL,
    trained_at  TEXT NOT NULL,
    is_active   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS eval_dataset (
    id         INTEGER PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE,
    n_images   INTEGER,
    notes      TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eval_item (
    id           INTEGER PRIMARY KEY,
    dataset_id   INTEGER NOT NULL REFERENCES eval_dataset(id) ON DELETE CASCADE,
    image_path   TEXT NOT NULL,
    split        TEXT NOT NULL,
    ground_truth TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eval_run (
    id           INTEGER PRIMARY KEY,
    dataset_id   INTEGER NOT NULL REFERENCES eval_dataset(id),
    config_name  TEXT NOT NULL,
    git_sha      TEXT,
    started_at   TEXT NOT NULL,
    finished_at  TEXT,
    metrics_json TEXT
);

CREATE TABLE IF NOT EXISTS eval_result (
    id           INTEGER PRIMARY KEY,
    run_id       INTEGER NOT NULL REFERENCES eval_run(id) ON DELETE CASCADE,
    item_id      INTEGER NOT NULL REFERENCES eval_item(id),
    prediction   TEXT NOT NULL,
    metrics_json TEXT
);

CREATE VIEW IF NOT EXISTS v_component_report AS
SELECT c.analysis_id, c.ord, c.label_display, c.mass_g,
       c.mass_ci_low, c.mass_ci_high, c.kcal, c.protein_g, c.carb_g, c.fat_g,
       c.confidence, c.flags_json,
       f.display_name AS kb_name,
       s.code         AS source_code,
       f.source_ref   AS source_ref
FROM analysis_component c
LEFT JOIN food   f ON f.id = c.food_id
LEFT JOIN source s ON s.id = f.source_id;
"""


def init_db(conn):
    conn.executescript(DDL)
    conn.commit()
