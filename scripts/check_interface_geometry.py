from migrate_p2 import *
import sys,math
sys.path.insert(0,str(W/'.pdf-review-tools'));import fitz
pdf=fitz.open(W/(sys.argv[1] if len(sys.argv)>1 else 'interface_review/final.pdf'));report={}
for idx,fn in [(1,'MCU.kicad_sch'),(6,'Interface.kicad_sch')]:
 s,r=load(W/fn);defs={d.items[1]:d for d in r.one('lib_symbols').kids('symbol')};words=list({tuple(w[:5]) for w in pdf[idx].get_text('words')});targets=[]
 for w in words:
  if idx==6 or w[4].startswith(('LCD_','BTN_','OLED_')) or (w[0]>800 and 590<w[1]<645):targets.append(w)
 bodies=[]
 for n in r.kids('symbol'):
  d=defs[n.val('lib_id')];x,y,a=map(float,n.one('at').items[1:]);a=math.radians(a);pts=[]
  for sub in d.kids('symbol'):
   for g in sub.items:
    if not isinstance(g,Node) or g.key not in ['rectangle','polyline','circle']:continue
    q=[]
    if g.key=='rectangle':q=[g.one('start'),g.one('end')]
    if g.key=='polyline':q=g.one('pts').kids('xy')
    for p in q:
     px,py=map(float,p.items[1:3]);pts.append(((x+px*math.cos(a)-py*math.sin(a))*72/25.4,(y-px*math.sin(a)-py*math.cos(a))*72/25.4))
  if pts:bodies.append((prop(n,'Reference'),fitz.Rect(min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts))))
 hits=[]
 for w in targets:
  for ref,b in bodies:
   q=fitz.Rect(w[:4])&b
   if q.width>.5 and q.height>.5:hits.append([w[4],ref,list(q)])
 # all text pair checks for new MCU note, deduplicated and whitespace ignored
 text=[]
 for w in targets:
  for v in words:
   if w!=v and (fitz.Rect(w[:4])&fitz.Rect(v[:4])).get_area()>2:text.append([w[4],v[4]])
 report[str(idx+1)]={'symbol_body_intersections':hits,'target_text_intersections':text}
(W/'interface_review/interface_geometry_check.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
