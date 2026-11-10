"""
Modify project_ppt_batch_11.pptx:
1. Slide 5 (Literature Survey Recent Work): Change column header "Paper / Authors" -> "Paper",
   replace author-name cells in first column with the actual paper name.
2. Slide 6 (Literature Survey Gap Analysis): DELETE this slide entirely.
3. Slide 11 (Problem Statement): Add more text to the problem statement.
4. Slide 13 (Methodology 11-Stage Pipeline): Change to 9-Stage Pipeline,
   remove Critic Agent (stage 7) and Persistence stages, update slide title,
   update font to Times New Roman 24px, add index number, generalize content.
5. Apply Times New Roman font 24pt to all body text across relevant slides.
   Update index slide to reflect removal of gap analysis slide.
"""

import sys
import os
import re
import zipfile
import shutil

# Use defusedxml for safety
import defusedxml.minidom

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PRES = "http://schemas.openxmlformats.org/presentationml/2006/main"

UNPACKED = "D:/final_year_project/unpacked"
PPTX_SRC = "D:/final_year_project/project_ppt_batch_11.pptx"
PPTX_OUT = "D:/final_year_project/project_ppt_batch_11_v2.pptx"
SLIDES_DIR = os.path.join(UNPACKED, "ppt/slides")
PRES_XML = os.path.join(UNPACKED, "ppt/presentation.xml")

FONT_SIZE = "2400"   # 24pt in hundredths of a point
FONT_NAME = "Times New Roman"

def read_xml(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return defusedxml.minidom.parseString(content.encode("utf-8"))

def write_xml(doc, path):
    xml_str = doc.toxml(encoding="utf-8")
    # toxml returns bytes when encoding is specified
    with open(path, "wb") as f:
        f.write(xml_str)

def get_text_of_node(node):
    """Get all text content from an XML node."""
    texts = []
    for t in node.getElementsByTagNameNS(NS_A, "t"):
        if t.firstChild:
            texts.append(t.firstChild.nodeValue or "")
    return "".join(texts)

def set_run_text(r_node, text):
    """Replace text in a <a:r> run node."""
    for t in r_node.getElementsByTagNameNS(NS_A, "t"):
        if t.firstChild:
            t.firstChild.nodeValue = text
        else:
            t.appendChild(r_node.ownerDocument.createTextNode(text))
        break

def set_font_on_rpr(rPr_node, font_name=FONT_NAME, font_size=FONT_SIZE):
    """Apply Times New Roman and size to an <a:rPr> node."""
    rPr_node.setAttribute("sz", font_size)
    # Remove existing latin/ea/cs typeface children and replace
    doc = rPr_node.ownerDocument
    for tag in ["latin", "ea", "cs"]:
        existing = rPr_node.getElementsByTagNameNS(NS_A, tag)
        for node in list(existing):
            rPr_node.removeChild(node)
    # Add new latin typeface
    lat = doc.createElementNS(NS_A, "a:latin")
    lat.setAttribute("typeface", font_name)
    lat.setAttribute("pitchFamily", "18")
    lat.setAttribute("charset", "0")
    rPr_node.appendChild(lat)

def apply_font_to_slide(doc, skip_title=False):
    """Apply Times New Roman 24pt to all runs in slide except title if skip_title."""
    sp_list = doc.getElementsByTagNameNS(NS_P, "sp")
    for i, sp in enumerate(sp_list):
        # Skip slide number element (small font)
        # Heuristic: title is usually first non-shape, big font shape
        # We'll apply to all body text (non-title) text boxes
        name_attrs = sp.getAttribute("name") if sp.hasAttribute("name") else ""
        for rPr in sp.getElementsByTagNameNS(NS_A, "rPr"):
            # Skip if sz is very small (page number, disclaimer)
            sz = rPr.getAttribute("sz") if rPr.hasAttribute("sz") else "0"
            try:
                if int(sz) < 900:
                    continue  # skip tiny text
            except ValueError:
                pass
            set_font_on_rpr(rPr)
        # Also fix endParaRPr
        for endRpr in sp.getElementsByTagNameNS(NS_A, "endParaRPr"):
            sz = endRpr.getAttribute("sz") if endRpr.hasAttribute("sz") else "0"
            try:
                if int(sz) < 900:
                    continue
            except ValueError:
                pass
            endRpr.setAttribute("sz", FONT_SIZE)
            doc2 = endRpr.ownerDocument
            for tag in ["latin", "ea", "cs"]:
                existing = endRpr.getElementsByTagNameNS(NS_A, tag)
                for node in list(existing):
                    endRpr.removeChild(node)
            lat = doc2.createElementNS(NS_A, "a:latin")
            lat.setAttribute("typeface", FONT_NAME)
            lat.setAttribute("pitchFamily", "18")
            lat.setAttribute("charset", "0")
            endRpr.appendChild(lat)

# ============================
# 1. Modify Slide 5: Literature Survey Recent Work
# ============================
def modify_slide5():
    path = os.path.join(SLIDES_DIR, "slide5.xml")
    doc = read_xml(path)
    
    # Paper name data to replace author-name cells
    # Row 1: Wang et al -> paper title
    # Row 2: FoodDecom Framework (2025) -> paper title  
    # Row 3: Arora, Arun, Jawahar -> paper title
    # Row 4: NutriVisRAG (2025) -> paper title
    # Row 5: OmniFood8K (Yu et al., CVPR) -> paper title
    # Row 6: Teng, Min, Liu, Li -> paper title
    
    # Map: current first-column content (partial) -> replacement paper name
    author_to_paper = {
        "Wang et al.": "A Comparative Study of VLMs for Food Ingredient Recognition and Nutrient Estimation",
        "FoodDecom Framework": "Decomposing Food Images for Better Nutrition Analysis: A Nutritionist-Inspired Two-Step Framework",
        "Arora, Arun, Jawahar": "What is there in an Indian Thali? Indian Thali Dataset (ITD) and Weight Estimation Dataset (WED)",
        "NutriVisRAG": "NutriVisRAG: Multimodal Exemplar Grounding for Nutritional Analysis Using Vector Databases",
        "OmniFood8K": "OmniFood8K: Single-Image Nutrition Estimation via Hierarchical Frequency-Aligned Fusion",
        "Teng, Min, Liu": "Multimodal Information Fusion for Food Nutrition Estimation: A Survey on Estimation Bottlenecks",
    }
    
    # Find the table (a:tbl)
    tables = doc.getElementsByTagNameNS(NS_A, "tbl")
    if not tables:
        print("No table found in slide5!")
        return
    tbl = tables[0]
    rows = tbl.getElementsByTagNameNS(NS_A, "tr")
    
    # First row is header - change "Paper / Authors" to "Paper"
    if rows:
        header_row = rows[0]
        tcs = header_row.getElementsByTagNameNS(NS_A, "tc")
        if tcs:
            first_tc = tcs[0]
            # Find text run and change it
            for r in first_tc.getElementsByTagNameNS(NS_A, "r"):
                for t in r.getElementsByTagNameNS(NS_A, "t"):
                    if t.firstChild and "Paper" in (t.firstChild.nodeValue or ""):
                        t.firstChild.nodeValue = "Paper"
    
    # Data rows (rows 1+): replace first column text with paper name
    for row in list(rows)[1:]:
        tcs = row.getElementsByTagNameNS(NS_A, "tc")
        if not tcs:
            continue
        first_tc = tcs[0]
        cell_text = get_text_of_node(first_tc)
        
        replacement = None
        for key, paper in author_to_paper.items():
            if key in cell_text:
                replacement = paper
                break
        
        if replacement:
            # Clear existing runs and set new text
            # Find all <a:p> paragraphs in this tc
            paras = first_tc.getElementsByTagNameNS(NS_A, "p")
            for para in list(paras):
                # Remove existing runs
                runs = list(para.getElementsByTagNameNS(NS_A, "r"))
                for r in runs:
                    para.removeChild(r)
                # Create new run with replacement text
                doc2 = para.ownerDocument
                new_r = doc2.createElementNS(NS_A, "a:r")
                new_rPr = doc2.createElementNS(NS_A, "a:rPr")
                new_rPr.setAttribute("lang", "en-US")
                new_rPr.setAttribute("sz", "920")
                new_rPr.setAttribute("b", "1")
                new_rPr.setAttribute("dirty", "0")
                # Dark color
                fill = doc2.createElementNS(NS_A, "a:solidFill")
                clr = doc2.createElementNS(NS_A, "a:srgbClr")
                clr.setAttribute("val", "14284B")
                fill.appendChild(clr)
                new_rPr.appendChild(fill)
                lat = doc2.createElementNS(NS_A, "a:latin")
                lat.setAttribute("typeface", "Times New Roman")
                lat.setAttribute("pitchFamily", "18")
                lat.setAttribute("charset", "0")
                new_rPr.appendChild(lat)
                new_r.appendChild(new_rPr)
                new_t = doc2.createElementNS(NS_A, "a:t")
                new_t.appendChild(doc2.createTextNode(replacement))
                new_r.appendChild(new_t)
                para.appendChild(new_r)
                break  # only first paragraph
    
    # Apply font to entire slide
    apply_font_to_slide(doc)
    write_xml(doc, path)
    print("Slide 5 modified.")


# ============================
# 2. Remove Slide 6 (Gap Analysis)
# ============================
def remove_slide6():
    """Remove slide6 from presentation.xml's sldIdLst and from slide list."""
    # Find slide6's relationship ID
    pres_doc = read_xml(PRES_XML)
    
    # Read slide rels to find the rId for slide6
    rels_path = os.path.join(UNPACKED, "ppt/_rels/presentation.xml.rels")
    rels_doc = read_xml(rels_path)
    
    # Find the rId pointing to slides/slide6.xml
    target_rid = None
    for rel in rels_doc.getElementsByTagName("Relationship"):
        target = rel.getAttribute("Target")
        if "slides/slide6.xml" in target or target == "slides/slide6.xml":
            target_rid = rel.getAttribute("Id")
            break
    
    if not target_rid:
        print("Could not find rId for slide6, trying different approach...")
        # Try to find it differently
        for rel in rels_doc.documentElement.childNodes:
            try:
                target = rel.getAttribute("Target")
                if "slide6" in target:
                    target_rid = rel.getAttribute("Id")
                    break
            except:
                pass
    
    print(f"slide6 rId: {target_rid}")
    
    # Remove the sldId entry from presentation.xml
    sldIdLst = pres_doc.getElementsByTagNameNS(NS_P, "sldIdLst")
    if sldIdLst:
        sldIdLst = sldIdLst[0]
        slide_ids = sldIdLst.getElementsByTagNameNS(NS_P, "sldId")
        to_remove = None
        for sldId in slide_ids:
            r_id = sldId.getAttributeNS(NS_R, "id")
            if r_id == target_rid:
                to_remove = sldId
                break
        if to_remove:
            sldIdLst.removeChild(to_remove)
            print(f"Removed sldId with r:id={target_rid} from presentation.xml")
        else:
            print(f"Could not find sldId with r:id={target_rid}")
    
    write_xml(pres_doc, PRES_XML)
    
    # Also remove relationship from presentation.xml.rels
    for rel in list(rels_doc.documentElement.childNodes):
        try:
            if rel.getAttribute("Id") == target_rid:
                rels_doc.documentElement.removeChild(rel)
                print(f"Removed relationship {target_rid} from rels file")
                break
        except:
            pass
    
    write_xml(rels_doc, rels_path)
    
    # Remove content type for slide6
    ct_path = os.path.join(UNPACKED, "[Content_Types].xml")
    ct_doc = read_xml(ct_path)
    for override in list(ct_doc.getElementsByTagName("Override")):
        pn = override.getAttribute("PartName")
        if "slide6.xml" in pn:
            ct_doc.documentElement.removeChild(override)
            print(f"Removed content type for {pn}")
    write_xml(ct_doc, ct_path)
    
    # Remove slide rels for slide6
    slide6_rels = os.path.join(SLIDES_DIR, "_rels/slide6.xml.rels")
    if os.path.exists(slide6_rels):
        os.remove(slide6_rels)
        print("Removed slide6.xml.rels")
    
    # Remove slide6.xml itself
    slide6_path = os.path.join(SLIDES_DIR, "slide6.xml")
    if os.path.exists(slide6_path):
        os.remove(slide6_path)
        print("Removed slide6.xml")


# ============================
# 3. Modify Slide 11: Problem Statement
# ============================
def modify_slide11():
    """Add more content to the problem statement."""
    # After gap analysis slide is removed, slide11 stays as slide11
    path = os.path.join(SLIDES_DIR, "slide11.xml")
    doc = read_xml(path)
    
    # Find the main problem statement text box and extend the problem statement
    # Look for the text box containing "Problem Statement:"
    sp_list = doc.getElementsByTagNameNS(NS_P, "sp")
    
    additional_text = (
        " The system must further ensure that all outputs carry "
        "calibrated confidence intervals, enabling users to understand the "
        "reliability of each estimate. It must handle occluded, partially "
        "visible, or composite food items (e.g., sambar, mixed rice) using "
        "recipe-fraction fallbacks with explicit uncertainty labelling. "
        "The solution must be deployable on commodity CPU hardware without "
        "internet dependency, ensuring privacy, reproducibility, and accessibility "
        "for resource-constrained settings."
    )
    
    for sp in sp_list:
        paras = sp.getElementsByTagNameNS(NS_A, "p")
        for para in paras:
            full_text = get_text_of_node(para)
            if "To design, implement" in full_text:
                # Find the run containing the main problem statement and append
                runs = list(para.getElementsByTagNameNS(NS_A, "r"))
                if runs:
                    last_run = runs[-1]
                    for t_node in last_run.getElementsByTagNameNS(NS_A, "t"):
                        if t_node.firstChild:
                            t_node.firstChild.nodeValue = (t_node.firstChild.nodeValue or "") + additional_text
                        break
                break
        
    apply_font_to_slide(doc)
    write_xml(doc, path)
    print("Slide 11 modified.")


# ============================
# 4. Modify Slide 13: Methodology - Change to 9-Stage Pipeline
# ============================
def modify_slide13():
    """Remove Critic Agent (Stage 7) and Persistence stages, rename to 9-Stage Pipeline."""
    # After removing slide6, slide13 is still slide13
    path = os.path.join(SLIDES_DIR, "slide13.xml")
    doc = read_xml(path)
    
    # 1. Change slide title: "11-Stage Pipeline" -> "9-Stage Pipeline"
    sp_list = doc.getElementsByTagNameNS(NS_P, "sp")
    for sp in sp_list:
        for t_node in sp.getElementsByTagNameNS(NS_A, "t"):
            if t_node.firstChild and "11-Stage Pipeline" in (t_node.firstChild.nodeValue or ""):
                t_node.firstChild.nodeValue = t_node.firstChild.nodeValue.replace("11-Stage Pipeline", "9-Stage Pipeline")
                print("Title updated to 9-Stage Pipeline")
    
    # 2. Find the table and remove rows for Stage 7 (Critic Agent) and Stage 11 (Persistence/Report)
    # The 11 stages are:
    # 1. Input Intake, 2. Image Preparation, 3. Perception Agent, 4. Food Analysis (RAG),
    # 5. Portion Estimation, 6. Nutrition Calculation, 7. Critic Agent, 8. Confidence Fusion,
    # 9. Active Clarification, 10. Report & Delivery, 11. Persistence & Audit
    # Remove: 7 (Critic Agent) and 11 (Persistence & Audit) -> keep 9 stages
    # Also renumber remaining stages
    
    tables = doc.getElementsByTagNameNS(NS_A, "tbl")
    if not tables:
        print("No table found in slide13!")
        return
    tbl = tables[0]
    rows = list(tbl.getElementsByTagNameNS(NS_A, "tr"))
    
    # Find rows to remove (Critic Agent = stage 7, Persistence = stage 11 or last)
    rows_to_remove = []
    for row in rows[1:]:  # skip header row
        row_text = get_text_of_node(row)
        if "Critic Agent" in row_text or "Persistence" in row_text or "Audit Trail" in row_text:
            rows_to_remove.append(row)
    
    print(f"Removing {len(rows_to_remove)} rows from slide13 table")
    for row in rows_to_remove:
        tbl.removeChild(row)
    
    # Renumber remaining rows (stage numbers)
    # Stages that remain: 1-6, 8-10 (after removing 7 and 11)
    # Need to renumber: 8->7, 9->8, 10->9
    stage_map = {
        "8. Confidence Fusion": "7. Confidence Fusion",
        "9. Active Clarification": "8. Active Clarification", 
        "10. Report": "9. Report & Delivery",
        "11.": "REMOVE",  # extra safety
    }
    
    rows_updated = list(tbl.getElementsByTagNameNS(NS_A, "tr"))
    for row in rows_updated[1:]:
        tcs = list(row.getElementsByTagNameNS(NS_A, "tc"))
        if tcs:
            cell_text = get_text_of_node(tcs[0])
            for old, new in stage_map.items():
                if old.split(".")[0] + "." in cell_text:
                    # Replace stage number
                    for t_node in tcs[0].getElementsByTagNameNS(NS_A, "t"):
                        if t_node.firstChild:
                            original = t_node.firstChild.nodeValue or ""
                            # Replace stage number prefix
                            new_val = re.sub(r'^\d+\.', new.split(".")[0] + ".", original)
                            if new_val != original:
                                t_node.firstChild.nodeValue = new_val
                    break
    
    # Also update the subtitle text
    for sp in sp_list:
        for t_node in sp.getElementsByTagNameNS(NS_A, "t"):
            if t_node.firstChild and "11-stage" in (t_node.firstChild.nodeValue or "").lower():
                t_node.firstChild.nodeValue = t_node.firstChild.nodeValue.replace("11-stage", "9-stage").replace("11-Stage", "9-Stage")
            if t_node.firstChild and "11 stage" in (t_node.firstChild.nodeValue or "").lower():
                t_node.firstChild.nodeValue = t_node.firstChild.nodeValue.replace("11 stage", "9 stage").replace("11 Stage", "9 Stage")
    
    apply_font_to_slide(doc)
    write_xml(doc, path)
    print("Slide 13 modified.")


# ============================
# 5. Apply font to slides 2 (Index) and update slide numbers
# ============================
def modify_slide2_index():
    """Update the Index slide to reflect removed slide (Gap Analysis removed = one less slide)."""
    path = os.path.join(SLIDES_DIR, "slide2.xml")
    doc = read_xml(path)
    
    # The index slide contains a table of contents. We need to:
    # 1. Remove the Literature Survey Gap Analysis entry
    # 2. Update subsequent slide numbers (-1 for each after slide 6)
    
    tables = doc.getElementsByTagNameNS(NS_A, "tbl")
    if tables:
        tbl = tables[0]
        rows = list(tbl.getElementsByTagNameNS(NS_A, "tr"))
        
        gap_analysis_row = None
        for row in rows:
            row_text = get_text_of_node(row)
            if "Gap Analysis" in row_text:
                gap_analysis_row = row
                break
        
        if gap_analysis_row:
            tbl.removeChild(gap_analysis_row)
            print("Removed Gap Analysis row from index table")
        
        # Update slide numbers for entries that come after slide 6
        # e.g., if slide 7 becomes slide 6, slide 8 becomes 7, etc.
        for row in list(tbl.getElementsByTagNameNS(NS_A, "tr")):
            tcs = list(row.getElementsByTagNameNS(NS_A, "tc"))
            if len(tcs) >= 2:
                # First column has the serial number
                sn_text = get_text_of_node(tcs[0]).strip()
                try:
                    sn = int(sn_text)
                    if sn >= 6:  # After gap analysis (was slide 6)
                        for t_node in tcs[0].getElementsByTagNameNS(NS_A, "t"):
                            if t_node.firstChild and t_node.firstChild.nodeValue.strip() == str(sn):
                                t_node.firstChild.nodeValue = str(sn - 1)
                except ValueError:
                    pass
    
    apply_font_to_slide(doc)
    write_xml(doc, path)
    print("Slide 2 (Index) modified.")


# ============================
# 6. Apply font to other slides
# ============================
def apply_font_all_slides():
    """Apply Times New Roman font to all slides."""
    slides = sorted([f for f in os.listdir(SLIDES_DIR) if f.startswith("slide") and f.endswith(".xml")],
                    key=lambda x: int(re.search(r'\d+', x).group()))
    for slide_file in slides:
        path = os.path.join(SLIDES_DIR, slide_file)
        try:
            doc = read_xml(path)
            apply_font_to_slide(doc)
            write_xml(doc, path)
            print(f"Font applied to {slide_file}")
        except Exception as e:
            print(f"Error applying font to {slide_file}: {e}")


# ============================
# 7. Repack the PPTX
# ============================
def repack_pptx():
    if os.path.exists(PPTX_OUT):
        os.remove(PPTX_OUT)
    
    with zipfile.ZipFile(PPTX_OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(UNPACKED):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, UNPACKED).replace("\\", "/")
                zf.write(abs_path, rel_path)
    
    print(f"\nRepacked to: {PPTX_OUT}")


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    print("Step 1: Modifying Slide 5 (Literature Survey)")
    modify_slide5()
    
    print("\nStep 2: Applying font to all slides first")
    apply_font_all_slides()
    
    print("\nStep 3: Removing Slide 6 (Gap Analysis)")
    remove_slide6()
    
    print("\nStep 4: Modifying Slide 11 (Problem Statement)")
    modify_slide11()
    
    print("\nStep 5: Modifying Slide 13 (Methodology 9-Stage)")
    modify_slide13()
    
    print("\nStep 6: Updating Slide 2 (Index)")
    modify_slide2_index()
    
    print("\nStep 7: Repacking PPTX")
    repack_pptx()
    
    print("\nDone!")
