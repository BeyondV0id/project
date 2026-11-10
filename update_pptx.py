#!/usr/bin/env python
"""Update the Adaptive Food Recognition PPTX with the requested changes."""
from pptx import Presentation
from pptx.util import Pt

prs = Presentation("D:\\final_year_project\\Adaptive_Food_Recognition_Final.pptx")

# Helper to find and replace text in a slide
def replace_text_in_slide(slide, old_text, new_text):
    """Replace text in all text frames in a slide."""
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    if old_text in run.text:
                        run.text = run.text.replace(old_text, new_text)
        # Also check grouped shapes
        if shape.shape_type == 6:  # GROUP
            for subshape in shape.shapes:
                if subshape.has_text_frame:
                    for para in subshape.text_frame.paragraphs:
                        for run in para.runs:
                            if old_text in run.text:
                                run.text = run.text.replace(old_text, new_text)

def replace_full_paragraph(slide, search_text, new_paragraphs):
    """Replace a full paragraph that contains search_text with new_paragraphs (list of strings)."""
    for shape in slide.shapes:
        if shape.has_text_frame:
            for i, para in enumerate(shape.text_frame.paragraphs):
                if search_text in para.text:
                    # Clear existing runs
                    for run in para.runs:
                        run.text = ""
                    # Set first run to first paragraph
                    if new_paragraphs:
                        para.runs[0].text = new_paragraphs[0] if para.runs else ""
                        # Add remaining paragraphs
                        for j, new_text in enumerate(new_paragraphs[1:], 1):
                            if j < len(para.runs):
                                para.runs[j].text = new_text
                            else:
                                new_run = para.add_run()
                                new_run.text = new_text
                    return True
    return False

def set_shape_text(shape, new_text):
    """Set all text in a shape to new_text."""
    if shape.has_text_frame:
        # Clear all paragraphs except first
        while len(shape.text_frame.paragraphs) > 1:
            p = shape.text_frame.paragraphs[-1]
            p._p.getparent().remove(p._p)
        # Set first paragraph
        para = shape.text_frame.paragraphs[0]
        for run in para.runs:
            run.text = ""
        para.runs[0].text = new_text

# ============================================
# SLIDE 11 - Problem Statement (refine wording)
# ============================================
slide11 = prs.slides[10]  # 0-indexed

# Find the problem statement text box and replace it
for shape in slide11.shapes:
    if shape.has_text_frame:
        full_text = ""
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                full_text += run.text
        if "Calorie-tracking apps treat a whole meal" in full_text:
            # Clear all paragraphs
            while len(shape.text_frame.paragraphs) > 1:
                p = shape.text_frame.paragraphs[-1]
                p._p.getparent().remove(p._p)
            
            # Set new problem statement
            para = shape.text_frame.paragraphs[0]
            for run in para.runs:
                run.text = ""
            para.runs[0].text = (
                "Calorie-tracking apps treat a mixed meal as a single dish and return one number "
                "from a guessed serving size. For a typical Indian thali with rice, dal, chapati, "
                "and multiple curries, this approach hides large errors, cannot be verified against "
                "ground truth, and gives users no meaningful indication of how far to trust the result. "
                "The problem addressed here is to design, implement, and evaluate a system that takes "
                "one meal photograph (along with optional text or speech context from the user), "
                "separates the plate into individual food components, estimates the mass of each "
                "component, and grounds every nutrient value in verified food-composition tables "
                "(IFCT 2017 / USDA). The system reports component-level and meal-level nutrition "
                "with a calibrated confidence score, and asks the user for clarification only when "
                "genuinely uncertain."
            )
            break

# ============================================
# SLIDE 16 - Functional Requirements
# ============================================
slide16 = prs.slides[15]

for shape in slide16.shapes:
    if shape.has_text_frame:
        full_text = ""
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                full_text += run.text
        if "Split a plate into" in full_text:
            # Clear all paragraphs
            while len(shape.text_frame.paragraphs) > 1:
                p = shape.text_frame.paragraphs[-1]
                p._p.getparent().remove(p._p)
            
            para = shape.text_frame.paragraphs[0]
            for run in para.runs:
                run.text = ""
            para.runs[0].text = (
                "• Accept a meal photo plus optional user context via text or speech input\n"
                "• Split a plate into 3–8 food components with their physical states (raw/cooked)\n"
                "• Estimate the mass of each component with a confidence range (grams)\n"
                "• Match each component to IFCT 2017 or USDA records using hybrid RAG with a state filter\n"
                "• Calculate nutrients in pure Python; missing values remain NULL (never zero)\n"
                "• Orchestrate the pipeline with LangGraph for deterministic, observable execution\n"
                "• Ask a few targeted clarification questions only when confidence is low\n"
                "• Show a clear report with values, ranges, sources, and calibrated confidence"
            )
            break

# ============================================
# SLIDE 18 - Technology Stack (add LangGraph)
# ============================================
slide18 = prs.slides[17]

for shape in slide18.shapes:
    if shape.has_text_frame:
        full_text = ""
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                full_text += run.text
        if "The system is written in Python" in full_text:
            # Clear all paragraphs
            while len(shape.text_frame.paragraphs) > 1:
                p = shape.text_frame.paragraphs[-1]
                p._p.getparent().remove(p._p)
            
            para = shape.text_frame.paragraphs[0]
            for run in para.runs:
                run.text = ""
            para.runs[0].text = (
                "• Python with Pydantic v2 data schemas\n"
                "• Gemini 2.5 Flash as the vision–language model for perception only\n"
                "• LangGraph for pipeline orchestration (deterministic, observable, interruptible)\n"
                "• SQLite (WAL mode) for records; Chroma for vector embeddings\n"
                "• Retrieval: bge-small-en-v1.5 embeddings + BM25 + reciprocal rank fusion + cross-encoder reranker\n"
                "• Isotonic regression for confidence calibration\n"
                "• Streamlit web UI with text and speech input support\n"
                "• Runs on a standard Windows laptop, CPU-only, 8 GB RAM"
            )
            break

# ============================================
# SLIDE 20 - Status of the Project (update)
# ============================================
slide20 = prs.slides[19]

for shape in slide20.shapes:
    if shape.has_text_frame:
        full_text = ""
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                full_text += run.text
        if "Phase 1 is complete" in full_text:
            # Clear all paragraphs
            while len(shape.text_frame.paragraphs) > 1:
                p = shape.text_frame.paragraphs[-1]
                p._p.getparent().remove(p._p)
            
            para = shape.text_frame.paragraphs[0]
            for run in para.runs:
                run.text = ""
            para.runs[0].text = (
                "• Phase 1 complete: specification, data modelling, database schema, knowledge-base "
                "ingestion, API contracts, and evaluation plan — all implemented in code\n"
                "• IFCT 2017, USDA, Indian Thali, Weight, and Nutrition5k datasets prepared and loaded\n"
                "• Data model (SQL DDL) and architecture (layers, routing tiers, ADRs) are coded and tested\n"
                "• Phase 2 in progress: pipeline skeleton with LangGraph, portion geometry, confidence "
                "tuning, and kitchen weighing sessions for ground truth"
            )
            break

# ============================================
# SLIDE 21 - Status of the Project — Roadmap (update)
# ============================================
slide21 = prs.slides[20]

for shape in slide21.shapes:
    if shape.has_text_frame:
        full_text = ""
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                full_text += run.text
        if "Phase 1, specification and data model" in full_text:
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

# Save the updated presentation
output_path = "D:\\final_year_project\\Adaptive_Food_Recognition_Final_Updated.pptx"
prs.save(output_path)
print(f"Saved to {output_path}")