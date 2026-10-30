import sys,json
sys.path.insert(0,'.pdf-review-tools')
import pymupdf
p=pymupdf.open(sys.argv[1])[-1]
words=list({tuple(x[:5]) for x in p.get_text('words')})
labels=[x for x in words if x[4].startswith('HSL_')]
hits=[]
for i,x in enumerate(labels):
 for y in labels[i+1:]:
  if x[4]!=y[4] and (pymupdf.Rect(x[:4])&pymupdf.Rect(y[:4])).get_area()>2:
   hits.append({'a':x[4],'b':y[4],'a_bbox':x[:4],'b_bbox':y[:4]})
print(json.dumps({'different_HSL_label_text_overlaps':len(hits),'hits':hits},indent=2))
