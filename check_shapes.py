#!/usr/bin/env python
from pptx import Presentation

prs = Presentation('D:\\final_year_project\\project_ppt_batch_11_Updated.pptx')

# Check slide 2 shapes
slide2 = prs.slides[1]
print('=== SLIDE 2 SHAPES ===')
for i, shape in enumerate(slide2.shapes):
    if shape.has_text_frame:
        full_text = ''
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                full_text += run.text
        print(f'Shape {i}: len={len(full_text)} | "{full_text[:150]}"')

# Check slide 13 shapes
slide13 = prs.slides[12]
print('\n=== SLIDE 13 SHAPES ===')
for i, shape in enumerate(slide13.shapes):
    if shape.has_text_frame:
        full_text = ''
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                full_text += run.text
        print(f'Shape {i}: len={len(full_text)} | "{full_text[:150]}"')