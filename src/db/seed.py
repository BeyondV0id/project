"""Seed data: sources, nutrients, portion models, 25 demo foods."""

from __future__ import annotations

import sqlite3

NUTRIENTS = [
    ("energy_kcal", "Energy", "kcal", "macro"),
    ("protein_g", "Protein", "g", "macro"),
    ("carb_g", "Carbohydrate", "g", "macro"),
    ("fat_g", "Fat", "g", "macro"),
    ("fibre_g", "Dietary fibre", "g", "macro"),
    ("calcium_mg", "Calcium", "mg", "micro"),
    ("iron_mg", "Iron", "mg", "micro"),
]

SOURCES = [
    ("IFCT2017", "IFCT 2017", "2017", "https://www.nin.res.in", "public domain facts", 10),
    ("USDA_FDC", "USDA FoodData Central", "Foundation 2026-04", "https://fdc.nal.usda.gov", "public domain", 20),
    ("CUSTOM", "User custom foods", None, None, "user", 30),
]

DEMO_FOODS = [
    # (canonical, display, category, state, kcal, protein, carb, fat, fibre)
    ("rice_cooked", "Rice, cooked (white)", "cereal", "cooked", 130, 2.7, 28.2, 0.3, 0.4),
    ("chapati", "Chapati (wheat)", "cereal", "cooked", 297, 9.0, 54.0, 3.7, 7.0),
    ("dal_cooked", "Dal, cooked (toor)", "pulse", "cooked", 116, 7.0, 17.0, 3.0, 4.0),
    ("sambar", "Sambar", "composite", "gravy", 62, 2.5, 8.0, 2.5, 2.0),
    ("rasam", "Rasam", "liquid", "liquid", 25, 0.8, 4.0, 0.5, 0.5),
    ("curd", "Curd (dahi)", "dairy", "any", 60, 3.1, 4.0, 3.0, 0.0),
    ("paneer", "Paneer, full fat", "dairy", "raw", 296, 18.0, 3.0, 24.0, 0.0),
    ("mixed_veg_curry", "Mixed vegetable curry", "vegetable", "gravy", 85, 2.0, 9.0, 4.5, 3.0),
    ("biryani", "Chicken biryani", "composite", "cooked", 190, 8.0, 24.0, 7.0, 1.5),
    ("idli", "Idli", "cereal", "cooked", 58, 2.0, 12.0, 0.3, 0.5),
    ("dosa", "Dosa (plain)", "cereal", "cooked", 160, 3.5, 24.0, 5.0, 1.0),
    ("upma", "Upma", "cereal", "cooked", 165, 4.0, 24.0, 6.0, 2.0),
    ("poha", "Poha", "cereal", "cooked", 180, 3.5, 30.0, 5.0, 1.5),
    ("egg_boiled", "Egg, boiled", "meat", "cooked", 155, 13.0, 1.1, 11.0, 0.0),
    ("chicken_curry", "Chicken curry", "meat", "gravy", 180, 18.0, 4.0, 10.0, 0.5),
    ("salad", "Mixed salad", "vegetable", "raw", 25, 1.0, 4.0, 0.3, 1.5),
    ("pickle", "Pickle (mango)", "other", "any", 120, 1.0, 8.0, 9.0, 1.0),
    ("papad", "Papad, roasted", "other", "cooked", 350, 23.0, 48.0, 6.0, 6.0),
    ("ghee", "Ghee", "oil", "any", 900, 0.0, 0.0, 100.0, 0.0),
    ("oil", "Cooking oil", "oil", "any", 884, 0.0, 0.0, 100.0, 0.0),
    ("sugar", "Sugar", "other", "any", 387, 0.0, 100.0, 0.0, 0.0),
    ("tea", "Tea (with milk, sugar)", "liquid", "liquid", 45, 1.0, 8.0, 1.0, 0.0),
    ("banana", "Banana", "fruit", "raw", 89, 1.1, 23.0, 0.3, 2.6),
    ("apple", "Apple", "fruit", "raw", 52, 0.3, 14.0, 0.2, 2.4),
    ("milk", "Milk, full fat", "dairy", "liquid", 61, 3.2, 4.8, 3.3, 0.0),
]


def seed(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    # sources
    for code, name, ver, url, lic, prio in SOURCES:
        cur.execute(
            "INSERT OR IGNORE INTO source (code,name,version,url,license,priority) VALUES (?,?,?,?,?,?)",
            (code, name, ver, url, lic, prio),
        )
    # nutrients
    for code, name, unit, kind in NUTRIENTS:
        cur.execute(
            "INSERT OR IGNORE INTO nutrient (code,name,unit,kind) VALUES (?,?,?,?)",
            (code, name, unit, kind),
        )
    # source id for IFCT
    cur.execute("SELECT id FROM source WHERE code='IFCT2017'")
    src_id = cur.fetchone()[0]
    # foods + nutrients
    for canon, disp, cat, state, kcal, prot, carb, fat, fib in DEMO_FOODS:
        cur.execute(
            """INSERT OR IGNORE INTO food (source_id,source_ref,canonical_name,display_name,
               category,physical_state,density_g_ml) VALUES (?,?,?,?,?,?,?)""",
            (src_id, canon, canon, disp, cat, state, 1.0),
        )
        cur.execute("SELECT id FROM food WHERE canonical_name=?", (canon,))
        fid = cur.fetchone()[0]
        vals = {
            "energy_kcal": kcal, "protein_g": prot, "carb_g": carb,
            "fat_g": fat, "fibre_g": fib,
        }
        for code, amt in vals.items():
            cur.execute("SELECT id FROM nutrient WHERE code=?", (code,))
            nid = cur.fetchone()[0]
            cur.execute(
                "INSERT OR REPLACE INTO food_nutrient (food_id,nutrient_id,amount_per_100g) VALUES (?,?,?)",
                (fid, nid, amt),
            )
    conn.commit()
