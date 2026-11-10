#!/usr/bin/env python
"""Fix remaining issues on slides 2 and 13."""
from pptx import Presentation

prs = Presentation("D:\\final_year_project\\project_ppt_batch_11_Updated.pptx")

def clear_shape_text(shape):
    """Clear all text in a shape."""
    if shape.has_text_frame:
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                run.text = ""

# ============================================
# SLIDE 2 - Index: Remove "Serial No." and "Contents" labels
# ============================================
slide2 = prs.slides[1]
for shape in slide2.shapes:
    if shape.has_text_frame:
        full_text = ""
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                full_text += run.text
        if "Serial No." in full_text or full_text.strip() == "Contents":
            clear_shape_text(shape)

# ============================================
# SLIDE 13 - Remove the old 11-stage table (second text box)
# ============================================
slide13 = prs.slides[12]
for shape in slide13.shapes:
    if shape.has_text_frame:
        full_text = ""
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                full_text += run.text
        # The old table has "Stage / Primary Operation / Architectural Invariant" headers
        if "Stage" in full_text and "Primary Operation" in full_text:
            clear_shape_text(shape)
        # Also clear the "13" slide number if it's in a separate box
        if full_text.strip() == "13":
            clear_shape_text(shape)

# Save
output_path = "D:\\final_year_project\\project_ppt_batch_11_Updated.pptx"
prs.save(output_path)
print("Fixed slides 2 and 13")