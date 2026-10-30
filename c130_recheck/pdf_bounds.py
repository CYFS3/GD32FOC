import sys,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'.pdf-review-tools'))
import pymupdf as fitz
pdf=fitz.open('c130_recheck/updated.pdf')
for i,p in enumerate(pdf):
 hits=p.search_for('C130') or p.search_for('C1130')
 if not hits:continue
 print('PAGE',i,p.rect,'HITS',hits)
 crop=fitz.Rect(325*72/25.4,190*72/25.4,378*72/25.4,233*72/25.4)
 for w in p.get_text('words'):
  if fitz.Rect(w[:4]).intersects(crop):print(w[:5])
 out=fitz.open();out.new_page(width=crop.width*3,height=crop.height*3).show_pdf_page(fitz.Rect(0,0,crop.width*3,crop.height*3),pdf,i,clip=crop);out.save(f'c130_recheck/focus_{i}.pdf')
