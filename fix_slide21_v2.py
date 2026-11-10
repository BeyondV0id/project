#!/usr/bin/env python
"""Fix duplicate critical path on slide 21 by clearing the extra text box."""
from pptx import Presentation

prs = Presentation('D:\\final_year_project\\Adaptive_Food_Recognition_Final_Updated.pptx')
slide21 = prs.slides[20]

# Shape 5 has the duplicate "Critical path" - clear it
shape5 = slide21.shapes[5]
if shape5.has_text_frame:
    for para in shape5.text_frame.paragraphs:
        for run in para.runs:
            run.text = ""

output_path = 'D:\\final_year_project\\Adaptive_Food_Recognition_Final_Updated.pptx'
prs.save(output_path)
print("Fixed slide 21 - cleared duplicate critical path text box")