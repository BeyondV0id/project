#!/usr/bin/env python
import zipfile
import xml.etree.ElementTree as ET

with zipfile.ZipFile('D:\\final_year_project\\project_ppt_batch_11_Updated.pptx', 'r') as z:
    # Check slide 2 XML structure
    content = z.read('ppt/slides/slide2.xml').decode('utf-8')
    root = ET.fromstring(content)
    
    # Find all text elements with their parent context
    ns = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
          'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
    
    for elem in root.iter():
        if elem.tag.endswith('}t'):
            if elem.text and ('Serial No.' in elem.text or 'Contents' in elem.text):
                # Print parent hierarchy
                parent = elem
                path = []
                for _ in range(5):
                    parent = parent.getparent() if hasattr(parent, 'getparent') else None
                    if parent is not None:
                        path.append(parent.tag)
                    else:
                        break
                print(f"Found in: {' > '.join(reversed(path))}")
                print(f"  Text: {elem.text}")
                print()
    
    print("--- SLIDE 13 ---")
    content = z.read('ppt/slides/slide13.xml').decode('utf-8')
    root = ET.fromstring(content)
    
    for elem in root.iter():
        if elem.tag.endswith('}t'):
            if elem.text and ('Stage' in elem.text and 'Primary Operation' in elem.text):
                parent = elem
                path = []
                for _ in range(5):
                    parent = parent.getparent() if hasattr(parent, 'getparent') else None
                    if parent is not None:
                        path.append(parent.tag)
                    else:
                        break
                print(f"Found in: {' > '.join(reversed(path))}")
                print(f"  Text: {elem.text[:100]}")
                print()