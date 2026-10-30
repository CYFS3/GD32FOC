import sys
sys.path.insert(0,'.pdf-review-tools')
import pymupdf
p=pymupdf.open('hslink_cleanup/after.pdf')[-1];w=list({tuple(x[:5]) for x in p.get_text('words')})
for a in w:
 if not a[4].startswith('HSL_'):continue
 for b in w:
  if b[4]==a[4]:continue
  if (pymupdf.Rect(a[:4])&pymupdf.Rect(b[:4])).get_area()>2: print(a[4],b[4],tuple(round(v*25.4/72,2) for v in a[:4]))
