#!/usr/bin/env python
import zipfile

with zipfile.ZipFile('D:\\final_year_project\\project_ppt_batch_11_Updated.pptx', 'r') as z:
    # Check slide 2 XML
    content = z.read('ppt/slides/slide2.xml').decode('utf-8')
    if 'Serial No.' in content:
        print("'Serial No.' FOUND in slide2.xml")
    else:
        print("'Serial No.' NOT in slide2.xml")
    if 'Contents' in content:
        print("'Contents' FOUND in slide2.xml")
    else:
        print("'Contents' NOT in slide2.xml")
    
    # Check notes slide 2
    content = z.read('ppt/notesSlides/notesSlide2.xml').decode('utf-8')
    if 'Serial No.' in content:
        print("'Serial No.' FOUND in notesSlide2.xml")
    if 'Contents' in content:
        print("'Contents' FOUND in notesSlide2.xml")
    
    # Check slide 13 XML
    content = z.read('ppt/slides/slide13.xml').decode('utf-8')
    if 'Stage' in content and 'Primary Operation' in content:
        print("Old table FOUND in slide13.xml")
    else:
        print("Old table NOT in slide13.xml")
    
    # Check notes slide 13
    content = z.read('ppt/notesSlides/notesSlide13.xml').decode('utf-8')
    if 'Stage' in content and 'Primary Operation' in content:
        print("Old table FOUND in notesSlide13.xml")
    else:
        print("Old table NOT in notesSlide13.xml")