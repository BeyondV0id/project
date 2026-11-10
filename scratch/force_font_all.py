"""
force_font_all.py
Brute-force: set EVERY sz in every slide that is > 1100 to 2400 (24pt),
and set EVERY sz <= 1100 but > 850 to 1100 (keep disclaimers/pg-numbers small).
Sizes <= 850 (true disclaimers) stay as-is.
Also sets typeface to Times New Roman on every rPr / endParaRPr.
Works directly on the unpacked_v3 folder and repacks to v3 (overwrite).
"""
import os, re, zipfile
import defusedxml.minidom

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"

UNPACKED   = "D:/final_year_project/unpacked_v3"
OUT_PPTX   = "D:/final_year_project/project_ppt_batch_11_v3.pptx"
SLIDES_DIR = os.path.join(UNPACKED, "ppt/slides")

BODY_SZ  = "2400"
TITLE_SZ = "3200"
FONT     = "Times New Roman"
DISCLAIMER_MAX = 850   # keep truly tiny sizes (page num disclaimer)

def read_xml(path):
    with open(path, "rb") as f:
        return defusedxml.minidom.parseString(f.read())

def write_xml(doc, path):
    with open(path, "wb") as f:
        f.write(doc.toxml(encoding="utf-8"))

def fix_rpr(rPr, target_sz):
    rPr.setAttribute("sz", target_sz)
    doc = rPr.ownerDocument
    for tag in ("latin", "ea", "cs"):
        for n in list(rPr.getElementsByTagNameNS(NS_A, tag)):
            rPr.removeChild(n)
    lat = doc.createElementNS(NS_A, "a:latin")
    lat.setAttribute("typeface", FONT)
    lat.setAttribute("pitchFamily", "18")
    lat.setAttribute("charset", "0")
    rPr.appendChild(lat)

def process(path):
    doc = read_xml(path)

    # Identify title shape by name="Text 0"
    title_shape_ids = set()
    for sp in doc.getElementsByTagNameNS(NS_P, "sp"):
        for cnv in sp.getElementsByTagNameNS(NS_P, "cNvPr"):
            if cnv.getAttribute("name").lower() == "text 0":
                title_shape_ids.add(id(sp))

    for tag_name in ("rPr", "endParaRPr"):
        for rPr in doc.getElementsByTagNameNS(NS_A, tag_name):
            sz_str = rPr.getAttribute("sz") if rPr.hasAttribute("sz") else "0"
            try:
                sz = int(sz_str)
            except ValueError:
                sz = 0

            if sz <= DISCLAIMER_MAX:
                continue  # leave page number / disclaimer alone

            # Decide target: title shapes get 3200, everything else 2400
            # Walk up to find parent sp
            parent = rPr.parentNode
            is_title = False
            while parent:
                if parent in [doc.getElementsByTagNameNS(NS_P, "sp")[i]
                               for i in range(len(doc.getElementsByTagNameNS(NS_P, "sp")))
                               if id(doc.getElementsByTagNameNS(NS_P, "sp")[i]) in title_shape_ids]:
                    is_title = True
                    break
                parent = parent.parentNode

            target = TITLE_SZ if is_title else BODY_SZ
            fix_rpr(rPr, target)

    write_xml(doc, path)

def repack(src_dir, out_path):
    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                abs_p = os.path.join(root, file)
                rel_p = os.path.relpath(abs_p, src_dir).replace("\\", "/")
                zf.write(abs_p, rel_p)

if __name__ == "__main__":
    slides = sorted(
        [f for f in os.listdir(SLIDES_DIR) if f.startswith("slide") and f.endswith(".xml")],
        key=lambda x: int(re.search(r"\d+", x).group())
    )
    print(f"Force-fixing {len(slides)} slides ...")
    for sf in slides:
        process(os.path.join(SLIDES_DIR, sf))
        print(f"  OK {sf}")
    print("Repacking ...")
    repack(UNPACKED, OUT_PPTX)
    print(f"Written: {OUT_PPTX}")
