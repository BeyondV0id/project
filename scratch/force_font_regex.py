"""
force_font_regex.py
Uses fast regex-based XML string replacement to:
  1. Set sz="2400" on every rPr/endParaRPr that has sz > 850
  2. Keep sz <= 850 as-is (page number, tiny disclaimer)
  3. Replace all latin typeface with Times New Roman
  4. Set title shape (Text 0) rPr to sz="3200"
  5. Repack the zip
Works in-place on unpacked_v3 folder, writes v3 pptx.
"""
import os, re, zipfile

UNPACKED   = "D:/final_year_project/unpacked_v3"
OUT_PPTX   = "D:/final_year_project/project_ppt_batch_11_v3.pptx"
SLIDES_DIR = os.path.join(UNPACKED, "ppt/slides")

BODY_SZ  = "2400"
TITLE_SZ = "3200"
FONT     = "Times New Roman"

# Regex patterns
# Match sz="NNN" in rPr / endParaRPr where NNN > 850
SZ_PATTERN = re.compile(r'((?:a:rPr|a:endParaRPr)[^>]*)sz="(\d+)"')

# Match any latin typeface
LATIN_PATTERN = re.compile(r'(a:latin\s[^>]*typeface=")[^"]*(")')

def replace_sz_and_font(xml_str, in_title_shape=False):
    """Replace sz attrs above 850 with BODY_SZ (or TITLE_SZ), and all latin typefaces."""

    def sz_replacer(m):
        prefix = m.group(1)
        old_sz = int(m.group(2))
        if old_sz <= 850:
            return m.group(0)  # keep tiny sizes
        new_sz = BODY_SZ  # default body
        return f'{prefix}sz="{new_sz}"'

    xml_str = SZ_PATTERN.sub(sz_replacer, xml_str)

    # Replace latin typeface
    xml_str = LATIN_PATTERN.sub(r'\g<1>' + FONT + r'\g<2>', xml_str)

    return xml_str

def process_slide(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the title shape (name="Text 0") and handle separately
    # Strategy: split content around shapes, process each
    # For simplicity, apply BODY_SZ everywhere > 850, then find title and boost to TITLE_SZ
    content = replace_sz_and_font(content)

    # Now boost title shape (Text 0) to TITLE_SZ
    # The title shape has cNvPr ... name="Text 0" ... and contains rPr
    # Pattern: find the first <p:sp> containing name="Text 0" and change its rPr sz
    # We'll use a targeted replacement within that sp block
    title_sp_pattern = re.compile(
        r'(<p:sp>.*?name="Text 0".*?</p:sp>)',
        re.DOTALL
    )
    def boost_title(m):
        sp_xml = m.group(1)
        # In the title sp, replace sz="2400" with sz="3200"
        sp_xml = sp_xml.replace('sz="2400"', f'sz="{TITLE_SZ}"')
        return sp_xml

    content = title_sp_pattern.sub(boost_title, content)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

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
    print(f"Force-fixing {len(slides)} slides with regex ...")
    for sf in slides:
        process_slide(os.path.join(SLIDES_DIR, sf))
        print(f"  OK {sf}")
    print("Repacking ...")
    repack(UNPACKED, OUT_PPTX)
    print(f"Written: {OUT_PPTX}")

    # Quick audit
    import zipfile as zf2
    all_sz = set()
    with zf2.ZipFile(OUT_PPTX) as z:
        for name in z.namelist():
            if name.startswith("ppt/slides/slide") and name.endswith(".xml"):
                data = z.read(name).decode("utf-8", errors="replace")
                for m in re.finditer(r'a:rPr[^>]*sz="(\d+)"', data):
                    all_sz.add(int(m.group(1)))
    print(f"All sizes found (pt): {sorted(s/100 for s in all_sz)}")
