"""Persistence helpers for analyses."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from src.db.connection import connect


def create_analysis(image_path=None, context=None, kb_version="2026.11.1"):
    aid = uuid.uuid4().hex
    now = datetime.now(timezone.utc).isoformat()
    conn = connect()
    conn.execute(
        "INSERT INTO analysis (id,created_at,updated_at,status,tier,image_path,context_text,kb_version) VALUES (?,?,?,?,?,?,?,?)",
        (aid, now, now, "received", None, image_path, context, kb_version),
    )
    conn.commit()
    conn.close()
    return aid


def update_status(aid, status, **fields):
    conn = connect()
    sets = ["status=?", "updated_at=?"]
    vals = [status, datetime.now(timezone.utc).isoformat()]
    for k, v in fields.items():
        sets.append(k + "=?")
        vals.append(v)
    vals.append(aid)
    conn.execute("UPDATE analysis SET " + ", ".join(sets) + " WHERE id=?", vals)
    conn.commit()
    conn.close()


def get_analysis(aid):
    conn = connect()
    row = conn.execute("SELECT * FROM analysis WHERE id=?", (aid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def save_component(aid, comp):
    conn = connect()
    conn.execute(
        "INSERT OR REPLACE INTO analysis_component (analysis_id,ord,label_raw,label_display,bbox_norm,food_id,mass_g,mass_ci_low,mass_ci_high,portion_method,kcal,protein_g,carb_g,fat_g,fibre_g,nutrients_json,confidence,flags_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (aid, comp["ord"], comp["label"], comp.get("display_label", comp["label"]),
         json.dumps(comp.get("bbox_norm", [0, 0, 1, 1])), comp.get("food_id"),
         comp.get("mass_g"), comp.get("mass_ci_low"), comp.get("mass_ci_high"),
         comp.get("portion_method"), comp.get("kcal"), comp.get("protein_g"),
         comp.get("carb_g"), comp.get("fat_g"), comp.get("fibre_g"),
         json.dumps(comp.get("nutrients", {})), comp.get("confidence"),
         json.dumps(comp.get("flags", []))),
    )
    conn.commit()
    conn.close()
