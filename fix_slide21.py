#!/usr/bin/env python
"""Fix duplicate critical path on slide 21."""
from pptx import Presentation

prs = Presentation("D:\\final_year_project\\Adaptive_Food_Recognition_Final_Updated.pptx")
slide21 = prs.slides[20]

for shape in slide21.shapes:
    if shape.has_text_frame:
        full_text = ""
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                full_text += run.text
        if "Critical path" in full_text and full_text.count("Critical path") > 1:
            # Clear all paragraphs
            while len(shape.text_frame.paragraphs) > 1:
                p = shape.text_frame.paragraphs[-1]
                p._p.getparent().remove(p._p)
            
            para = shape.text_frame.paragraphs[0]
            for run in para.runs:
                run.text = ""
            para.runs[0].text = (
                "• Phase 1 — Specification, data model, KB ingestion, API contracts: DONE (code complete)\n"
                "• Phase 2 — Walking skeleton with LangGraph, offline demo, portion geometry: IN PROGRESS\n"
                "• Phase 3 — Live VLM integration, confidence calibration, clarification loop: PLANNED\n"
                "• Phase 4 — Full evaluation on gold_v1, final report and presentation: PLANNED\n"
                "• Critical path: kitchen weighing sessions to expand component-level ground truth"
            )
            break

output_path = "D:\\final_year_project\\Adaptive_Food_Recognition_Final_Updated.pptx"
prs.save(output_path)
print("Fixed slide 21")