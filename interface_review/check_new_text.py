import sys,json
sys.path.insert(0,'.pdf-review-tools')
import pymupdf
D=pymupdf.open(sys.argv[1]);out={}
for i in [1,3,4,6]:
 p=D[i];w=list({tuple(x[:5])for x in p.get_text('words')});a=w
 if i==1:a=[x for x in w if x[4].startswith(('LCD_','BTN_'))]
 if i in(3,4):a=[x for x in w if x[1]<310];w=a
 hits=[]
 for x in a:
  for y in w:
   if x[4]!=y[4] and(pymupdf.Rect(x[:4])&pymupdf.Rect(y[:4])).get_area()>2:
    pair=sorted([x[4],y[4]])
    if pair not in hits:hits.append(pair)
 out[str(i+1)]=hits
print(json.dumps(out,indent=2))
