#!/usr/bin/env python
"""Clear tables on slides 2 and 13."""
from pptx import Presentation

prs = Presentation("D:\\final_year_project\\project_ppt_batch_11_Updated.pptx")

# ============================================
# SLIDE 2 - Clear the index table
# ============================================
slide2 = prs.slides[1]
for shape in slide2.shapes:
    if shape.has_table:
        table = shape.table
        # Clear all cells
        for row in table.rows:
            for cell in row.cells:
                cell.text = ""

# ============================================
# SLIDE 13 - Clear the old pipeline table
# ============================================
slide13 = prs.slides[12]
for shape in slide13.shapes:
    if shape.has_table:
        table = shape.table
        # Clear all cells
        for row in table.rows:
            for cell in row.cells:
                cell.text = ""

# Save
output_path = "D:\\final_year_project\\project_ppt_batch_11_Updated.pptx"
prs.save(output_path)
print("Cleared tables on slides 2 and 13")