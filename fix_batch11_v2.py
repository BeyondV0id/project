#!/usr/bin/env python
"""Fix batch11 by properly replacing main content and clearing duplicate text boxes."""
from pptx import Presentation
from pptx.util import Pt, Inches

prs = Presentation("D:\\final_year_project\\project_ppt_batch_11_Updated.pptx")

def clear_text_frame(text_frame):
    """Clear all paragraphs except the first."""
    while len(text_frame.paragraphs) > 1:
        p = text_frame.paragraphs[-1]
        p._p.getparent().remove(p._p)
    for run in text_frame.paragraphs[0].runs:
        run.text = ""
    return text_frame.paragraphs[0]

def set_shape_text(shape, new_text):
    """Set all text in a shape to new_text."""
    if shape.has_text_frame:
        para = clear_text_frame(shape.text_frame)
        para.runs[0].text = new_text

def clear_shape_text(shape):
    """Clear all text in a shape."""
    if shape.has_text_frame:
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                run.text = ""

def get_shape_text_length(shape):
    """Get total text length in a shape."""
    if not shape.has_text_frame:
        return 0
    total = 0
    for para in shape.text_frame.paragraphs:
        for run in para.runs:
            if run.text:
                total += len(run.text)
    return total

# For each slide, find the shape with the most text (main content) and update it
# Clear all other text shapes

# ============================================
# SLIDE 2 - Index
# ============================================
slide2 = prs.slides[1]
main_shape = None
max_len = 0
for shape in slide2.shapes:
    if shape.has_text_frame:
        l = get_shape_text_length(shape)
        if l > max_len:
            max_len = l
            main_shape = shape
# Clear all, then set main
for shape in slide2.shapes:
    if shape.has_text_frame:
        clear_shape_text(shape)
if main_shape:
    set_shape_text(main_shape, (
        "1.  Abstract\n"
        "2.  Introduction\n"
        "3.  Literature Survey\n"
        "4.  Challenges in Food Recognition\n"
        "5.  Our Approach: How We Solve Each Challenge\n"
        "6.  Motivation — Why This Matters\n"
        "7.  Objectives\n"
        "8.  Problem Statement\n"
        "9.  System Workflow\n"
        "10. Methodology — The Pipeline\n"
        "11. Requirements\n"
        "12. Datasets\n"
        "13. Project Status\n"
        "14. Roadmap\n"
        "15. Conclusion\n"
        "16. References"
    ))

# ============================================
# SLIDE 3 - Abstract
# ============================================
slide3 = prs.slides[2]
main_shape = None
max_len = 0
for shape in slide3.shapes:
    if shape.has_text_frame:
        l = get_shape_text_length(shape)
        if l > max_len:
            max_len = l
            main_shape = shape
for shape in slide3.shapes:
    if shape.has_text_frame:
        clear_shape_text(shape)
if main_shape:
    set_shape_text(main_shape, (
        "Today's calorie-tracking apps give you one number for an entire meal. "
        "For a mixed Indian plate — rice, dal, chapati, sabzi — that single number is "
        "wrong by design, because every item has a different calorie density.\n\n"
        "We are building a system that changes this. From a single meal photo, it:\n"
        "• Separates the plate into individual food items\n"
        "• Estimates how many grams of each item are on the plate\n"
        "• Looks up verified nutrition data from India's official food tables (IFCT 2017) and USDA\n"
        "• Reports calories and macros per item, plus a confidence score so you know what's reliable\n\n"
        "Key difference: the AI only identifies food — it never guesses calories. All numbers come from "
        "verified databases, calculated in plain code. When the system isn't sure, it asks you a quick "
        "question instead of guessing. Built for Indian meals first, runs on a regular laptop."
    ))

# ============================================
# SLIDE 4 - Introduction
# ============================================
slide4 = prs.slides[3]
main_shape = None
max_len = 0
for shape in slide4.shapes:
    if shape.has_text_frame:
        l = get_shape_text_length(shape)
        if l > max_len:
            max_len = l
            main_shape = shape
for shape in slide4.shapes:
    if shape.has_text_frame:
        clear_shape_text(shape)
if main_shape:
    set_shape_text(main_shape, (
        "A mixed meal is not a single dish — but today's apps treat it like one.\n\n"
        "THE PROBLEM\n"
        "Photo logging is fast and convenient. But when you snap a thali, the app "
        "collapses 3–8 different foods into one guessed entry. A single serving-size "
        "mistake can throw off the calorie count by 50% or more.\n\n"
        "WHY IT'S HARD\n"
        "• No depth in a 2D photo — we can't see how tall the dal is\n"
        "• Foods hide under each other (chicken under rice)\n"
        "• The same food has wildly different calories depending on how it's cooked "
        "(cooked rice: 130 kcal/100g | raw rice: 345 kcal/100g)\n"
        "• Indian dishes and regional names (pappu, koora, annam) aren't in global databases\n\n"
        "WHAT WE'RE BUILDING\n"
        "A system that sees the plate the way a nutritionist would — component by component — "
        "and grounds every number in a verified food-composition table. No hallucinated calories. "
        "Honest uncertainty. Runs offline on your laptop."
    ))

# ============================================
# SLIDE 10 - Objectives
# ============================================
slide10 = prs.slides[9]
main_shape = None
max_len = 0
for shape in slide10.shapes:
    if shape.has_text_frame:
        l = get_shape_text_length(shape)
        if l > max_len:
            max_len = l
            main_shape = shape
for shape in slide10.shapes:
    if shape.has_text_frame:
        clear_shape_text(shape)
if main_shape:
    set_shape_text(main_shape, (
        "WHAT WE AIM TO ACHIEVE\n\n"
        "1. SEE THE PLATE CLEARLY\n"
        "   Identify 3–8 food items on a mixed plate with their boundaries and "
        "   preparation state (raw, cooked, fried, gravy).\n\n"
        "2. ESTIMATE PORTIONS IN GRAMS\n"
        "   Use the plate as a scale reference to calculate how many grams of each "
        "   item are present, with a realistic uncertainty range.\n\n"
        "3. GROUND EVERY NUMBER IN VERIFIED DATA\n"
        "   Every calorie and macro value traces back to IFCT 2017 or USDA — "
        "   nothing comes from the AI's memory.\n\n"
        "4. CALCULATE HONESTLY\n"
        "   Pure Python arithmetic: nutrients per 100g × grams ÷ 100. Missing values "
        "   stay missing — never silently become zero.\n\n"
        "5. REPORT CONFIDENCE YOU CAN TRUST\n"
        "   A calibrated reliability score (not the AI's internal confidence) so you "
        "   know which items are solid and which are uncertain.\n\n"
        "6. ASK ONLY WHEN IT MATTERS\n"
        "   At most 2 targeted questions per meal, only for the items where your "
        "   answer would actually change the result.\n\n"
        "7. STAY FAST AND LIGHTWEIGHT\n"
        "   Results in under 20 seconds on a regular CPU laptop. Works offline for demos."
    ))

# ============================================
# SLIDE 11 - Problem Statement
# ============================================
slide11 = prs.slides[10]
main_shape = None
max_len = 0
for shape in slide11.shapes:
    if shape.has_text_frame:
        l = get_shape_text_length(shape)
        if l > max_len:
            max_len = l
            main_shape = shape
for shape in slide11.shapes:
    if shape.has_text_frame:
        clear_shape_text(shape)
if main_shape:
    set_shape_text(main_shape, (
        "THE PROBLEM\n"
        "Calorie-tracking apps collapse a mixed meal into one dish and one guessed "
        "number. For an Indian thali (rice, dal, chapati, 2–3 curries), that single "
        "number hides large errors, can't be verified, and gives no hint of how much "
        "to trust it.\n\n"
        "WHAT WE'RE BUILDING\n"
        "A system that takes one meal photo and produces a component-level nutrition "
        "report — not a single guess.\n\n"
        "INPUT: One smartphone photo of a mixed Indian meal (3–8 items), plus optional "
        "notes like plate size or meal type. Text or voice input supported.\n\n"
        "OUTPUT: For each food item — name, estimated grams (with range), calories, "
        "protein, carbs, fat, confidence score, and the database source. Plus a meal "
        "total with an overall reliability indicator.\n\n"
        "HOW WE MEASURE SUCCESS\n"
        "• Component identification accuracy (F1 score)\n"
        "• Portion estimation error in grams\n"
        "• Calorie error vs. weighed ground truth\n"
        "• Calibration: does 80% confidence mean 80% accurate?\n"
        "• Speed: under 20 seconds on a regular laptop\n\n"
        "NON-NEGOTIABLE: This is an informational self-tracking tool — not medical, "
        "clinical, or diagnostic advice. Every result carries this disclaimer."
    ))

# ============================================
# SLIDE 13 - Methodology Pipeline
# ============================================
slide13 = prs.slides[12]
main_shape = None
max_len = 0
for shape in slide13.shapes:
    if shape.has_text_frame:
        l = get_shape_text_length(shape)
        if l > max_len:
            max_len = l
            main_shape = shape
for shape in slide13.shapes:
    if shape.has_text_frame:
        clear_shape_text(shape)
if main_shape:
    set_shape_text(main_shape, (
        "THE 9-STAGE PIPELINE: FROM PHOTO TO VERIFIED REPORT\n\n"
        "1. INPUT & CONTEXT\n"
        "   Photo uploaded; optional plate size, meal type, or diet goals noted.\n\n"
        "2. QUALITY CHECK & ROUTING\n"
        "   Blur/exposure validated; simple vs. complex plate routed to appropriate depth.\n\n"
        "3. SEE THE COMPONENTS (Perception)\n"
        "   Vision model finds each food item, draws its region, labels its state "
        "(cooked/raw/fried/gravy). CRITICAL: The model NEVER outputs calories or grams.\n\n"
        "4. LOOK UP VERIFIED NUTRITION (RAG)\n"
        "   Hybrid search matches each item to IFCT 2017 / USDA. Physical-state filter "
        "ensures cooked rice matches cooked rice (130 kcal), not raw (345 kcal).\n\n"
        "5. ESTIMATE PORTION MASS\n"
        "   Plate diameter → pixel scale → food area → heap volume × density → grams "
        "with an 80% confidence interval.\n\n"
        "6. CALCULATE NUTRITION\n"
        "   Pure Python: (nutrient per 100g × grams ÷ 100) for each item. Sum for meal total.\n\n"
        "7. SANITY CHECK (Critic)\n"
        "   Automatic veto on impossible portions or macro ratios before you see results.\n\n"
        "8. CALIBRATED CONFIDENCE\n"
        "   7 pipeline signals fused → isotonic regression → honest reliability score.\n\n"
        "9. DECIDE & CLARIFY\n"
        "   High confidence? Deliver report. Low confidence? Ask 1–2 targeted questions, "
        "recalculate only what's affected.\n\n"
        "10. PERSIST EVERYTHING\n"
        "   Full audit trail: model version, prompt version, KB version, compute version — "
        "deterministic replay guaranteed."
    ))

# ============================================
# SLIDE 14 - Core Mechanisms
# ============================================
slide14 = prs.slides[13]
main_shape = None
max_len = 0
for shape in slide14.shapes:
    if shape.has_text_frame:
        l = get_shape_text_length(shape)
        if l > max_len:
            max_len = l
            main_shape = shape
for shape in slide14.shapes:
    if shape.has_text_frame:
        clear_shape_text(shape)
if main_shape:
    set_shape_text(main_shape, (
        "FOUR CORE MECHANISMS THAT MAKE IT WORK\n\n"
        "1. VISION THAT DOESN'T HALLUCINATE\n"
        "   The AI is constrained by a strict output schema: label, bounding box, "
        "physical state, relative size. ZERO numeric fields. It literally cannot output "
        "a calorie number.\n\n"
        "2. RETRIEVAL THAT KNOWS RAW FROM COOKED\n"
        "   Dense + keyword search over IFCT 2017 & USDA, fused with reciprocal rank "
        "fusion. A physical-state filter rejects mismatches — cooked rice never matches "
        "raw rice. Hard cutoff at 0.55 similarity: below that, we say 'uncertain,' not "
        "'here's a guess.'\n\n"
        "3. PORTIONS FROM GEOMETRY, NOT GUESSES\n"
        "   Plate diameter in the photo gives us pixels-per-cm. Segmented food area × "
        "category-specific heap height × food density = grams. Log-normal confidence "
        "interval reflects real uncertainty.\n\n"
        "4. CONFIDENCE THAT'S STATISTICALLY HONEST\n"
        "   7 observable signals (identity match, retrieval score, portion plausibility, "
        "critic verdict, image quality, state certainty, visibility) → weighted fusion → "
        "isotonic calibration on held-out weighed meals. The result: when we say 80% "
        "confidence, we're right ~80% of the time.\n\n"
        "WHY STATE FILTERING MATTERS:\n"
        "Cooked white rice = 130 kcal/100g | Raw rice = 345 kcal/100g. Without the filter, "
        "a basic staple is overestimated by 2.6×. This is the single largest systematic "
        "error in the field — and we eliminate it by design."
    ))

# ============================================
# SLIDE 15 - Requirements
# ============================================
slide15 = prs.slides[14]
main_shape = None
max_len = 0
for shape in slide15.shapes:
    if shape.has_text_frame:
        l = get_shape_text_length(shape)
        if l > max_len:
            max_len = l
            main_shape = shape
for shape in slide15.shapes:
    if shape.has_text_frame:
        clear_shape_text(shape)
if main_shape:
    set_shape_text(main_shape, (
        "WHAT THE SYSTEM MUST DO (Functional)\n\n"
        "• Break a mixed plate into 3–8 items with regions and prep states\n"
        "• Estimate grams per item using the plate as a scale reference\n"
        "• Match each item to IFCT 2017 / USDA with raw/cooked filtering\n"
        "• Calculate nutrition in pure Python — missing values stay missing\n"
        "• Sanity-check portions and macros before showing results\n"
        "• Report a calibrated confidence score you can trust\n"
        "• Ask at most 2 questions, only when your answer changes the result\n"
        "• Save full audit trail for exact reproducibility\n\n"
        "QUALITY & CONSTRAINTS (Non-Functional)\n\n"
        "• Accuracy: Component F1 ≥ 0.80 | Calorie MAPE ≤ 18% | Calibration error ≤ 0.10\n"
        "• Speed: Median ≤ 8 sec, 95th percentile ≤ 20 sec on complex plates\n"
        "• Cost: ≤ $0.01 per analysis\n"
        "• Offline-first: Full pipeline runs without internet (MOCK_MODE)\n"
        "• Zero hallucination: Every number traces to a database row\n"
        "• Runs on: Standard Windows laptop, 8 GB RAM, CPU only\n"
        "• Privacy: Photos and data stay local; user controls deletion\n"
        "• Safety: Non-medical disclaimer on every result"
    ))

# ============================================
# SLIDE 17 - Project Status
# ============================================
slide17 = prs.slides[16]
main_shape = None
max_len = 0
for shape in slide17.shapes:
    if shape.has_text_frame:
        l = get_shape_text_length(shape)
        if l > max_len:
            max_len = l
            main_shape = shape
for shape in slide17.shapes:
    if shape.has_text_frame:
        clear_shape_text(shape)
if main_shape:
    set_shape_text(main_shape, (
        "WHERE WE ARE TODAY\n\n"
        "✅ PHASE 1 COMPLETE — FOUNDATION BUILT\n"
        "All the 'plumbing' is done and tested:\n"
        "• Database design (12 tables) — stores foods, nutrients, analyses, user feedback\n"
        "• Knowledge base — IFCT 2017 (528 Indian foods), USDA (~8,000 foods), loaded and searchable\n"
        "• Vector search index — finds the right food record even with regional names\n"
        "• API contracts — exact data shapes for every request and response\n"
        "• Evaluation plan — how we'll measure success, on what data\n\n"
        "📦 DATA ASSETS READY\n"
        "• IFCT 2017 with ~800 regional aliases (Telugu, Hindi, transliterated)\n"
        "• USDA Foundation Foods as global fallback\n"
        "• Indian Thali Dataset (7,900 images) for training segmentation\n"
        "• Weight Estimation Dataset (1,400 images) for portion baselines\n"
        "• Nutrition5k (5,000 plates with depth) for geometry validation\n"
        "• Our gold_v1: 150 photos of 60 weighed Indian meals — our report card\n\n"
        "🔄 PHASE 2 IN PROGRESS — CONNECTING THE PIECES\n"
        "Building the walking skeleton: upload photo → get component nutrition report.\n"
        "Current focus: portion geometry (plate → pixels → grams), confidence calibration, "
        "and kitchen weighing sessions to expand gold_v1.\n\n"
        "📍 NEXT MILESTONE\n"
        "End-to-end run on first 20 gold_v1 meals in offline mock mode — fully reproducible."
    ))

# ============================================
# SLIDE 18 - Roadmap
# ============================================
slide18 = prs.slides[17]
main_shape = None
max_len = 0
for shape in slide18.shapes:
    if shape.has_text_frame:
        l = get_shape_text_length(shape)
        if l > max_len:
            max_len = l
            main_shape = shape
for shape in slide18.shapes:
    if shape.has_text_frame:
        clear_shape_text(shape)
if main_shape:
    set_shape_text(main_shape, (
        "OUR ROADMAP\n\n"
        "PHASE 1 — FOUNDATION          ✅ DONE\n"
        "Architecture, database schema, dual-index RAG design, API contracts, evaluation plan.\n\n"
        "PHASE 2 — WALKING SKELETON    🔄 IN PROGRESS\n"
        "Mock pipeline end-to-end; Streamlit UI; offline deterministic execution.\n"
        "Sprints 3–4: Image upload → perception → deterministic nutrition math.\n"
        "Sprints 5–6: Portion geometry (plate → area → volume → grams).\n\n"
        "PHASE 3 — LIVE AI & CALIBRATION   📋 PLANNED\n"
        "Live Gemini 2.5 Flash integration; 7-signal isotonic calibration; "
        "active clarification loop (targeted questions).\n"
        "Sprints 7–8: Calibration fitting on weighed meals; question triggers.\n\n"
        "PHASE 4 — EVALUATION & REPORT   📋 PLANNED\n"
        "Full gold_v1 benchmark; comparative baselines; final thesis documentation.\n"
        "Sprints 9–10: Evaluation, ablation studies, write-up.\n\n"
        "⚠️ CRITICAL PATH\n"
        "Kitchen weighing sessions — every evaluation number depends on ground-truth mass data."
    ))

# ============================================
# SLIDE 19 - Conclusion
# ============================================
slide19 = prs.slides[18]
main_shape = None
max_len = 0
for shape in slide19.shapes:
    if shape.has_text_frame:
        l = get_shape_text_length(shape)
        if l > max_len:
            max_len = l
            main_shape = shape
for shape in slide19.shapes:
    if shape.has_text_frame:
        clear_shape_text(shape)
if main_shape:
    set_shape_text(main_shape, (
        "WHAT MAKES THIS DIFFERENT\n\n"
        "ERROR DECOMPOSITION\n"
        "We don't just chase a lower calorie error. We break it into four independent "
        "pieces — identity, mass, grounding, calibration — and solve each with a "
        "dedicated, measurable component.\n\n"
        "GROUNDING BY CONSTRUCTION\n"
        "The AI sees food; it never predicts numbers. Every calorie comes from "
        "IFCT 2017 / USDA, aggregated in unit-tested Python. Zero hallucination path.\n\n"
        "HONESTY AS A FEATURE\n"
        "Calibrated confidence bands + targeted clarification = no silent overconfident "
        "guesses. You always know what's solid and what's uncertain.\n\n"
        "BUILT FOR INDIAN PLATES FIRST\n"
        "~800 regional aliases, state-filtered retrieval, composite-dish recipes — "
        "not an afterthought, the primary design target.\n\n"
        "WHERE WE STAND\n"
        "Phase 1 (data, architecture, contracts) complete. Walking skeleton underway.\n\n"
        "WHAT'S NEXT\n"
        "• 3D volume from video (not just single photos)\n"
        "• Wearable glucose correlation for personal calibration\n"
        "• Multi-regional recipe coverage\n\n"
        "IMMEDIATE GOAL: End-to-end offline demo on 20 weighed thali meals."
    ))

# Save
output_path = "D:\\final_year_project\\project_ppt_batch_11_Updated.pptx"
prs.save(output_path)
print(f"Saved to {output_path}")