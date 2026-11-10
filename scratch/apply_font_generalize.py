"""
apply_font_generalize.py
  - Re-extracts from project_ppt_batch_11_v2.pptx (the already-modified deck)
  - Applies Times New Roman 24pt to EVERY text run (titles get 32pt, subtitles 24pt,
    table header rows 24pt, body/table cells 24pt, disclaimer keeps 10pt, page number keeps 11pt)
  - Generalises verbose table cell content (trims to concise bullet-point style)
  - Increases table row heights so 24pt text is comfortable
  - Re-packs to project_ppt_batch_11_v3.pptx
"""

import os, re, zipfile, shutil
import defusedxml.minidom

NS_A  = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_P  = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_R  = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

SRC_PPTX   = "D:/final_year_project/project_ppt_batch_11_v2.pptx"
UNPACKED   = "D:/final_year_project/unpacked_v3"
OUT_PPTX   = "D:/final_year_project/project_ppt_batch_11_v3.pptx"
SLIDES_DIR = os.path.join(UNPACKED, "ppt/slides")

TITLE_SZ   = "3200"   # 32 pt
BODY_SZ    = "2400"   # 24 pt
SMALL_SZ   = "1100"   # ~11 pt  (page numbers, disclaimer — keep small)
FONT_NAME  = "Times New Roman"

# ── helpers ──────────────────────────────────────────────────────────────────

def unpack(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    with zipfile.ZipFile(src) as z:
        z.extractall(dst)

def read_xml(path):
    with open(path, "rb") as f:
        return defusedxml.minidom.parseString(f.read())

def write_xml(doc, path):
    xml_bytes = doc.toxml(encoding="utf-8")
    with open(path, "wb") as f:
        f.write(xml_bytes)

def get_text(node):
    parts = []
    for t in node.getElementsByTagNameNS(NS_A, "t"):
        if t.firstChild:
            parts.append(t.firstChild.nodeValue or "")
    return "".join(parts).strip()

def set_rpr_font(rPr, sz, bold=None):
    """Set font size + Times New Roman on a <a:rPr> or <a:endParaRPr> node."""
    rPr.setAttribute("sz", sz)
    # Remove old latin/ea/cs children
    doc = rPr.ownerDocument
    for tag in ("latin", "ea", "cs"):
        for n in list(rPr.getElementsByTagNameNS(NS_A, tag)):
            rPr.removeChild(n)
    lat = doc.createElementNS(NS_A, "a:latin")
    lat.setAttribute("typeface", FONT_NAME)
    lat.setAttribute("pitchFamily", "18")
    lat.setAttribute("charset", "0")
    rPr.appendChild(lat)
    if bold is not None:
        rPr.setAttribute("b", "1" if bold else "0")

def is_tiny(sz_str):
    """Return True if the size should stay small (page-number / disclaimer)."""
    try:
        return int(sz_str) <= 1100
    except ValueError:
        return False

def classify_sp(sp):
    """Heuristic: return 'title', 'subtitle', or 'body' for a shape."""
    name = ""
    for cnvpr in sp.getElementsByTagNameNS(NS_P, "cNvPr"):
        name = cnvpr.getAttribute("name").lower()
        break
    all_text = get_text(sp)
    # slide title is usually the first big text shape
    if "text 0" in name or name == "":
        return "title"
    return "body"

# ── generalise cell text ──────────────────────────────────────────────────────

GENERALISE_MAP = [
    # long verbose phrases → concise version
    (r"Accepts meal image, optional context \(plate diameter, meal type, diet goals\)\.",
     "Accepts meal image and optional user context (plate size, meal type)."),
    (r"Captures user context to constrain portion estimation\.",
     "Provides context for portion estimation."),
    (r"Validates format, checks blur/lighting, assigns routing tier \(T0, T1, T2\)\.",
     "Validates image quality; routes to appropriate processing tier."),
    (r"Fails fast on unusable photos; matches pipeline depth to complexity\.",
     "Rejects unusable images early; adapts depth to scene complexity."),
    (r"Detects visual components, bounding boxes, physical states, relative areas\.",
     "Detects food components, bounding regions, and physical states."),
    (r"Strict rule: VLM emits labels and coordinates only; never calories or grams\.",
     "VLM outputs labels and regions only — no calorie or mass values."),
    (r"Dense \+ BM25 hybrid search over IFCT 2017 & USDA; state-filtered reranking\.",
     "Hybrid BM25 + dense search over IFCT 2017 & USDA with state filtering."),
    (r"Every number grounded in peer-reviewed composition tables \(cutoff 0\.55\)\.",
     "All values grounded in verified composition tables (threshold 0.55)."),
    (r"Plate scale anchor → projected area → heap volume → food density → grams\.",
     "Scale anchor → area → volume → density → mass (g)."),
    (r"Scale-anchored geometry converts 2D pixels to mass with 80% CI\.",
     "Geometric inference converts pixels to mass with 80 % confidence."),
    (r"Scales per-100 g database nutrients by estimated mass; sums overall totals\.",
     "Scales per-100 g nutrients by mass; sums component totals."),
    (r"Pure Python arithmetic outside LLM; unit-tested; NULL values preserved\.",
     "Deterministic Python arithmetic; no LLM in the calculation path."),
    (r"Fuses 7 pipeline signals into a single score; calibrated via isotonic regression\.",
     "7-signal fusion calibrated via isotonic regression."),
    (r"Catches hallucinated portions or impossible macronutrient ratios\.",
     "Catches physically impossible portion or macro predictions."),
    (r"Triggers targeted user clarification when confidence is below threshold\.",
     "Asks targeted questions only for low-confidence components."),
    (r"Ranked by expected error reduction.*?max 2 questions per round, 2 rounds",
     "Max 2 questions per round, up to 2 rounds."),
    (r"Presents validated nutritional report to the user\.",
     "Delivers validated nutritional report."),
    (r"Persists execution provenance.*?deterministic re-runs\.",
     "Logs full provenance for deterministic re-runs."),
    # Literature survey column text generalisation
    (r"Proves external database grounding \(RAG/IFCT\) and separate deterministic math are mathematically mandatory\.",
     "Shows that external database grounding and deterministic math are essential."),
    (r"Direct empirical justification for our decoupled perception-first pipeline; proves two-step beats end-to-end VLM guessing\.",
     "Justifies two-step perception pipeline over end-to-end VLM estimation."),
    (r"Direct foundation for Indian platter segmentation and portion mass baselines on mixed regional foods\.",
     "Provides datasets for Indian platter segmentation and portion estimation."),
    (r"Architectural blueprint for our IFCT 2017 vector retrieval and RAG grounding pipeline\.",
     "Blueprint for vector retrieval and RAG-based nutrient grounding."),
    (r"Demonstrates need for scale-anchored geometry and physical density priors in portion estimation\.",
     "Highlights need for scale-anchored geometry and density priors."),
    (r"Tested 17 modern VLMs on Nutrition5k\. Discovered the .Ground-Truth Paradox.: VLMs recognize ingredients well \(~60% AP\) but fail dramatically at nutritional math even when given true ingredients\.",
     "VLMs recognise ingredients (~60 % AP) but fail at nutritional arithmetic — grounding is mandatory."),
    (r"Splits analysis into visual component decomposition \(using SAM2/FoodSAM\) followed by nutritional reasoning\.",
     "Two-step: visual decomposition (SAM2/FoodSAM), then nutritional reasoning."),
    (r"Retrieves exact nutritional values from vector databases to eliminate LLM parametric hallucination\.",
     "Vector DB retrieval eliminates LLM hallucination in nutrient values."),
    (r"Highlights limitations of 2D RGB models lacking depth sensors and suffering cross-modal scaling noise\.",
     "2D RGB models need scale anchors; depth absence causes large errors."),
    (r"Addresses multi-item cultural platters packed with overlapping curries, dal, rice, and flatbreads\.",
     "Covers dense multi-item platters (curries, dal, rice, flatbreads)."),
]

def generalise_text(text):
    for pattern, replacement in GENERALISE_MAP:
        text = re.sub(pattern, replacement, text, flags=re.DOTALL)
    return text

def generalise_run(r_node):
    for t in r_node.getElementsByTagNameNS(NS_A, "t"):
        if t.firstChild:
            original = t.firstChild.nodeValue or ""
            new_val = generalise_text(original)
            if new_val != original:
                t.firstChild.nodeValue = new_val

# ── per-slide processing ──────────────────────────────────────────────────────

def process_slide(path, slide_num):
    doc = read_xml(path)
    changed = False

    # 1. Text shapes ──────────────────────────────────────────────────────────
    sp_list = doc.getElementsByTagNameNS(NS_P, "sp")
    for idx, sp in enumerate(sp_list):
        # decide target size for this shape
        name_node = sp.getElementsByTagNameNS(NS_P, "cNvPr")
        name = name_node[0].getAttribute("name").lower() if name_node else ""

        # shape containing "Text 0" == title; "Shape N" == decorative bar; others == body
        is_title = ("text 0" in name)
        is_decorator = ("shape" in name)

        for rPr in sp.getElementsByTagNameNS(NS_A, "rPr"):
            sz = rPr.getAttribute("sz") if rPr.hasAttribute("sz") else "0"
            if is_tiny(sz):
                continue  # keep page number and disclaimer sizes
            target_sz = TITLE_SZ if is_title else BODY_SZ
            set_rpr_font(rPr, target_sz)
            changed = True

        for endRpr in sp.getElementsByTagNameNS(NS_A, "endParaRPr"):
            sz = endRpr.getAttribute("sz") if endRpr.hasAttribute("sz") else "0"
            if is_tiny(sz):
                continue
            target_sz = TITLE_SZ if is_title else BODY_SZ
            set_rpr_font(endRpr, target_sz)
            changed = True

        # Generalise run text in body shapes
        if not is_title and not is_decorator:
            for r in sp.getElementsByTagNameNS(NS_A, "r"):
                generalise_run(r)

    # 2. Tables ───────────────────────────────────────────────────────────────
    for tbl in doc.getElementsByTagNameNS(NS_A, "tbl"):
        rows = list(tbl.getElementsByTagNameNS(NS_A, "tr"))
        for row_idx, row in enumerate(rows):
            is_header = (row_idx == 0)
            # increase row height for 24 pt comfort
            cur_h = row.getAttribute("h") if row.hasAttribute("h") else "0"
            try:
                h_val = int(cur_h)
            except ValueError:
                h_val = 0
            # 1 pt = 12700 EMU; 24 pt body → ~40 pt row height = 508000 EMU minimum
            if h_val < 490000:
                row.setAttribute("h", "508000")
                changed = True

            for tc in row.getElementsByTagNameNS(NS_A, "tc"):
                for rPr in tc.getElementsByTagNameNS(NS_A, "rPr"):
                    sz = rPr.getAttribute("sz") if rPr.hasAttribute("sz") else "0"
                    if is_tiny(sz):
                        continue
                    set_rpr_font(rPr, BODY_SZ, bold=True if is_header else None)
                    changed = True
                for endRpr in tc.getElementsByTagNameNS(NS_A, "endParaRPr"):
                    sz = endRpr.getAttribute("sz") if endRpr.hasAttribute("sz") else "0"
                    if is_tiny(sz):
                        continue
                    set_rpr_font(endRpr, BODY_SZ)
                    changed = True
                # Generalise cell text
                for r in tc.getElementsByTagNameNS(NS_A, "r"):
                    generalise_run(r)

    if changed:
        write_xml(doc, path)
        print(f"  updated: {os.path.basename(path)}")

# ── repack ────────────────────────────────────────────────────────────────────

def repack(src_dir, out_path):
    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                abs_p = os.path.join(root, file)
                rel_p = os.path.relpath(abs_p, src_dir).replace("\\", "/")
                zf.write(abs_p, rel_p)
    print(f"\nRepacked → {out_path}")

# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Unpacking v2 ...")
    unpack(SRC_PPTX, UNPACKED)

    slide_files = sorted(
        [f for f in os.listdir(SLIDES_DIR) if f.startswith("slide") and f.endswith(".xml")],
        key=lambda x: int(re.search(r"\d+", x).group()),
    )
    print(f"Processing {len(slide_files)} slides ...")
    for i, sf in enumerate(slide_files, 1):
        process_slide(os.path.join(SLIDES_DIR, sf), i)

    print("\nRepacking ...")
    repack(UNPACKED, OUT_PPTX)
    print("Done.")
