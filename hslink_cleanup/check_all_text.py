import sys,json
sys.path.insert(0,'.pdf-review-tools')
import pymupdf
p=pymupdf.open(sys.argv[1])[-1];w=list({tuple(x[:5]) for x in p.get_text('words')});a=[x for x in w if x[4].startswith('HSL_')];hits=[]
for x in a:
 for y in w:
  if x[4]!=y[4] and (pymupdf.Rect(x[:4])&pymupdf.Rect(y[:4])).get_area()>2:
   hits.append({'label':x[4],'other':y[4],'label_xy':x[:2],'other_xy':y[:2]})
print(json.dumps({'count':len(hits),'hits':hits},indent=2))
